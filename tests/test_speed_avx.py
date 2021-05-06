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

import os
import shutil
import subprocess
import time
import unittest

SCRIPT_DIR = os.path.dirname(__file__)

def compile_and_run_patch(pd_file):
    # setup
    patch_name = os.path.splitext(os.path.basename(pd_file))[0]

    # clean any existing output directories
    out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "./build"))
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    # create new output directories and copy over assets
    c_src_dir = os.path.join(out_dir, "src")
    os.makedirs(c_src_dir)
    asm_dir = os.path.join(out_dir, "asm")
    os.makedirs(asm_dir)
    shutil.copy2(os.path.join(SCRIPT_DIR, "test_speed.c"), c_src_dir)

    # pd2hv
    py_script = os.path.join(SCRIPT_DIR, "../interpreters/pd2hv/pd2hv.py")
    cmd = (["python", py_script, pd_file,
            "-o", out_dir,
            "-v"])
    print(subprocess.check_output(cmd))

    # hv2ir
    py_script = os.path.join(SCRIPT_DIR, "../core/hv2ir/hv2ir.py")
    hv_file = os.path.join(out_dir, patch_name + ".hv.json")
    ir_file = os.path.join(out_dir, patch_name + ".ir.hv.json")
    cmd = (["python", py_script, hv_file,
            "--hv_ir_path", ir_file])
    print(subprocess.check_output(cmd))

    # ir2c
    ir2c_dir = os.path.join(SCRIPT_DIR, "../generators/ir2c")
    cmd = (["python", os.path.join(ir2c_dir, "ir2c.py"), ir_file,
            "--static_path", os.path.join(ir2c_dir, "static"),
            "--template_path", os.path.join(ir2c_dir, "template"),
            "--output_path", c_src_dir,
            "--verbose"])
    print(subprocess.check_output(cmd))

    # ir2c-perf
    cmd = (["python", os.path.join(ir2c_dir, "ir2c_perf.py"), ir_file])
    print(subprocess.check_output(cmd))

    c_sources = [os.path.join(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith(".c")]
    flags = [
        "-msse" ,"-msse2", "-msse3", "-mssse3", "-msse4.1", "-msse4.2", "-mavx",
        "-O3", "-march=native",
        "-funsafe-math-optimizations",  "-ffast-math", "-freciprocal-math",
        "-ffinite-math-only",  "-fassociative-math", "-fno-trapping-math",
        "-DNDEBUG"
    ]

    # generate assembly
    print("Assembly output directory: ", asm_dir + "/")
    for c_src in c_sources:
        asm_out = os.path.join(asm_dir, os.path.splitext(os.path.basename(c_src))[0] + ".s")
        cmd = ["clang"] + flags + ["-S", "-O3", "-mllvm", "--x86-asm-syntax=intel", c_src, "-o", asm_out]
        subprocess.check_output(cmd)

    # compile app
    exe_file = os.path.join(out_dir, "heavy")
    cmd = ["clang", "-Werror"] + flags + c_sources + ["-o", exe_file, "-lm"]

    start_time = time.time()
    subprocess.check_output(cmd)
    compile_time_s = (time.time() - start_time) * 1000.0
    print("Total compile time: {0:2f}ms\n".format(compile_time_s))

    # run executable (returns stdout)
    result = subprocess.check_output([exe_file]).split("\n")

    # # clean up
    # if os.path.exists(out_dir):
    #     shutil.rmtree(out_dir)

    return result


class TestPdPatches(unittest.TestCase):

    def test_speed_avx(self):
        self.maxDiff = None
        # collect all test patches in script directory
        patches_dir = os.path.join(SCRIPT_DIR, "pd", "speed")
        test_patches = []
        for f in os.listdir(patches_dir):
            if f.startswith("test-") and f.endswith(".pd"):
                test_patches.append(os.path.join(patches_dir, f))

        # compile, run and compare patches
        for pd_file in test_patches:
            patch_name = os.path.splitext(os.path.basename(pd_file))[0]

            print()
            print("##################################################")
            print("#")
            print("# Testing patch " + pd_file)
            print("#")
            print("##################################################")
            result = compile_and_run_patch(pd_file)
            print("\n".join(result))
