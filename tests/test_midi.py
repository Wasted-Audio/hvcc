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

import unittest
import subprocess

from pathlib import Path

from tests.framework.base_midi import TestPdMIDIBase


class TestPdMIDIPatches(TestPdMIDIBase):
    SCRIPT_DIR = Path(__file__).parent
    TEST_DIR = Path(Path(__file__).parent, "pd", "midi")

    @classmethod
    def setUpClass(cls):
        command = "cd tests/src/; " \
            "clang++ create_test_midi.cpp midifile/src/MidiFile.cpp midifile/src/MidiEventList.cpp " \
            "midifile/src/MidiMessage.cpp midifile/src/MidiEvent.cpp midifile/src/Binasc.cpp -I midifile/include/ " \
            "-o create_test_midi ; " \
            "./create_test_midi"

        subprocess.run(command, capture_output=True, shell=True)

    def test_notein(self):
        self._test_midi_patch("test-notein.pd")

    def test_notein_channel(self):
        self._test_midi_patch("test-notein-channel.pd")

    def test_ctlin(self):
        self._test_midi_patch("test-ctlin.pd")

    def test_ctlin_controller(self):
        self._test_midi_patch("test-ctlin-controller.pd")

    def test_ctlin_controller_channel(self):
        self._test_midi_patch("test-ctlin-controller-channel.pd")

    def test_nbendin(self):
        self._test_midi_patch("test-bendin.pd")

    def test_nbendin_channel(self):
        self._test_midi_patch("test-bendin-channel.pd")

    def test_polytouchin(self):
        self._test_midi_patch("test-polytouchin.pd")

    def test_polytouchin_channel(self):
        self._test_midi_patch("test-polytouchin-channel.pd")

    def test_pgmin(self):
        self._test_midi_patch("test-pgmin.pd")

    def test_pgmin_channel(self):
        self._test_midi_patch("test-pgmin-channel.pd")

    def test_touchin(self):
        self._test_midi_patch("test-touchin.pd")

    def test_touchin_channel(self):
        self._test_midi_patch("test-touchin-channel.pd")

    @unittest.SkipTest
    def test_midiin(self):
        self._test_midi_patch("test-midiin.pd")
