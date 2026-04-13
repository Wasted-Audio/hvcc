# Copyright (C) 2022-2025 Daniel Billotte, Wasted Audio
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
import unittest

from tests.framework.base_control import TestPdControlBase


class TestPdSignalCyclonePatches(TestPdControlBase):

    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "signal_cyclone")

    # Math operations

    def test_lt_gt(self):
        self._test_control_patch("test-lt-gt.pd")

    def test_lte_gte(self):
        self._test_control_patch("test-lte-gte.pd")

    def test_eq_neq(self):
        self._test_control_patch("test-eq-neq.pd")

    @unittest.skip("Needs work for selecting modes")
    def test_bit_and(self):
        self._test_control_patch("test-bit-and.pd")

    @unittest.skip("Needs work for selecting modes")
    def test_bit_not(self):
        self._test_control_patch("test-bit-not.pd")

    @unittest.skip("Needs work for selecting modes")
    def test_bit_or(self):
        self._test_control_patch("test-bit-or.pd")

    @unittest.skip("Needs work for selecting modes")
    def test_bit_shift(self):
        self._test_control_patch("test-bit-shift.pd")

    @unittest.skip("Needs work for selecting modes")
    def test_exc_or(self):
        self._test_control_patch("test-exc-or.pd")

    # Trigonometric

    def test_sinx_asin_sinh_asinh(self):
        self._test_control_patch("test-sinx-asin-sinh-asinh.pd", num_iterations=2)

    def test_cosx_acos_cosh_acosh(self):
        self._test_control_patch("test-cosx-acos-cosh-acosh.pd", num_iterations=2)

    def test_tanx_atan_tanh_atanh(self):
        self._test_control_patch("test-tanx-atan-tanh-atanh.pd", num_iterations=2)

    def test_atan2(self):
        self._test_control_patch("test-atan2.pd")

    # Other

    def test_bitsafe(self):
        self._test_control_patch("test-bitsafe.pd")


def main():
    # TODO(mhroth): make this work
    parser = argparse.ArgumentParser(
        description="Compile a specific pd patch.")
    parser.add_argument(
        "pd_path",
        help="The path to the Pd file to read.")
    args = parser.parse_args()
    if os.path.exists(args.pd_path):
        result = TestPdSignalCyclonePatches._test_control_patch(args.pd_path)
        print(result)
    else:
        print(f"Pd file path '{args.pd_path}' doesn't exist")


if __name__ == "__main__":
    main()
