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

import jinja2
import os
import shutil
import subprocess
import unittest

from typing import Optional

import hvcc

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum


simd_flags = {
    "HV_SIMD_NONE": ["-DHV_SIMD_NONE"],
    "HV_SIMD_SSE": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2"],
    "HV_SIMD_SSE_FMA": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2", "-mfma"],
    "HV_SIMD_AVX": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2", "-mavx", "-mfma"],
    "HV_SIMD_NEON": ["-mcpu=cortex-a7", "-mfloat-abi=hard"]
}


class HvBaseTest(unittest.TestCase):
    SCRIPT_DIR = ''
    TEST_DIR = ''

    def setUp(self):
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader(os.path.join(
            os.path.dirname(__file__),
            "template"))

    def _run_hvcc(
        self,
        pd_path,
        expect_warning: bool = False,
        expect_fail: bool = False,
        expected_enum: NotificationEnum = NotificationEnum.WARNING_GENERIC
    ) -> Optional[str]:
        """Run hvcc on a Pd file. Returns the output directory.
        """

        # clean default output directories
        out_dir = os.path.join(self.SCRIPT_DIR, "build")
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        hvcc_results = hvcc.compile_dataflow(pd_path, out_dir, verbose=False)

        for r in hvcc_results.values():
            if not expect_fail:
                # if there are any errors from hvcc, fail immediately
                # TODO(mhroth): standardise how errors and warnings are returned between stages
                if r.notifs.has_error:
                    if r.stage == "pd2hv":
                        self.fail(hvcc_results["pd2hv"].notifs.errors[0])
                    else:
                        self.fail(str(r.notifs))

            if expect_warning:
                for r in hvcc_results.values():
                    if r.stage == "pd2hv":
                        self.assertTrue(
                            expected_enum in [w.enum for w in hvcc_results["pd2hv"].notifs.warnings]
                        )
                        return

                self.fail(f"Expected warning enum: {expected_enum}")

            if expect_fail and r.notifs.has_error:
                if r.stage == "pd2hv":
                    self.assertTrue(expected_enum in [e.enum for e in hvcc_results["pd2hv"].notifs.errors])
                    return
                elif r.stage == "hvcc":
                    if len(hvcc_results["hvcc"].notifs.errors) > 0:
                        return  # hvcc isn't using Notification enums so just pass

                self.fail(f"Expected error enum: {expected_enum}")

        return out_dir

    def _compile_and_run(
        self,
        source_files,
        out_dir,
        flag=None
    ):
        exe_path = os.path.join(out_dir, "heavy")

        # template Makefile
        # NOTE(mhroth): assertions are NOT turned off (help to catch errors)
        makefile_path = os.path.join(out_dir, "c", "Makefile")
        with open(makefile_path, "w") as f:
            f.write(self.env.get_template("Makefile").render(
                simd_flags=simd_flags[flag or "HV_SIMD_NONE"],
                source_files=source_files,
                out_path=exe_path))

        # run the compile command
        subprocess.check_output(["make", "-C", os.path.dirname(makefile_path), "-j"])

        return exe_path

    def _compile_and_run_clang(
        self,
        source_files,
        out_dir,
        flag=None,
    ):
        flag = flag or "HV_SIMD_NONE"
        self.assertTrue(flag in simd_flags, f"Unknown compiler flag: {flag}")

        c_flags = simd_flags[flag]

        # all warnings are errors (except for #warning)
        # assertions are NOT turned off (help to catch errors)
        c_flags += [
            "-std=c11",
            "-O3", "-ffast-math", "-DNDEBUG",
            "-Werror", "-Wno-#warnings", "-Wno-unused-function",
            "-lm"]

        exe_path = os.path.join(out_dir, "heavy")

        # run the compile command
        cmd = ["clang"] + c_flags + source_files + ["-o", exe_path]  # + ['-v']
        subprocess.check_output(cmd)

        return exe_path
