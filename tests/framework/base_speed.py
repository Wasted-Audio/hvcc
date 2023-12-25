# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2022 Wasted Audio
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

import os
import json
import shutil
import subprocess

from tests.framework.base_test import HvBaseTest


class TestPdSpeedBase(HvBaseTest):

    def compile_and_run(
        self,
        source_files,
        out_dir,
        sample_rate=None,
        block_size=None,
        num_iterations=None,
        flag=None
    ):
        exe_path = self._compile_and_run_clang(source_files, out_dir, flag)

        # run executable
        result = subprocess.check_output([
            exe_path,
            str(sample_rate),
            str(block_size),
            str(num_iterations)])

        return float(result)

    def _test_speed_patch(self, pd_file):
        pd_path = os.path.join(self.TEST_DIR, pd_file)
        # out_dir = os.path.join(os.path.dirname(__file__), "build")

        json_path = os.path.join(os.path.dirname(pd_path), f"{os.path.basename(pd_path)[:-3]}.golden.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                golden = json.load(f)
        else:
            golden = {}

        try:
            out_dir = self._run_hvcc(pd_path)
        except Exception as e:
            self.fail(str(e))

        c_src_dir = os.path.join(out_dir, "c")

        # copy additional source
        shutil.copy2(os.path.join(self.SCRIPT_DIR, "src/test_speed.c"), c_src_dir)

        c_sources = [os.path.join(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith(".c")]

        tick = self.compile_and_run(c_sources, out_dir,
                                    golden.get("samplerate", 48000.0),
                                    golden.get("blocksize", 512),
                                    golden.get("numIterations", 2000000),
                                    flag="HV_SIMD_SSE")

        if "HV_SIMD_SSE" in golden.get("usPerBlock", {}):
            tock = golden["usPerBlock"]["HV_SIMD_SSE"]
            percent_difference = 100.0 * (tick - tock) / tock
            self.assertTrue(percent_difference < self.__PERCENT_THRESHOLD,
                            f"{os.path.basename(pd_path)} has become {percent_difference:g}% slower @ {tick}us/block.")
            if (percent_difference < -self.__PERCENT_THRESHOLD):
                print(f"{os.path.basename(pd_path)} has become significantly faster: {percent_difference:g}%")
        else:
            print(tick)
