# Heavy Compiler Collection
# Copyright (C) 2025-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import time

from typing import Optional
from pathlib import Path

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.interpreters.pd2gui.PdGUIParser import PdGUIParser
from hvcc.types.compiler import CompilerResp, CompilerNotif, CompilerMsg


class Colours:
    purple = "\033[95m"
    cyan = "\033[96m"
    dark_cyan = "\033[36m"
    blue = "\033[94m"
    green = "\033[92m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold = "\033[1m"
    underline = "\033[4m"
    end = "\033[0m"


class pd2gui:

    @classmethod
    def compile(
        cls,
        pd_path: Path,
        ir_file: Path,
        search_paths: Optional[list] = None,
        verbose: bool = False
    ):
        tick = time.time()

        parser = PdGUIParser()
        if search_paths is not None:
            for p in search_paths:
                parser.add_absolute_search_directory(p)

        try:
            gui_graph, _ = parser.gui_from_file(pd_path)

            ir_dir = ir_file.parent
            if not ir_dir.exists():
                Path.mkdir(ir_dir)

            with open(ir_file, "w") as f:
                f.write(gui_graph.model_dump_json(indent=2) + "\n")

            return CompilerResp(
                stage="pd2gui",
                notifs=CompilerNotif(),
                in_dir=pd_path.parent,
                in_file=pd_path,
                out_dir=ir_dir,
                out_file=ir_file,
                compile_time=(time.time() - tick)
            )
        except Exception as e:
            return CompilerResp(
                stage="pd2gui",
                notifs=CompilerNotif(
                    has_error=True,
                    exception=e,
                    errors=[CompilerMsg(
                        enum=NotificationEnum.ERROR_EXCEPTION,
                        message=str(e)
                    )]
                ),
                compile_time=(time.time() - tick)
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converts a Pd patch into the GUI format.")
    parser.add_argument(
        "pd_path",
        help="The Pd patch to convert to GUI.")
    parser.add_argument(
        "ir_dir",
        help="Directory to store generated GUI patches.")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show debugging information.",
        action="count")
    args = parser.parse_args()

    pd_path = Path(args.pd_path).expanduser().absolute()
    ir_dir = Path(args.ir_dir).expanduser().absolute()

    pd2gui.compile(
        pd_path=pd_path,
        ir_file=Path(ir_dir, f"{pd_path.stem}.heavy.gui.json"),
        search_paths=None,
        verbose=args.verbose)


if __name__ == "__main__":
    main()
