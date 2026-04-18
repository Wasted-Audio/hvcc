# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2022-2026 Wasted Audio
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
import shutil
import subprocess
import time
import unittest

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

raise unittest.SkipTest()


def compile_and_run_patch(pd_file):
    # setup
    patch_name = pd_file.stem

    # clean any existing output directories
    out_dir = Path(SCRIPT_DIR, "./build").absolute()
    if out_dir.exists():
        shutil.rmtree(out_dir)

    # create new output directories and copy over assets
    c_src_dir = Path(out_dir, "src")
    c_src_dir.mkdir(parents=True)
    asm_dir = Path(out_dir, "asm")
    asm_dir.mkdir(parents=True)
    shutil.copy2(Path(SCRIPT_DIR, "test_speed.c"), c_src_dir)

    # pd2hv
    py_script = Path(SCRIPT_DIR, "../hvcc/interpreters/pd2hv/pd2hv.py")
    cmd = (["python", py_script, pd_file, out_dir, "-v"])
    print(subprocess.check_output(cmd))

    # hv2ir
    py_script = Path(SCRIPT_DIR, "../hvcc/core/hv2ir/hv2ir.py")
    hv_file = Path(out_dir, f"{patch_name}.hv.json")
    ir_file = Path(out_dir, f"{patch_name}.ir.hv.json")
    cmd = (["python", py_script, hv_file, "--hv_ir_path", ir_file])
    print(subprocess.check_output(cmd))

    # ir2c
    ir2c_dir = Path(SCRIPT_DIR, "../hvcc/generators/ir2c/")
    cmd = (["python", Path(ir2c_dir, "ir2c.py"), ir_file,
            "--static_dir", Path(ir2c_dir, "static"),
            # "--template_path", Path(ir2c_dir, "template"),
            "--output_dir", c_src_dir,
            "--verbose"])
    print(subprocess.check_output(cmd))

    # ir2c-perf
    cmd = (["python", Path(ir2c_dir, "ir2c_perf.py"), ir_file])
    print(subprocess.check_output(cmd))

    c_sources = [Path(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith(".c")]
    flags = [
        "-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2", "-mavx",
        "-O3", "-march=native",
        "-funsafe-math-optimizations", "-ffast-math", "-freciprocal-math",
        "-ffinite-math-only", "-fassociative-math", "-fno-trapping-math",
        "-DNDEBUG"
    ]

    # generate assembly
    print(f"Assembly output directory: {asm_dir}/")
    for c_src in c_sources:
        asm_out = Path(asm_dir, f"{Path(c_src).stem}.s")
        cmd = ["clang"] + flags + ["-S", "-O3", "-mllvm", "--x86-asm-syntax=intel", c_src, "-o", asm_out]
        subprocess.check_output(cmd)

    # compile app
    exe_file = Path(out_dir, "heavy")
    cmd = ["clang", "-Werror"] + flags + c_sources + ["-o", exe_file, "-lm"]

    start_time = time.time()
    subprocess.check_output(cmd)
    compile_time_s = (time.time() - start_time) * 1000.0
    print(f"Total compile time: {compile_time_s:2f}ms\n")

    # run executable (returns stdout)
    result = subprocess.check_output([exe_file]).split("\n")

    # # clean up
    # if out_dir.exists():
    #     shutil.rmtree(out_dir)

    return result


class TestPdPatches(unittest.TestCase):

    def test_speed_avx(self):
        self.maxDiff = None
        # collect all test patches in script directory
        patches_dir = Path(SCRIPT_DIR, "pd", "speed")
        test_patches = []
        for f in os.listdir(patches_dir):
            if f.startswith("test-") and f.endswith(".pd"):
                test_patches.append(Path(patches_dir, f))

        # compile, run and compare patches
        for pd_file in test_patches:
            # patch_name = os.path.splitext(os.path.basename(pd_file))[0]

            print(
                "##################################################\n"
                "#\n"
                f"# Testing patch {pd_file}\n"
                "#\n"
                "##################################################")

            result = compile_and_run_patch(pd_file)
            print("\n".join(result))
