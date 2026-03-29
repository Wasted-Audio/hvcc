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

import argparse
import os
import shutil

from tests.framework.base_signal import TestPdSignalBase


class TestPdSignalPatches(TestPdSignalBase):
    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "signal")

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

    test_patch = TestPdSignalPatches()
    test_patch.setUp()
    out_dir = test_patch._run_hvcc(args.pd_path)
    assert out_dir is not None

    c_src_dir = os.path.join(out_dir, "c")
    shutil.copy2(os.path.join(test_patch.SCRIPT_DIR, "src/test_signal.c"), c_src_dir)
    shutil.copy2(os.path.join(test_patch.SCRIPT_DIR, "src/tinywav/tinywav.h"), c_src_dir)
    shutil.copy2(os.path.join(test_patch.SCRIPT_DIR, "src/tinywav/tinywav.c"), c_src_dir)
    c_sources = os.listdir(c_src_dir)

    wav_path = test_patch.compile_and_run(
        source_files=c_sources,
        out_dir=out_dir,
        sample_rate=args.samplerate,
        block_size=args.blocksize,
        num_iterations=args.numblocks,
        flag=args.simd)

    if args.verbose:
        print(os.path.abspath(wav_path))


if __name__ == "__main__":
    main()
