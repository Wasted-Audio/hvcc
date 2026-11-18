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

import functools
import platform
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import numpy
from scipy.io import wavfile

from tests.framework.base_test import HvBaseTest


def input_signal(channel: int, num_samples: int) -> numpy.ndarray:
    # same as input_sample() in tests/src/test_interleaved.c
    n = numpy.arange(num_samples, dtype=numpy.int64)
    return ((n * (2 * channel + 3)) % 1009 - 504).astype(numpy.float32) / numpy.float32(512)


class TestInterleavedProcessing(HvBaseTest):
    """hv_processInlineInterleaved() with aligned, misaligned and in-place buffers."""

    SCRIPT_DIR = Path(__file__).parent
    TEST_DIR = Path(Path(__file__).parent, "pd", "interleaved")

    def _flags(self) -> list[str]:
        flags = ["HV_SIMD_NONE"]
        if platform.machine().startswith("x86"):
            flags += ["HV_SIMD_SSE", "HV_SIMD_SSE_FMA", "HV_SIMD_AVX"]
        elif platform.machine().startswith(("arm", "aarch64")):
            flags += ["HV_SIMD_NEON"]
        return flags

    def _run_interleaved(
        self,
        exe_path: Path,
        out_dir: Path,
        sample_rate: int | None = None,
        block_size: int | None = None,
        num_iterations: int | None = None,
        flag: str | None = None,
        offset: int = 0,
        in_place: bool = False
    ) -> Path:
        # run executable
        # e.g. $ /path/heavy /path/heavy.wav 48000 480 100 1 0
        # offset: misalign the caller's buffers by this many floats; in_place: input buffer = output buffer
        wav_path = Path(out_dir, f"heavy.{flag}.{offset}.{int(in_place)}.wav")
        subprocess.check_output([
            exe_path,
            wav_path,
            str(sample_rate or 48000),
            str(block_size or 480),
            str(num_iterations or 100),
            str(offset),
            str(int(in_place))])

        return wav_path

    def _test_interleaved_patch(
        self,
        pd_file: str,
        expected: Callable[[Callable[[int], numpy.ndarray]], list[numpy.ndarray]],
        sample_rate: int | None = None,
        block_size: int | None = None,
        num_iterations: int | None = None
    ):
        """Compiles and runs a patch through hv_processInlineInterleaved() for every SIMD variant of
        this machine, with aligned and misaligned buffers, separate and in place.

        expected(x) returns the output channels for the input channels x(0), x(1), ...
        """
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
                for in_place in (False, True):
                    wav_path = self._run_interleaved(
                        exe_path, out_dir, sample_rate, block_size, num_iterations,
                        flag=flag, offset=offset, in_place=in_place)
                    _, result = wavfile.read(wav_path)
                    result = result.reshape(len(result), -1)
                    golden = numpy.stack(
                        expected(functools.partial(input_signal, num_samples=len(result))), axis=1)
                    numpy.testing.assert_array_equal(
                        result, golden,
                        err_msg=f"{pd_file} with {flag}, offset {offset}, in-place {in_place}")

    def test_interleaved_1ch(self):
        self._test_interleaved_patch(
            "test-interleaved-1ch.pd",
            lambda x: [x(0) * numpy.float32(0.5)])

    def test_interleaved_2ch(self):
        self._test_interleaved_patch(
            "test-interleaved-2ch.pd",
            lambda x: [x(0) - x(1), x(0) * numpy.float32(0.25)])

    def test_interleaved_3ch(self):
        self._test_interleaved_patch(
            "test-interleaved-3ch.pd",
            lambda x: [x(1) * numpy.float32(2), x(2) * numpy.float32(3), x(0) * numpy.float32(4)])
