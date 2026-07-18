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


class TestPdMIDIOutPatches(TestPdMIDIBase):
    MIDI_RUNNER_SOURCE = "test_midi_out.cpp"
    SCRIPT_DIR = Path(__file__).parent
    TEST_DIR = Path(Path(__file__).parent, "pd", "midi_out")

    @classmethod
    def setUpClass(cls):
        command = "cd tests/src/; " \
            "clang++ create_test_midi.cpp midifile/src/MidiFile.cpp midifile/src/MidiEventList.cpp " \
            "midifile/src/MidiMessage.cpp midifile/src/MidiEvent.cpp midifile/src/Binasc.cpp -I midifile/include/ " \
            "-o create_test_midi ; " \
            "./create_test_midi"

        subprocess.run(command, capture_output=True, shell=True)

    def test_noteout(self):
        self._test_midi_patch("test-noteout.pd")

    def test_noteout_pack(self):
        self._test_midi_patch("test-noteout-pack.pd")

    # confirm that setting the channel on noteout works
    def test_noteout_pack_chan(self):
        self._test_midi_patch("test-noteout-pack-chan.pd")

    def test_ctlout(self):
        self._test_midi_patch("test-ctlout.pd")

    def test_ctlout_pack(self):
        self._test_midi_patch("test-ctlout-pack.pd")

    def test_polytouchout(self):
        self._test_midi_patch("test-polytouchout.pd")

    def test_polytouchout_pack(self):
        self._test_midi_patch("test-polytouchout-pack.pd")

    def test_pgmout(self):
        self._test_midi_patch("test-pgmout.pd")

    def test_pgmout_pack(self):
        self._test_midi_patch("test-pgmout-pack.pd")

    def test_touchout(self):
        self._test_midi_patch("test-touchout.pd")

    def test_touchout_pack(self):
        self._test_midi_patch("test-touchout-pack.pd")

    def test_bendout(self):
        self._test_midi_patch("test-bendout.pd")

    def test_bendout_pack(self):
        self._test_midi_patch("test-bendout-pack.pd")

    @unittest.SkipTest
    def test_midiout(self):
        self._test_midi_patch("test-midiout.pd")
