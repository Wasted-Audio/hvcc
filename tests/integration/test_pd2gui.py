# Heavy Compiler Collection
# Copyright (C) 2025-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import os
import json

from hvcc.interpreters.pd2gui.pd2gui import pd2gui
from hvcc.version import VERSION


class TestPdGuiParser:
    SCRIPT_DIR = os.path.dirname(__file__)

    def _test_gui_patch(
        self,
        path: str
    ) -> None:
        source_path = os.path.join(self.SCRIPT_DIR, "data", path)
        ir_file = os.path.join(self.SCRIPT_DIR, "ir", os.path.splitext(path)[0] + ".gui.json")

        response = pd2gui.compile(
            pd_path=source_path,
            ir_file=ir_file
        )

        if response.notifs.has_error:
            raise Exception(response.notifs.errors[0])

        with open(ir_file, "r") as f:
            gui = json.loads(f.read())

        expected_path = os.path.join(os.path.splitext(source_path)[0] + ".golden.json")
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
