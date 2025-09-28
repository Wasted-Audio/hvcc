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


class TestPdControlExprPatches(TestPdControlBase):
    """
        Consider all available expressions: https://pd.iem.sh/objects/expr~/
    """

    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "signal_expr")

    # Math operations

    def test_mult(self):
        self._test_control_patch("test-mult.pd")

    def test_div(self):
        self._test_control_patch("test-div.pd")

    def test_modulo(self):
        self._test_control_patch("test-modulo.pd")

    def test_add_sub(self):
        self._test_control_patch("test-add-sub.pd")

    def test_shift(self):
        self._test_control_patch("test-shift.pd")

    def test_lt_gt(self):
        self._test_control_patch("test-lt-gt.pd")

    def test_lte_gte(self):
        self._test_control_patch("test-lte-gte.pd")

    def test_eq_neq(self):
        self._test_control_patch("test-eq-neq.pd")

    def test_bit_and(self):
        self._test_control_patch("test-bit-and.pd")

    def test_exc_or(self):
        self._test_control_patch("test-exc-or.pd")

    def test_bit_or(self):
        self._test_control_patch("test-bit-or.pd")

    def test_log_and(self):
        self._test_control_patch("test-log-and.pd")

    def test_log_or(self):
        self._test_control_patch("test-log-or.pd")

    # Unary

    @unittest.skip("not supported yet")
    def test_unary_neg(self):
        self._test_control_patch("test-unary-neg.pd")

    def test_unary_tilde(self):
        self._test_control_patch("test-unary-tilde.pd")

    def test_unary_not(self):
        self._test_control_patch("test-unary-not.pd")

    # Functions

    def test_if(self):
        self._test_control_patch("test-if.pd")

    @unittest.skip("not supported yet (needs unary operator)")
    def test_if2(self):
        self._test_control_patch("test-if2.pd")

    def test_int(self):
        self._test_control_patch("test-int.pd")

    def test_rint(self):
        self._test_control_patch("test-rint.pd")

    def test_float(self):
        self._test_control_patch("test-float.pd")

    def test_min_max(self):
        self._test_control_patch("test-min-max.pd")

    def test_abs(self):
        self._test_control_patch("test-abs.pd")

    def test_isinf(self):
        self._test_control_patch("test-isinf.pd")

    def test_finite(self):
        self._test_control_patch("test-finite.pd")

    def test_isnan(self):
        self._test_control_patch("test-isnan.pd")

    def test_copysign(self):
        self._test_control_patch("test-copysign.pd")

    def test_modf(self):
        self._test_control_patch("test-modf.pd")

    # def test_imodf(self):
    #     self._test_control_patch("test-imodf.pd")

    # def test_remainder_fmod(self):
    #     self._test_control_patch("test-remainder-fmod.pd")

    def test_ceil_floor(self):
        self._test_control_patch("test-ceil-floor.pd")

    # # Power functions

    def test_pow(self):
        self._test_control_patch("test-pow.pd")

    def test_sqrt(self):
        self._test_control_patch("test-sqrt.pd")

    def test_exp(self):
        self._test_control_patch("test-exp.pd")

    def test_expm1(self):
        self._test_control_patch("test-expm1.pd")

    def test_ln_log(self):
        self._test_control_patch("test-ln-log.pd")

    def test_log10(self):
        self._test_control_patch("test-log10.pd")

    # def test_fact(self):
    #     self._test_control_patch("test-fact.pd")

    def test_erf_erfc(self):
        self._test_control_patch("test-erf-erfc.pd")

    def test_cbrt(self):
        self._test_control_patch("test-cbrt.pd")

    def test_log1p(self):
        self._test_control_patch("test-log1p.pd")

    # def test_ldexp(self):
    #     self._test_control_patch("test-ldexp.pd")

    # # Trigonometric

    # def test_sin_asin_sinh_asinh(self):
    #     self._test_control_patch("test-sin-asin-sinh-asinh.pd")

    # def test_cos_acos_cosh_acosh(self):
    #     self._test_control_patch("test-cos-acos-cosh-acosh.pd")

    # def test_tan_atan_tanh_atanh(self):
    #     self._test_control_patch("test-tan-atan-tanh-atanh.pd")

    # def test_atan2(self):
    #     self._test_control_patch("test-atan2.pd")

    # # Some complex expressions

    # def test_complex_expr1(self):
    #     self._test_control_patch("test-complex-expr1.pd")

    # def test_complex_expr2(self):
    #     self._test_control_patch("test-complex-expr2.pd")


def main():
    # TODO(mhroth): make this work
    parser = argparse.ArgumentParser(
        description="Compile a specific pd patch.")
    parser.add_argument(
        "pd_path",
        help="The path to the Pd file to read.")
    args = parser.parse_args()
    if os.path.exists(args.pd_path):
        result = TestPdControlExprPatches._test_control_patch(args.pd_path)
        print(result)
    else:
        print(f"Pd file path '{args.pd_path}' doesn't exist")


if __name__ == "__main__":
    main()
