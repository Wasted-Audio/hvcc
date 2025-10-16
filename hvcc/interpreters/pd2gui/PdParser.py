# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import os

from typing import Generator


from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.types.GUI import (
    Size, Coords,
    # Label, Bang, Toggle, VRadio, HRadio, VSlider, HSlider, Knob, Number, Float, Canvas,
    Comment, GUIObjects, Graph, GraphRoot
)


class PdGUIParser(PdParser):
    def __init__(self):
        # search paths at this graph level
        self.search_paths: list[str] = []

    def gui_from_file(
        self,
        file_path: str,
        is_root: bool = True
    ) -> Graph | GraphRoot:
        if is_root:
            self.search_paths.append(os.path.dirname(file_path))

        file_iterator = self.get_pd_line(file_path)
        canvas_line = file_iterator.__next__()

        if not canvas_line.startswith("#N canvas"):
            raise Exception(f"Pd files must begin with \"#N canvas\": {canvas_line}")

        g, _ = self.gui_from_canvas(
            file_iterator,
            canvas_line,
            file_path,
            is_root
        )

        return g

    def gui_from_canvas(
        self,
        file_iterator: Generator,
        canvas_line: str,
        pd_path: str,
        is_root: bool = False
    ) -> tuple[Graph | GraphRoot, bool]:

        objects: list[GUIObjects] = []
        graphs: list[Graph] = []

        # graph on parent settings
        gop: bool = False
        gop_start: Coords = Coords()
        gop_size: Size = Size()

        try:
            for li in file_iterator:
                line = self.split_line(li)

                if line[0] == "#N":
                    if line[1] == "canvas":
                        g, gop = self.gui_from_canvas(
                            file_iterator=file_iterator,
                            canvas_line=li,
                            pd_path=pd_path
                        )
                        if gop:
                            assert isinstance(g, Graph)
                            graphs.append(g)

                elif line[0] == "#X":
                    if line[1] == "coords":
                        if line[8] == "1":
                            # canvas is active
                            gop = True
                            gop_start = Coords(x=int(line[9]), y=int(line[10]))
                            gop_size = Size(x=int(line[6]), y=int(line[7]))

                    elif line[1] == "restore" and gop:
                        # TODO: remove invisible objects and graphs
                        return Graph(
                            position=Coords(
                                x=int(line[2]),
                                y=int(line[3])
                            ),
                            gop_start=gop_start,
                            gop_size=gop_size,
                            objects=objects,
                            graphs=graphs
                        ), gop

                    elif line[1] == "text":
                        x = Comment(
                            position=Coords(
                                x=int(line[2]),
                                y=int(line[3])
                            ),
                            text=" ".join(line[4:])
                        )
                        objects.append(x)

                    elif line[1] == "obj":
                        if len(line) > 4:
                            obj_type = line[4]

                        abs_path = self.find_abstraction_path(os.path.dirname(pd_path), obj_type)

                        if abs_path is not None:
                            g = self.gui_from_file(abs_path, is_root=False)
                            assert isinstance(g, Graph)
                            graphs.append(g)

        except Exception as e:
            raise e

        if is_root:
            line = self.split_line(canvas_line)

            return GraphRoot(
                width=int(line[4]),
                height=int(line[5]),
                objects=objects,
                graphs=graphs
            ), gop
        else:
            return Graph(
                position=Coords(
                    x=int(line[2]),
                    y=int(line[3])
                ),
                gop_start=gop_start,
                gop_size=gop_size,
                objects=objects,
                graphs=graphs
            ), gop
