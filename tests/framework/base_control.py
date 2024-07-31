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

from tests.framework.base_test import HvBaseTest


class TestPdControlBase(HvBaseTest):

    def compile_and_run(
        self,
        source_files,
        out_dir,
        num_iterations,
        flag=None
    ):
        exe_path = self._compile_and_run(source_files, out_dir, flag)

        # run executable (returns stdout)
        output = subprocess.check_output([
            exe_path,
            str(num_iterations)]
        ).splitlines()

        return [x.decode('utf-8') for x in output]

    def create_fail_message(self, result, golden, flag=None):
        return "\nResult ({0})\n-----------\n{1}\n\nGolden\n-----------\n{2}".format(
            flag or "",
            "\n".join(result),
            "\n".join(golden))

    def _test_control_patch_expect_error(self, pd_file, expected_enum):
        pd_path = os.path.join(self.TEST_DIR, pd_file)

        try:
            self._run_hvcc(pd_path, expect_fail=True, expected_enum=expected_enum)
        except Exception as e:
            self.fail(str(e))

    def _test_control_patch_expect_warning(self, pd_file, expected_enum):
        # setup
        pd_path = os.path.join(self.TEST_DIR, pd_file)

        try:
            self._run_hvcc(pd_path, expect_warning=True, expected_enum=expected_enum)
        except Exception as e:
            self.fail(str(e))

    def _test_control_patch(self, pd_file, num_iterations=1, allow_warnings=True, fail_message=None):
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
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_SSE")
                    self.assertEqual(result, golden, message)

                    # SSE with FMA
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_SSE_FMA")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_SSE_FMA")
                    self.assertEqual(result, golden, message)

                    # AVX (with FMA)
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_AVX")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_AVX")
                    self.assertEqual(result, golden, message)

                elif platform.machine().startswith("arm"):
                    # NEON
                    result = self.compile_and_run(c_sources, out_dir, num_iterations, "HV_SIMD_NEON")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_NEON")
                    self.assertEqual(result, golden, message)

        else:
            self.fail(f"{os.path.basename(golden_path)} could not be found.")
