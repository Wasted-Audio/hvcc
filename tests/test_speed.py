# Copyright (C) 2014-2018 Enzien Audio, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import shutil
import subprocess
import sys
import time
import unittest

sys.path.append("../")
import hvcc

SCRIPT_DIR = os.path.dirname(__file__)

class TestPdPatches(unittest.TestCase):

    # test results cannot be more than 2% slower than the golden value
    __PERCENT_THRESHOLD = 2.0

    def _compile_and_run_patch(self, pd_path, out_dir, samplerate=None, blocksize=None, num_iterations=None, flag=None):
        hvcc_results = hvcc.compile_dataflow(pd_path, out_dir, verbose=False)

        # determine correct compiler flags
        flag = flag or "HV_SIMD_NONE"

        simd_flags = {
          "HV_SIMD_NONE" : ["-DHV_SIMD_NONE"],
          "HV_SIMD_SSE" : ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2"],
          "HV_SIMD_AVX" : ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2", "-mavx", "-mfma"],
          "HV_SIMD_NEON" : ["-mcpu=cortex-a7", "-mfloat-abi=hard"]
        }

        self.assertTrue(flag in simd_flags, "Unknown compiler flag: " + flag)
        c_flags = simd_flags[flag]

        # all warnings are errors (except for #warning)
        # assertions are NOT turned off (help to catch errors)
        c_flags += [
            "-std=c11",
            "-O3", "-ffast-math", "-DNDEBUG",
            "-Werror", "-Wno-#warnings", "-Wno-unused-function",
            "-lm"]

        exe_path = os.path.join(out_dir, "heavy")
        c_src_dir = os.path.join(out_dir, "c")

        # copy additional source
        shutil.copy2(os.path.join(SCRIPT_DIR, "test_speed.c"), c_src_dir)

        c_sources = [os.path.join(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith(".c")]

        # run the compile command
        cmd = ["clang"] + c_flags + c_sources + ["-o", exe_path]
        subprocess.check_output(cmd)

        # run executable
        result = subprocess.check_output([
            exe_path,
            str(samplerate),
            str(blocksize),
            str(num_iterations)])
        return float(result)

    def test_00_fire(self):
        self._compile_and_test_path("test-00-fire.pd")

    def test_01_fire(self):
        self._compile_and_test_path("test-01-fire.pd")

    def _compile_and_test_path(self, pd_name):
        pd_path = os.path.join(os.path.dirname(__file__), "pd", "speed", pd_name)
        out_dir = os.path.join(os.path.dirname(__file__), "build")

        json_path = os.path.join(
            os.path.dirname(pd_path),
            os.path.basename(pd_path)[:-3]+".golden.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                golden = json.load(f)
        else:
            golden = {}

        tick = self._compile_and_run_patch(pd_path, out_dir,
            golden.get("samplerate", 48000.0),
            golden.get("blocksize", 512),
            golden.get("numIterations", 2000000),
            flag="HV_SIMD_SSE")

        if "HV_SIMD_SSE" in golden.get("usPerBlock",{}):
            tock = golden["usPerBlock"]["HV_SIMD_SSE"]
            percent_difference = 100.0*(tick - tock)/tock
            self.assertTrue(
                percent_difference < TestPdPatches.__PERCENT_THRESHOLD,
                "{0} has become {1:g}% slower @ {2}us/block.".format(os.path.basename(pd_path), percent_difference, tick))
            if (percent_difference < -TestPdPatches.__PERCENT_THRESHOLD):
                print(("{0} has become significantly faster: {1:g}%".format(
                    os.path.basename(pd_path),
                    percent_difference)))
        else:
            print(tick)
