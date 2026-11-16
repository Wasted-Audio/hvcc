# Copyright (C) 2026 Wasted Audio
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

import platform
import shutil
import subprocess
from pathlib import Path

import numpy
from scipy.io import wavfile

from tests.framework.base_test import ARM_MACHINES, HvBaseTest

SAMPLE_RATE = 48000
BLOCK_SIZE = 480
NUM_ITERATIONS = 4


def input_signal(channel: int, num_samples: int) -> numpy.ndarray:
    # same as input_sample() in tests/src/test_interleaved.c
    n = numpy.arange(num_samples, dtype=numpy.int64)
    return ((n * (2 * channel + 3)) % 1009 - 504).astype(numpy.float32) / numpy.float32(512)


class TestInterleavedProcessing(HvBaseTest):
    """hv_processInlineInterleaved() with aligned, misaligned and in-place buffers."""

    SCRIPT_DIR = Path(__file__).parent
    TEST_DIR = Path(Path(__file__).parent, "pd", "interleaved")

    def _flags(self):
        flags = ["HV_SIMD_NONE"]
        if platform.machine().startswith("x86"):
            flags += ["HV_SIMD_SSE", "HV_SIMD_SSE_FMA", "HV_SIMD_AVX"]
        elif platform.machine().startswith(ARM_MACHINES):
            flags += ["HV_SIMD_NEON"]
        return flags

    def _test_interleaved_patch(self, pd_file: str, expected: numpy.ndarray):
        out_dir = self._run_hvcc(Path(self.TEST_DIR, pd_file))
        assert out_dir is not None
        c_src_dir = Path(out_dir, "c")
        shutil.copy2(Path(self.SCRIPT_DIR, "src/test_interleaved.c"), c_src_dir)
        shutil.copy2(Path(self.SCRIPT_DIR, "src/tinywav/tinywav.h"), c_src_dir)
        shutil.copy2(Path(self.SCRIPT_DIR, "src/tinywav/tinywav.c"), c_src_dir)
        source_files = [Path(child) for child in c_src_dir.iterdir()]

        for flag in self._flags():
            exe_path = self._compile_and_run(source_files, out_dir, flag)
            for offset in (0, 1):
                for in_place in (0, 1):
                    wav_path = Path(out_dir, f"heavy.{flag}.{offset}.{in_place}.wav")
                    subprocess.check_output([
                        exe_path, wav_path, str(SAMPLE_RATE), str(BLOCK_SIZE), str(NUM_ITERATIONS),
                        str(offset), str(in_place)])
                    _, result = wavfile.read(wav_path)
                    numpy.testing.assert_array_equal(
                        result.reshape(len(result), -1), expected,
                        err_msg=f"{pd_file} with {flag}, offset {offset}, in-place {in_place}")

    def test_interleaved_1ch(self):
        n = BLOCK_SIZE * NUM_ITERATIONS
        self._test_interleaved_patch("test-interleaved-1ch.pd", numpy.stack([
            input_signal(0, n) * numpy.float32(0.5)], axis=1))

    def test_interleaved_2ch(self):
        n = BLOCK_SIZE * NUM_ITERATIONS
        x0, x1 = input_signal(0, n), input_signal(1, n)
        self._test_interleaved_patch("test-interleaved-2ch.pd", numpy.stack([
            x0 - x1, x0 * numpy.float32(0.25)], axis=1))

    def test_interleaved_3ch(self):
        n = BLOCK_SIZE * NUM_ITERATIONS
        x0, x1, x2 = input_signal(0, n), input_signal(1, n), input_signal(2, n)
        self._test_interleaved_patch("test-interleaved-3ch.pd", numpy.stack([
            x1 * numpy.float32(2), x2 * numpy.float32(3), x0 * numpy.float32(4)], axis=1))
