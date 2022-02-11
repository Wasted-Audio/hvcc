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
import numpy
import os
import platform
import shutil
from scipy.io import wavfile
import subprocess
import sys
import unittest

sys.path.append("../")
import hvcc

SCRIPT_DIR = os.path.dirname(__file__)
SIGNAL_TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "signal")


class TestPdSignalPatches(unittest.TestCase):

    __ENV__ = jinja2.Environment()
    __ENV__.loader = jinja2.FileSystemLoader(os.path.join(
        os.path.dirname(__file__),
        "template"))

    @classmethod
    def _compile_and_run(clazz, out_dir, source_files,
                         sample_rate=None, block_size=None, num_iterations=None, flag=None):

        simd_flags = {
            "HV_SIMD_NONE": ["-DHV_SIMD_NONE"],
            "HV_SIMD_SSE": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1"],
            "HV_SIMD_SSE_FMA": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-mfma"],
            "HV_SIMD_AVX": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-mavx", "-mfma"],
            "HV_SIMD_NEON": ["-mcpu=cortex-a7", "-mfloat-abi=hard"]
        }

        exe_path = os.path.join(out_dir, "heavy")

        # template Makefile
        # NOTE(mhroth): assertions are NOT turned off (help to catch errors)
        makefile_path = os.path.join(out_dir, "c", "Makefile")
        with open(makefile_path, "w") as f:
            f.write(TestPdSignalPatches.__ENV__.get_template("Makefile").render(
                simd_flags=simd_flags[flag or "HV_SIMD_NONE"],
                source_files=source_files,
                out_path=exe_path))

        # run the compile command
        subprocess.check_output(["make", "-C", os.path.dirname(makefile_path), "-j"])

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

    def _compare_wave_output(self, out_dir, c_sources, golden_path, flag=None):
        # http://stackoverflow.com/questions/10580676/comparing-two-numpy-arrays-for-equality-element-wise
        # http://docs.scipy.org/doc/numpy/reference/routines.testing.html

        TestPdSignalPatches._compile_and_run(out_dir, c_sources, flag=flag)

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

    @classmethod
    def _run_hvcc(clazz, pd_path):
        """Run hvcc on a Pd file. Returns the output directory.
        """

        # clean default output directories
        out_dir = os.path.join(SCRIPT_DIR, "build")
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        hvcc_results = hvcc.compile_dataflow(pd_path, out_dir)
        for r in hvcc_results.values():
            # if there are any errors from hvcc, fail immediately
            # TODO(mhroth): standardise how errors and warnings are returned between stages
            if r["notifs"].get("has_error", False):
                raise Exception(r["notifs"]["errors"][0] if r["stage"] == "pd2hv" else str(r["notifs"]))

        return out_dir

    def _test_signal_patch(self, pd_file):
        """Compiles, runs, and tests a signal patch.
        """

        pd_path = os.path.join(SIGNAL_TEST_DIR, pd_file)
        patch_name = os.path.splitext(os.path.basename(pd_path))[0]
        golden_path = os.path.join(SIGNAL_TEST_DIR, f"{patch_name}.golden.wav")
        self.assertTrue(os.path.exists(golden_path), f"File not found: {golden_path}")

        try:
            out_dir = TestPdSignalPatches._run_hvcc(pd_path)
        except Exception as e:
            self.fail(str(e))

        # copy over additional C assets
        c_src_dir = os.path.join(out_dir, "c")
        for c in os.listdir(os.path.join(SCRIPT_DIR, "src", "signal")):
            shutil.copy2(os.path.join(SCRIPT_DIR, "src", "signal", c), c_src_dir)

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

    def test_line(self):
        self._test_signal_patch("test-line.pd")

    def test_phasor_control(self):
        self._test_signal_patch("test-phasor-control.pd")


def main():
    parser = argparse.ArgumentParser(
        description="A script used to generate golden files for signal tests.")
    parser.add_argument(
        "pd_path",
        help="A Pd patch to render to WAV.")
    parser.add_argument(
        "--simd",
        default="HV_SIMD_NONE",
        help="Possible values are 'HV_SIMD_NONE', 'HV_SIMD_SSE', 'HV_SIMD_SSE_FMA', 'HV_SIMD_AVX', or HV_SIMD_NEON.")
    parser.add_argument(
        "--samplerate", "-r",
        type=int,
        default=48000,
        help="Defaults to 48000.")
    parser.add_argument(
        "--blocksize", "-b",
        type=int,
        default=480,
        help="Defaults to 480.")
    parser.add_argument(
        "--numblocks", "-n",
        type=int,
        default=100,
        help="Defaults to 100.")
    parser.add_argument(
        "--verbose", "-v",
        help="Show debugging information.",
        action="count")
    args = parser.parse_args()

    out_dir = TestPdSignalPatches._run_hvcc(args.pd_path)

    c_src_dir = os.path.join(out_dir, "c")
    c_sources = [os.path.join(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith(".c")]

    wav_path = TestPdSignalPatches._compile_and_run(
        out_dir,
        c_sources,
        args.samplerate,
        args.blocksize,
        args.numblocks,
        flag=args.simd)

    if args.verbose:
        print(os.path.abspath(wav_path))


if __name__ == "__main__":
    main()
