# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import os

from typing import Generator, Optional, Union

from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.types.GUI import (
    Size, Coords, Font, LabelShow, Label, Color, Canvas, Bang, Toggle,
    VRadio, HRadio, VSlider, HSlider, Knob,  # Number, Float,
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
    ) -> Union[Graph, GraphRoot]:
        if is_root:
            self.search_paths.append(os.path.dirname(file_path))

        file_iterator = self.get_pd_line(file_path)
        canvas_line: str = file_iterator.__next__()

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
    ) -> tuple[Union[Graph, GraphRoot], bool]:

        objects: list[GUIObjects] = []
        graphs: list[Graph] = []
        x: Optional[GUIObjects]

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
                        # TODO: remove invisible objects
                        objects = self.filter_invisible_objects(objects, gop_start, gop_size)
                        graphs = self.filter_invisible_graphs(graphs, gop_start, gop_size)

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
                        text = " ".join(line[4:])
                        x = Comment(
                            position=Coords(
                                x=int(line[2]),
                                y=int(line[3])
                            ),
                            text=text,
                            size=Size(
                                x=10, y=10*len(text)
                            )
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

                        if obj_type == "cnv":
                            x = self.add_canvas(line)
                        elif obj_type == "bng":
                            x = self.add_bang(line)
                        elif obj_type == "tgl":
                            x = self.add_toggle(line)
                        elif obj_type == "vradio" or obj_type == "hradio":
                            x = self.add_radio(line)
                        elif obj_type == "vsl" or obj_type == "hsl":
                            x = self.add_slider(line)
                        elif obj_type == "knob" or obj_type == "else/knob":
                            x = self.add_knob(line)

                        if x is not None:
                            objects.append(x)

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
            objects = self.filter_invisible_objects(objects, gop_start, gop_size)
            graphs = self.filter_invisible_graphs(graphs, gop_start, gop_size)
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

    @classmethod
    def filter_invisible_objects(
        cls,
        objects: list[GUIObjects],
        gop_start: Coords,
        gop_size: Size
    ) -> list[GUIObjects]:
        filtered_objects: list[GUIObjects] = []
        gop_max_y = gop_start.y + gop_size.y
        gop_max_x = gop_start.x + gop_size.x

        for obj in objects:
            obj_min_y = obj.position.y
            obj_max_y = obj.position.y + obj.size.y
            obj_min_x = obj.position.x
            obj_max_x = obj.position.x + obj.size.x

            # check if object is overlapping with gop
            if ((obj_min_y < gop_max_y) or (obj_min_x < gop_max_x)) and \
                    ((obj_max_y > gop_start.y) and (obj_max_x > gop_start.x)) and \
                    ((obj_min_y < gop_max_y) and (obj_min_x < gop_max_x)):
                filtered_objects.append(obj)

        return filtered_objects

    @classmethod
    def filter_invisible_graphs(
        cls,
        graphs: list[Graph],
        gop_start: Coords,
        gop_size: Size
    ) -> list[Graph]:
        filtered_graphs: list[Graph] = []
        gop_max_y = gop_start.y + gop_size.y
        gop_max_x = gop_start.x + gop_size.x

        for g in graphs:
            # skip empty graphs
            if len(g.objects) == 0:
                continue

            g_min_y = g.position.y
            g_max_y = g.position.y + g.gop_size.y
            g_min_x = g.position.x
            g_max_x = g.position.x + g.gop_size.x

            # check if graph is overlapping with gop
            if ((g_min_y < gop_max_y) or (g_min_x < gop_max_x)) and \
                    ((g_max_y > gop_start.y) and (g_max_x > gop_start.x)) and \
                    ((g_min_y < gop_max_y) and (g_min_x < gop_max_x)):
                filtered_graphs.append(g)

        return filtered_graphs

    @classmethod
    def filter_params(cls, param: str) -> Optional[str]:
        """ Only allow externed parameters
        """

        if "@hv_param" in param:
            return param.split(" ")[0]
        else:
            return None

    @classmethod
    def add_canvas(cls, line: list[str]) -> Canvas:
        label = Label(
            text=line[10],
            color=Color(line[16]),
            position=Coords(
                x=int(line[11]),
                y=int(line[12])
            ),
            font=Font(int(line[13])),
            font_size=int(line[14])
        ) if line[10] != "empty" else None

        return Canvas(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            label=label,
            size=Size(
                x=int(line[6]),
                y=int(line[7])
            ),
            bg_color=Color(line[15])
        )

    @classmethod
    def add_bang(cls, line: list[str]) -> Optional[Bang]:
        param = cls.filter_params(line[10])
        if param is None:
            return None

        label = Label(
            text=line[11],
            color=Color(line[18]),
            position=Coords(
                x=int(line[12]),
                y=int(line[13])
            ),
            font=Font(int(line[14])),
            font_size=int(line[15])
        ) if line[11] != "empty" else None

        return Bang(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[5]),
                y=int(line[5])
            ),
            parameter=param,
            label=label,
            bg_color=Color(line[16]),
            fg_color=Color(line[17])
        )

    @classmethod
    def add_toggle(cls, line: list[str]) -> Optional[Toggle]:
        param = cls.filter_params(line[8])
        if param is None:
            return None

        label = Label(
            text=line[9],
            color=Color(line[16]),
            position=Coords(
                x=int(line[10]),
                y=int(line[11])
            ),
            font=Font(int(line[12])),
            font_size=int(line[13])
        ) if line[9] != "empty" else None

        return Toggle(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[5]),
                y=int(line[5])
            ),
            parameter=param,
            label=label,
            bg_color=Color(line[14]),
            fg_color=Color(line[15]),
            non_zero=float(line[18])
        )

    @classmethod
    def add_radio(cls, line: list[str]) -> Optional[Union[VRadio, HRadio]]:
        param = cls.filter_params(line[10])
        if param is None:
            return None

        radio_type = line[4]

        radio_obj: dict[str, type[Union[VRadio, HRadio]]] = {
            "vradio": VRadio,
            "hradio": HRadio
        }

        label = Label(
            text=line[11],
            color=Color(line[18]),
            position=Coords(
                x=int(line[12]),
                y=int(line[13])
            ),
            font=Font(int(line[14])),
            font_size=int(line[15])
        ) if line[11] != "empty" else None

        return radio_obj[radio_type](
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[5]) * (int(line[8]) if radio_type == "hradio" else 1),
                y=int(line[5]) * (int(line[8]) if radio_type == "vradio" else 1)
            ),
            parameter=param,
            label=label,
            bg_color=Color(line[16]),
            fg_color=Color(line[17]),
            options=int(line[8])
        )

    @classmethod
    def add_slider(cls, line: list[str]) -> Optional[Union[VSlider, HSlider]]:
        param = cls.filter_params(line[12])
        if param is None:
            return None

        slider: dict[str, type[Union[VSlider, HSlider]]] = {
            "vsl": VSlider,
            "hsl": HSlider
        }

        label = Label(
            text=line[13],
            color=Color(line[20]),
            position=Coords(
                x=int(line[14]),
                y=int(line[15])
            ),
            font=Font(int(line[16])),
            font_size=int(line[17])
        ) if line[13] != "empty" else None

        return slider[line[4]](
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[5]),
                y=int(line[6])
            ),
            parameter=param,
            label=label,
            bg_color=Color(line[18]),
            fg_color=Color(line[19]),
            min=float(line[7]),
            max=float(line[8]),
            logarithmic=bool(int(line[9])),
            steady=bool(int(line[22]))
        )

    @classmethod
    def add_knob(cls, line: list[str]) -> Optional[Knob]:
        param = cls.filter_params(line[11])
        if param is None:
            return None

        log_val = float(line[8])

        if log_val == 0.0:
            log_mode = "lin"
        elif log_val == 1.0:
            log_mode = "log"
        else:
            log_mode = "exp"

        return Knob(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[5]),
                y=int(line[5])
            ),
            parameter=param,
            label_size=int(line[27]),
            label_pos=Coords(
                x=int(line[28]),
                y=int(line[29])
            ),
            label_show=LabelShow(int(line[26])),
            min=float(line[6]),
            max=float(line[7]),
            bg_color=Color(line[12]),
            fg_color=Color(line[14]),
            init_val=float(line[9]),
            ang_range=int(line[20]),
            ang_offset=int(line[21]),
            log_mode=log_mode,
            exp_fact=float(line[8]),
            discrete=bool(int(line[18])),
            ticks=bool(int(line[32])),
            steps=int(line[17]),
            circular=bool(int(line[16])),
            jump=bool(0),
            square=bool(int(line[15])),
            arc=Color(line[13]),
            arc_start=float(line[23]),
            arc_show=bool(int(line[19]))
        )
