# Heavy Compiler Collection
# Copyright (C) 2025-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import json

from pathlib import Path

from hvcc.interpreters.pd2gui.pd2gui import pd2gui
from hvcc.version import VERSION


class TestPdGuiParser:
    SCRIPT_DIR = Path(__file__).parent

    def _test_gui_patch(
        self,
        path: str
    ) -> None:
        source_path = Path(self.SCRIPT_DIR, "data", path)
        ir_path = Path(self.SCRIPT_DIR, "ir")
        gui_path = Path(ir_path, Path(path).stem + ".gui.json")

        response = pd2gui.compile(
            pd_path=source_path,
            ir_file=gui_path
        )

        if response.notifs.has_error:
            raise Exception(response.notifs.errors[0])

        with open(gui_path, "r") as f:
            gui = json.loads(f.read())

        expected_path = Path(source_path.parent, source_path.stem + ".golden.json")
        with open(expected_path, "r") as f:
            expected = json.loads(f.read())
            expected['version'] = VERSION

        assert gui == expected

    def test_abstraction(self):
        self._test_gui_patch("gui_abstraction.pd")

    def test_subpatch(self):
        self._test_gui_patch("gui_subpatch.pd")

    def test_dollarzero(self):
        self._test_gui_patch("gui_dollarzero.pd")

    def test_abs_args(self):
        self._test_gui_patch("gui_abs_args.pd")
