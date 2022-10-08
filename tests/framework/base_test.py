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
import jinja2
import os
import platform
import shutil
import subprocess
import sys
import unittest

sys.path.append("../")
import hvcc
from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum


simd_flags = {
    "HV_SIMD_NONE": ["-DHV_SIMD_NONE"],
    "HV_SIMD_SSE": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1"],
    "HV_SIMD_SSE_FMA": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-mfma"],
    "HV_SIMD_AVX": ["-msse", "-msse2", "-msse3", "-mssse3", "-msse4.1", "-mavx", "-mfma"],
    "HV_SIMD_NEON": ["-mcpu=cortex-a7", "-mfloat-abi=hard"]
}


class HvBaseTest(unittest.TestCase):
    SCRIPT_DIR = ''

    def setUp(self):
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader(os.path.join(
            os.path.dirname(__file__),
            "template"))

    @classmethod
    def _run_hvcc(clazz, pd_path):
        """Run hvcc on a Pd file. Returns the output directory.
        """

        # clean default output directories
        out_dir = os.path.join(clazz.SCRIPT_DIR, "build")
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        hvcc_results = hvcc.compile_dataflow(pd_path, out_dir, verbose=False)
        for r in hvcc_results.values():
            # if there are any errors from hvcc, fail immediately
            # TODO(mhroth): standardise how errors and warnings are returned between stages
            if r["notifs"].get("has_error", False):
                # raise Exception(r["notifs"]["errors"][0] if r["stage"] == "pd2hv" else str(r["notifs"]))
                if r["stage"] == "pd2hv":
                    clazz.fail(hvcc_results["pd2hv"]["notifs"]["errors"][0])
                else:
                    clazz.fail(str(r["notifs"]))

        return out_dir
