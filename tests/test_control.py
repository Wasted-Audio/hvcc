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
import unittest

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from tests.framework.base_control import TestPdControlBase


class TestPdControlPatches(TestPdControlBase):
    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "control")

    def test_abs(self):
        self._test_control_patch("test-abs.pd")

    def test_add(self):
        self._test_control_patch("test-add.pd")

    def test_and(self):
        self._test_control_patch("test-and.pd")

    def test_array(self):
        self._test_control_patch("test-array.pd")

    def test_array_long(self):
        self._test_control_patch("test-array_long.pd", allow_warnings=False)

    def test_atan(self):
        self._test_control_patch("test-atan.pd")

    def test_atan2(self):
        self._test_control_patch("test-atan2.pd")

    def test_bang(self):
        self._test_control_patch("test-bang.pd")

    def test_bin_and(self):
        self._test_control_patch("test-binary-and.pd")

    def test_bin_shiftleft(self):
        self._test_control_patch("test-binary-bitshift_left.pd")

    def test_bin_shiftright(self):
        self._test_control_patch("test-binary-bitshift_right.pd")

    def test_bin_or(self):
        self._test_control_patch("test-binary-or.pd")

    def test_change(self):
        self._test_control_patch("test-change.pd")

    def test_clip(self):
        self._test_control_patch("test-clip.pd")

    def test_cos(self):
        self._test_control_patch("test-cos.pd")

    def test_dbtopow(self):
        self._test_control_patch("test-dbtopow.pd")

    def test_dbtorms(self):
        self._test_control_patch("test-dbtorms.pd")

    # NOTE(mhroth): also does a good job testing abstraction support
    def test_declare(self):
        self._test_control_patch("test-declare.pd")

    def test_delay(self):
        self._test_control_patch("test-delay.pd")

    def test_div(self):
        self._test_control_patch("test-div.pd")

    def test_divide(self):
        self._test_control_patch("test-divide.pd")

    def test_dollar_arg(self):
        self._test_control_patch("test-dollar_arg.pd")

    def test_eq(self):
        self._test_control_patch("test-eq.pd")

    def test_empty_message(self):
        self._test_control_patch_expect_warning("test-empty_message.pd", NotificationEnum.WARNING_EMPTY_MESSAGE)

    def test_exp(self):
        self._test_control_patch("test-exp.pd")

    def test_extern_names_capitals(self):
        self._test_control_patch_expect_error("test-extern_names_capitals.pd", None)

    def test_empty_patch(self):
        self._test_control_patch("test-empty_patch.pd")

    def test_float(self):
        self._test_control_patch("test-float.pd")

    def test_ftom(self):
        self._test_control_patch("test-ftom.pd")

    def test_greaterthan(self):
        self._test_control_patch("test-greaterthan.pd")

    def test_greaterthaneq(self):
        self._test_control_patch("test-greaterthaneq.pd")

    def test_gui(self):
        self._test_control_patch("test-gui.pd")

    def test_hanging_binop(self):
        self._test_control_patch("test-hanging_binop.pd")

    def test_int(self):
        self._test_control_patch("test-int.pd")

    def test_lessthan(self):
        self._test_control_patch("test-lessthan.pd")

    def test_lessthaneq(self):
        self._test_control_patch("test-lessthaneq.pd")

    def test_line(self):
        self._test_control_patch("test-line.pd")

    def test_loadbang(self):
        self._test_control_patch("test-loadbang.pd")

    def test_local_search(self):
        self._test_control_patch("test-local-search.pd")

    def test_log(self):
        self._test_control_patch("test-log.pd")

    def test_log2(self):
        self._test_control_patch("test-log2.pd")

    def test_log10(self):
        self._test_control_patch("test-log10.pd")

    def test_makenote(self):
        self._test_control_patch("test-makenote.pd", num_iterations=10)

    def test_max(self):
        self._test_control_patch("test-max.pd")

    def test_metro(self):
        self._test_control_patch("test-metro.pd", num_iterations=100)

    def test_min(self):
        self._test_control_patch("test-min.pd")

    def test_mod(self):
        self._test_control_patch("test-mod.pd")

    def test_moses(self):
        self._test_control_patch("test-moses.pd")

    def test_msg(self):
        self._test_control_patch("test-msg.pd")

    def test_remote_msg(self):
        self._test_control_patch("test-remote-msg.pd")

    def test_msg_remote_args(self):
        self._test_control_patch("test-msg_remote_args.pd")

    def test_mtof(self):
        self._test_control_patch("test-mtof.pd")

    def test_multiply(self):
        self._test_control_patch("test-multiply.pd")

    def test_naked_dollar(self):
        self._test_control_patch("test-naked_dollar.pd")

    def test_neq(self):
        self._test_control_patch("test-neq.pd")

    def test_null_object(self):
        self._test_control_patch("test-null_object.pd")

    def test_pack(self):
        self._test_control_patch("test-pack.pd")

    def test_pack_wrong_args(self):
        self._test_control_patch_expect_error("test-pack_wrong_args.pd", NotificationEnum.ERROR_PACK_FLOAT_ARGUMENTS)

    def test_pipe(self):
        self._test_control_patch("test-pipe.pd", num_iterations=100)

    def test_poly(self):
        self._test_control_patch("test-poly.pd")

    def test_pow(self):
        self._test_control_patch("test-pow.pd")

    def test_powtodb(self):
        self._test_control_patch("test-powtodb.pd")

    def test_print(self):
        self._test_control_patch("test-print.pd")

    def test_random(self):
        self._test_control_patch("test-random.pd", num_iterations=10)

    def test_rmstodb(self):
        self._test_control_patch("test-rmstodb.pd")

    def test_route(self):
        self._test_control_patch("test-route.pd")

    @unittest.skip("currently does not support right inlet")
    def test_select(self):
        self._test_control_patch("test-select.pd")

    def test_select_min(self):
        self._test_control_patch("test-select-min.pd")

    def test_send_receive(self):
        self._test_control_patch("test-send_receive.pd")

    def test_sin(self):
        self._test_control_patch("test-sin.pd")

    def test_stripnote(self):
        self._test_control_patch("test-stripnote.pd")

    def test_spigot(self):
        self._test_control_patch("test-spigot.pd")

    def test_sqrt(self):
        self._test_control_patch("test-sqrt.pd")

    def test_subpatch(self):
        self._test_control_patch("test-subpatch.pd")

    def test_subtract(self):
        self._test_control_patch("test-subtract.pd")

    def test_swap(self):
        self._test_control_patch("test-swap.pd")

    def test_table(self):
        self._test_control_patch("test-table.pd")

    def test_tabread_no_args(self):
        self._test_control_patch_expect_error(
            "test-tabread_no_args.pd",
            NotificationEnum.ERROR_MISSING_REQUIRED_ARGUMENT)

    def test_tabread(self):
        self._test_control_patch("test-tabread.pd")

    def test_tabwrite(self):
        self._test_control_patch("test-tabwrite.pd")

    def test_tan(self):
        self._test_control_patch("test-tan.pd")

    def test_tgl(self):
        self._test_control_patch("test-tgl.pd")

    def test_timer(self):
        self._test_control_patch("test-timer.pd", num_iterations=20)

    def test_top_level_dollar_args(self):
        self._test_control_patch("test-top_level_dollar_args.pd")

    def test_top_level_lets(self):
        self._test_control_patch_expect_error(
            "test-top_level_lets.pd",
            NotificationEnum.ERROR_NO_TOPLEVEL_SIGNAL_LETS)

    def test_trigger_invalid_args(self):
        self._test_control_patch_expect_error(
            "test-trigger_invalid_args.pd",
            NotificationEnum.ERROR_TRIGGER_ABFS)

    def test_trigger(self):
        self._test_control_patch("test-trigger.pd")

    def test_unpack(self):
        self._test_control_patch("test-unpack.pd")

    def test_until(self):
        self._test_control_patch("test-until.pd")

    def test_variable_args(self):
        self._test_control_patch("test-variable_args.pd")

    def test_width(self):
        self._test_control_patch(
            "test-width.pd",
            fail_message="Parser failed to parse an object with an adjusted width.")

    def test_wrap(self):
        self._test_control_patch("test-wrap.pd")


def main():
    # TODO(mhroth): make this work
    parser = argparse.ArgumentParser(
        description="Compile a specific pd patch.")
    parser.add_argument(
        "pd_path",
        help="The path to the Pd file to read.")
    args = parser.parse_args()
    if os.path.exists(args.pd_path):
        test_control = TestPdControlPatches()
        result = test_control._test_control_patch(pd_file=args.pd_path)
        print(result)
    else:
        print(f"Pd file path '{args.pd_path}' doesn't exist")


if __name__ == "__main__":
    main()
