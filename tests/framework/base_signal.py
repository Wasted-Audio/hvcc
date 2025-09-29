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
import platform
import shutil
import subprocess
import numpy

from typing import List, Optional

from scipy.io import wavfile

from tests.framework.base_test import HvBaseTest


class TestPdSignalBase(HvBaseTest):

    def compile_and_run(
        self,
        source_files: List[str],
        out_dir: str,
        sample_rate: Optional[int] = None,
        block_size: Optional[int] = None,
        num_iterations: Optional[int] = None,
        flag: Optional[str] = None
    ):
        exe_path = self._compile_and_run(source_files, out_dir, flag)

        # run executable
        # e.g. $ /path/heavy /path/heavy.wav 48000 480 1000
        wav_path = os.path.join(out_dir, f"heavy.{flag}.wav")
        subprocess.check_output([
            exe_path,
            wav_path,
            str(sample_rate or 48000),
            str(block_size or 480),
            str(num_iterations or 100)])

        return wav_path

    def _compare_wave_output(
        self,
        out_dir: str,
        c_sources: List[str],
        golden_path: str,
        flag: Optional[str] = None
    ):
        # http://stackoverflow.com/questions/10580676/comparing-two-numpy-arrays-for-equality-element-wise
        # http://docs.scipy.org/doc/numpy/reference/routines.testing.html

        self.compile_and_run(c_sources, out_dir, flag=flag)

        [r_fs, result] = wavfile.read(os.path.join(out_dir, f"heavy.{flag}.wav"))
        [g_fs, golden] = wavfile.read(golden_path)
        self.assertEqual(g_fs, r_fs, f"Expected WAV sample rate of {g_fs}Hz, got {r_fs}Hz.")
        try:
            numpy.testing.assert_array_almost_equal(
                result,
                golden,
                decimal=4,
                verbose=True,
                err_msg=f"Generated WAV does not match the golden file with {flag}.")
        except AssertionError as e:
            self.fail(e)

    def _test_signal_patch(self, pd_file: str):
        """Compiles, runs, and tests a signal patch.
        """

        pd_path = os.path.join(self.TEST_DIR, pd_file)

        # setup
        patch_name = os.path.splitext(os.path.basename(pd_path))[0]
        golden_path = os.path.join(self.TEST_DIR, f"{patch_name}.golden.wav")
        self.assertTrue(os.path.exists(golden_path), f"File not found: {golden_path}")

        try:
            out_dir = self._run_hvcc(pd_path)
        except Exception as e:
            self.fail(str(e))

        # copy over additional C assets
        c_src_dir = os.path.join(out_dir, "c")
        shutil.copy2(os.path.join(self.SCRIPT_DIR, "src/test_signal.c"), c_src_dir)
        shutil.copy2(os.path.join(self.SCRIPT_DIR, "src/tinywav/tinywav.h"), c_src_dir)
        shutil.copy2(os.path.join(self.SCRIPT_DIR, "src/tinywav/tinywav.c"), c_src_dir)

        # prepare the clang command
        source_files = os.listdir(c_src_dir)

        # always test HV_SIMD_NONE
        self._compare_wave_output(out_dir, source_files, golden_path, "HV_SIMD_NONE")

        if platform.machine().startswith("x86"):
            self._compare_wave_output(out_dir, source_files, golden_path, "HV_SIMD_SSE")
            self._compare_wave_output(out_dir, source_files, golden_path, "HV_SIMD_SSE_FMA")
            self._compare_wave_output(out_dir, source_files, golden_path, "HV_SIMD_AVX")

        elif platform.machine().startswith("arm"):
            self._compare_wave_output(out_dir, source_files, golden_path, "HV_SIMD_NEON")

        # don't delete the output dir
        # if the test fails, we can examine the output
