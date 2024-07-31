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

from tests.framework.base_control import TestPdControlBase


class TestPdControlExprPatches(TestPdControlBase):
    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "control_expr")

    def test_mult(self):
        self._test_control_patch("test-mult.pd")

    def test_div(self):
        self._test_control_patch("test-div.pd")


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
