# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import os
import time

from typing import Optional

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
        pd_path: str,
        ir_dir: str,
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

            if not os.path.exists(ir_dir):
                os.makedirs(ir_dir)

            gui_file = f"{os.path.splitext(os.path.basename(pd_path))[0]}.gui.json"
            gui_path = os.path.join(ir_dir, gui_file)
            with open(gui_path, "w") as f:
                f.write(gui_graph.model_dump_json(indent=2) + "\n")

            return CompilerResp(
                stage="pd2gui",
                notifs=CompilerNotif(),
                in_dir=os.path.dirname(pd_path),
                in_file=os.path.basename(pd_path),
                out_dir=ir_dir,
                out_file=gui_file,
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

    args.pd_path = os.path.abspath(os.path.expanduser(args.pd_path))
    args.ir_dir = os.path.abspath(os.path.expanduser(args.ir_dir))

    pd2gui.compile(
        pd_path=args.pd_path,
        ir_dir=args.ir_dir,
        search_paths=None,
        verbose=args.verbose)


if __name__ == "__main__":
    main()
