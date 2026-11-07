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
import re
import platform
import shutil
import subprocess

from typing import List, Optional

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from tests.framework.base_test import HvBaseTest, ARM_MACHINES


class TestPdControlBase(HvBaseTest):

    def compile_and_run(
        self,
        source_files: List[str],
        out_dir: str,
        num_iterations: int,
        flag: Optional[str] = None
    ) -> List[str]:
        exe_path = self._compile_and_run(source_files, out_dir, flag)

        # run executable (returns stdout)
        output = subprocess.check_output([
            exe_path,
            str(num_iterations)]
        ).splitlines()

        return [x.decode('utf-8') for x in output]

    # samples per vector for each SIMD flag; the sample rate is set in tests/src/test_control.c
    SIMD_WIDTH = {"HV_SIMD_NONE": 1, "HV_SIMD_SSE": 4, "HV_SIMD_SSE_FMA": 4, "HV_SIMD_AVX": 8, "HV_SIMD_NEON": 4}
    SAMPLE_RATE = 48000.0

    def align_vector_timestamps(self, result: List[str], golden: List[str], flag: str) -> List[str]:
        """Messages from signal objects (e.g. snapshot~) are timed at vector boundaries, so with
        SIMD they can arrive up to one vector later than in the golden file (HV_SIMD_NONE).
        Returns the result with such timestamps replaced by the golden ones; any other
        difference is left for assertEqual to report.
        """
        tolerance = 1000.0 * self.SIMD_WIDTH[flag] / self.SAMPLE_RATE + 0.001  # + rounding of %.3f
        stamp = re.compile(r"^\[@ ([0-9.]+)\] ")
        aligned = []
        for r, g in zip(result, golden):
            mr, mg = stamp.match(r), stamp.match(g)
            if mr and mg and r[mr.end():] == g[mg.end():] \
                    and 0.0 <= float(mr.group(1)) - float(mg.group(1)) < tolerance:
                r = g
            aligned.append(r)
        return aligned + result[len(golden):]

    def create_fail_message(
        self,
        result: str,
        golden: str,
        flag: Optional[str] = None
    ) -> str:
        return "\nResult ({0})\n-----------\n{1}\n\nGolden\n-----------\n{2}".format(
            flag or "",
            "\n".join(result),
            "\n".join(golden))

    def _test_control_patch_expect_error(
        self,
        pd_file: str,
        expected_enum: NotificationEnum
    ) -> None:
        pd_path = os.path.join(self.TEST_DIR, pd_file)

        try:
            self._run_hvcc(pd_path, expect_fail=True, expected_enum=expected_enum)
        except Exception as e:
            self.fail(str(e))

    def _test_control_patch_expect_warning(
        self,
        pd_file: str,
        expected_enum: NotificationEnum
    ) -> None:
        # setup
        pd_path = os.path.join(self.TEST_DIR, pd_file)

        try:
            self._run_hvcc(pd_path, expect_warning=True, expected_enum=expected_enum)
        except Exception as e:
            self.fail(str(e))

    def _test_control_patch(
        self,
        pd_file: str,
        num_iterations: int = 1,
        allow_warnings: bool = True,
        fail_message: Optional[str] = None
    ) -> None:
        """Compiles, runs, and tests a control patch.
        Allows warnings by default, always fails on errors.
        @param fail_message  An optional message displayed in case of test failure.
        """

        # setup
        pd_path = os.path.join(self.TEST_DIR, pd_file)
        patch_name = os.path.splitext(os.path.basename(pd_path))[0]

        try:
            out_dir = self._run_hvcc(pd_path)
        except Exception as e:
            self.fail(str(e))

        # copy over additional C assets
        c_src_dir = os.path.join(out_dir, "c")
        shutil.copy2(os.path.join(self.SCRIPT_DIR, "src/test_control.c"), c_src_dir)

        # prepare the clang command
        c_sources = os.listdir(c_src_dir)

        # don't delete the output dir
        # if the test fails, we can examine the output

        golden_path = os.path.join(os.path.dirname(pd_path), f"{patch_name.split('.')[0]}.golden.txt")
        if os.path.exists(golden_path):
            with open(golden_path, "r") as f:
                golden = "".join(f.readlines()).splitlines()

                # NO SIMD (always test this case)
                result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_NONE")
                message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_NONE")
                self.assertEqual(result, golden, message)

                if platform.machine().startswith("x86"):
                    # SSE
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_SSE")
                    result = self.align_vector_timestamps(result, golden, "HV_SIMD_SSE")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_SSE")
                    self.assertEqual(result, golden, message)

                    # SSE with FMA
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_SSE_FMA")
                    result = self.align_vector_timestamps(result, golden, "HV_SIMD_SSE_FMA")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_SSE_FMA")
                    self.assertEqual(result, golden, message)

                    # AVX (with FMA)
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_AVX")
                    result = self.align_vector_timestamps(result, golden, "HV_SIMD_AVX")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_AVX")
                    self.assertEqual(result, golden, message)

                elif platform.machine().startswith(ARM_MACHINES):
                    # NEON
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_NEON")
                    result = self.align_vector_timestamps(result, golden, "HV_SIMD_NEON")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_NEON")
                    self.assertEqual(result, golden, message)

        else:
            self.fail(f"{os.path.basename(golden_path)} could not be found.")
