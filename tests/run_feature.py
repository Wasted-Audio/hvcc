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

import argparse
import jinja2
import os
import platform
import shutil
import subprocess
import sys
# import unittest

sys.path.append("../")
import hvcc
# from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum

SCRIPT_DIR = os.path.dirname(__file__)
CONTROL_TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "control")


class PatchRunner:

    def __init__(self):
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader(os.path.join(
            os.path.dirname(__file__),
            "template"))

    def compile_and_run(self, source_files, out_path, num_iterations, flag=None):

        simd_flags = {
            "HV_SIMD_NONE": ["-DHV_SIMD_NONE"],
            "HV_SIMD_SSE": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1"],
            "HV_SIMD_SSE_FMA": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-mfma"],
            "HV_SIMD_AVX": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-mavx", "-mfma"],
            "HV_SIMD_NEON": ["-mcpu=cortex-a7", "-mfloat-abi=hard"]
        }

        # template Makefile
        # NOTE(mhroth): assertions are NOT turned off (help to catch errors)
        makefile_path = os.path.join(os.path.dirname(out_path), "c", "Makefile")
        with open(makefile_path, "w") as f:
            f.write(self.env.get_template("Makefile").render(
                simd_flags=simd_flags[flag or "HV_SIMD_NONE"],
                source_files=source_files,
                out_path=out_path))

        # run the compile command
        subprocess.check_output(["make", "-C", os.path.dirname(makefile_path), "-j"])

        # run executable (returns stdout)
        output = subprocess.check_output([out_path, str(num_iterations)]).splitlines()
        return [x.decode('utf-8') for x in output]

    def create_fail_message(self, result, golden, flag=None):
        return "\nResult ({0})\n-----------\n{1}\n\nGolden\n-----------\n{2}".format(
            flag or "",
            "\n".join(result),
            "\n".join(golden))

    # def _test_control_patch_expect_error(self, pd_file, expected_enum):
    #     pd_path = os.path.join(CONTROL_TEST_DIR, pd_file)

    #     # clean any existing output directories
    #     out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "./build"))
    #     if os.path.exists(out_dir):
    #         shutil.rmtree(out_dir)

    #     hvcc_results = hvcc.compile_dataflow(pd_path, out_dir, verbose=False)
    #     for r in hvcc_results.values():
    #         if r["notifs"].get("has_error", False):
    #             if r["stage"] == "pd2hv":
    #                 self.assertTrue(expected_enum in [e["enum"] for e in hvcc_results["pd2hv"]["notifs"]["errors"]])
    #                 return
    #             elif r["stage"] == "hvcc":
    #                 if len(hvcc_results["hvcc"]["notifs"]["errors"]) > 0:
    #                     return  # hvcc isn't using Notification enums so just pass

    #     self.fail("Expected error enum: " + str(expected_enum))

    # def _test_control_patch_expect_warning(self, pd_file, expected_enum):
    #     pd_path = os.path.join(CONTROL_TEST_DIR, pd_file)

    #     # clean any existing output directories
    #     out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "./build"))
    #     if os.path.exists(out_dir):
    #         shutil.rmtree(out_dir)

    #     hvcc_results = hvcc.compile_dataflow(pd_path, out_dir, verbose=False)
    #     for r in hvcc_results.values():
    #         if r["stage"] == "pd2hv":
    #             self.assertTrue(expected_enum in [w["enum"] for w in hvcc_results["pd2hv"]["notifs"]["warnings"]])
    #             return

    #     self.fail("Expected warning enum: " + str(expected_enum))

    def _test_control_patch(self, pd_file, num_iterations=1, allow_warnings=True, fail_message=None):

        """Compiles, runs, and tests a control patch.
        Allows warnings by default, always fails on errors.
        @param fail_message  An optional message displayed in case of test failure.
        """

        pd_path = os.path.join(CONTROL_TEST_DIR, pd_file)

        # setup
        patch_name = os.path.splitext(os.path.basename(pd_path))[0]

        # clean any existing output directories
        out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "./build"))
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        # compile the pd patch
        hvcc_results = hvcc.compile_dataflow(pd_path, out_dir, verbose=False)
        for r in hvcc_results.values():
            # if there are any errors from hvcc, fail immediately
            # TODO(mhroth): standardise how errors and warnings are returned
            # between stages
            if r["notifs"].get("has_error", False):
                if r["stage"] == "pd2hv":
                    self.fail(hvcc_results["pd2hv"]["notifs"]["errors"][0])
                else:
                    self.fail(str(r["notifs"]))

            if not allow_warnings:
                if len(hvcc_results["pd2hv"]["notifs"]["warnings"]) > 0:
                    self.fail(hvcc_results["pd2hv"]["notifs"]["warnings"][0]["message"])

        # copy over additional C assets
        c_src_dir = os.path.join(out_dir, "c")
        print("copying main c file: ", os.path.join(SCRIPT_DIR, "test_control.c"), c_src_dir)
        shutil.copy2(os.path.join(SCRIPT_DIR, "test_control.c"), c_src_dir)

        # prepare the clang command
        exe_file = os.path.join(out_dir, "run_feature")
        # c_sources = [os.path.join(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith((".c", ".cpp"))]
        c_sources = [c for c in os.listdir(c_src_dir)]

        # don't delete the output dir
        # if the test fails, we can examine the output

        golden_path = os.path.join(os.path.dirname(pd_path), f"{patch_name.split('.')[0]}.golden.txt")
        if os.path.exists(golden_path):
            with open(golden_path, "r") as f:
                golden = "".join(f.readlines()).splitlines()

                # NO SIMD (always test this case)
                result = self.compile_and_run(c_sources, exe_file, num_iterations, "HV_SIMD_NONE")
                message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_NONE")
                self.assertEqual(result, golden, message)

                if platform.machine().startswith("x86"):
                    print("DGB: running x86 optimization tests")
                    # SSE
                    result = self.compile_and_run(c_sources, exe_file, num_iterations, "HV_SIMD_SSE")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_SSE")
                    self.assertEqual(result, golden, message)

                    # SSE with FMA
                    result = self.compile_and_run(c_sources, exe_file, num_iterations, "HV_SIMD_SSE_FMA")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_SSE_FMA")
                    self.assertEqual(result, golden, message)

                    # AVX (with FMA)
                    result = self.compile_and_run(c_sources, exe_file, num_iterations, "HV_SIMD_AVX")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_AVX")
                    self.assertEqual(result, golden, message)

                elif platform.machine().startswith("arm"):
                    # NEON
                    result = self.compile_and_run(c_sources, exe_file, num_iterations, "HV_SIMD_NEON")
                    message = fail_message or self.create_fail_message(result, golden, "HV_SIMD_NEON")
                    self.assertEqual(result, golden, message)

        else:
            self.fail(f"{os.path.basename(golden_path)} could not be found.")

    def assertEqual(self, test, expected, message=None):
        assert test == expected, message

    def test_exp(self):
        print("DGB: looking for something---------------------------")
        self._test_control_patch("test-exp.pd")


def main():
    print("DGB: in test_feature.py")
    # TODO(mhroth): make this work
    parser = argparse.ArgumentParser(
        description="Compile a specific pd patch.")
    parser.add_argument(
        "pd_path",
        help="The path to the Pd file to read.")
    args = parser.parse_args()
    print("Args", args)
    # the argument should be a file that exists in tests/pd
    # the test below should be updated to test for that
    # for now just pass it through and let the underlying system
    # complain about it.
    # if os.path.exists(args.pd_path):
    print("patch exists, proceeding....")
    tester = PatchRunner()
    result = tester._test_control_patch(args.pd_path)

    print(result)
    # else:
    #     print(f"Pd file path '{args.pd_path}' doesn't exist")


from sys import argv
if __name__ == "__main__":
    print("ARGV: ", argv)
    main()
