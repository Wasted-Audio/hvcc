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

import os
import unittest

from tests.framework.base_midi import TestPdMIDIBase


class TestPdMIDIPatches(TestPdMIDIBase):
    SCRIPT_DIR = os.path.dirname(__file__)
    TEST_DIR = os.path.join(os.path.dirname(__file__), "pd", "midi")

    def test_midinotein(self):
        self._test_midi_patch("test-midinotein.pd")

    def test_midinotein_channel(self):
        self._test_midi_patch("test-midinotein-channel.pd")

    def test_midictlin(self):
        self._test_midi_patch("test-midictlin.pd")

    def test_midictlin_controller(self):
        self._test_midi_patch("test-midictlin-controller.pd")

    def test_midictlin_controller_channel(self):
        self._test_midi_patch("test-midictlin-controller-channel.pd")

    def test_midinbendin(self):
        self._test_midi_patch("test-midibendin.pd")

    def test_midinbendin_channel(self):
        self._test_midi_patch("test-midibendin-channel.pd")

    def test_midipolytouchin(self):
        self._test_midi_patch("test-midipolytouchin.pd")

    def test_midipolytouchin_channel(self):
        self._test_midi_patch("test-midipolytouchin-channel.pd")
    
    def test_midipgmin(self):
        self._test_midi_patch("test-midipgmin.pd")

    def test_midipgmin_channel(self):
        self._test_midi_patch("test-midipgmin-channel.pd")

    def test_miditouchin(self):
        self._test_midi_patch("test-miditouchin.pd")

    def test_miditouchin_channel(self):
        self._test_midi_patch("test-miditouchin-channel.pd")

    @unittest.SkipTest
    def test_midiin(self):
        self._test_midi_patch("test-midiin.pd")
