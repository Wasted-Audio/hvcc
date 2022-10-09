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
import unittest

from tests.framework.base_speed import TestPdSpeedBase

raise unittest.SkipTest()


class TestPdPatches(TestPdSpeedBase):

    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "speed")
    # test results cannot be more than 2% slower than the golden value
    __PERCENT_THRESHOLD = 2.0

    def test_00_fire(self):
        self._test_speed_patch("test-00-fire.pd")

    def test_01_fire(self):
        self._test_speed_patch("test-01-fire.pd")
