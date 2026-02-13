# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import os

from typing import Generator, Optional, Union

from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.types.GUI import (
    Size, Coords, Font, LabelShow, LabelPos, Label, Color, Canvas,
    Bang, Toggle, VRadio, HRadio, VSlider, HSlider, Knob,  Number, Float,
    Comment, GUIObjects, Graph, GraphRoot
)


class PdGUIParser(PdParser):
    def __init__(self) -> None:
        # the current global value of $0
        # Note(joe): set a high starting value to avoid potential user naming conflicts
        self.__DOLLAR_ZERO = 1000

        # search paths at this graph level
        self.search_paths: list[str] = []

    def gui_from_file(
        self,
        file_path: str,
        obj_args: Optional[list] = None,
        is_root: bool = True
    ) -> tuple[Union[Graph, GraphRoot], bool]:
        if is_root:
            self.search_paths.append(os.path.dirname(file_path))

        file_iterator = self.get_pd_line(file_path)
        canvas_line: str = file_iterator.__next__()

        self.__DOLLAR_ZERO += 1  # increment $0
        graph_args = [self.__DOLLAR_ZERO] + (obj_args or [])

        if not canvas_line.startswith("#N canvas"):
            raise Exception(f"Pd files must begin with \"#N canvas\": {canvas_line}")

        g, gop = self.gui_from_canvas(
            file_iterator,
            canvas_line,
            graph_args,
            file_path,
            is_root
        )

        return g, gop

    def gui_from_canvas(
        self,
        file_iterator: Generator,
        canvas_line: str,
        graph_args: list,
        pd_path: str,
        is_root: bool = False
    ) -> tuple[Union[Graph, GraphRoot], bool]:

        objects: list[GUIObjects] = []
        graphs: list[Graph] = []
        x: Optional[GUIObjects] = None

        # graph on parent settings
        gop: bool = False
        gop_start: Coords = Coords()
        gop_size: Size = Size()
        obj_type = ""
        obj_args = []

        try:
            for li in file_iterator:
                line = self.split_line(li)

                if line[0] == "#N":
                    if line[1] == "canvas":
                        g, gop = self.gui_from_canvas(
                            file_iterator=file_iterator,
                            canvas_line=li,
                            graph_args=graph_args,
                            pd_path=pd_path
                        )
                        if gop:
                            assert isinstance(g, Graph)
                            graphs.append(g)

                elif line[0] == "#X":
                    if line[1] == "coords":
                        try:
                            if int(line[8]) > 0:
                                # canvas is active
                                gop = True
                                gop_start = Coords(x=int(line[9]), y=int(line[10]))
                                gop_size = Size(x=int(line[6]), y=int(line[7]))
                        except IndexError:
                            continue

                    elif line[1] == "restore" and gop:
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
                        x = self.add_comment(line)

                    elif line[1] == "floatatom":
                        obj_args = self.__resolve_object_args(
                            obj_args=line[1:],
                            graph_args=graph_args,
                            is_root=is_root
                        )

                        # replace args with resolved args
                        line = line[:1] + obj_args
                        x = self.add_float(line)

                    elif line[1] == "obj":
                        if len(line) > 4:
                            obj_type = line[4]
                            # sometimes objects have $ arguments in them as well
                            obj_type = self.__resolve_object_args(
                                obj_args=[obj_type],
                                graph_args=graph_args,
                                is_root=is_root)[0]
                            obj_args = self.__resolve_object_args(
                                obj_args=line[5:],
                                graph_args=graph_args,
                                is_root=is_root
                            )

                            # replace args with resolved args
                            line = line[:5] + obj_args

                        abs_path = self.find_abstraction_path(os.path.dirname(pd_path), obj_type)

                        if abs_path is not None:
                            g, gop = self.gui_from_file(abs_path, obj_args=obj_args, is_root=False)

                            if gop:
                                assert isinstance(g, Graph)
                                # set object coordinates
                                g.position = Coords(
                                    x=int(line[2]),
                                    y=int(line[3])
                                )
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
                        elif obj_type == "nbx":
                            x = self.add_number(line)

                    if x is not None:
                        objects.append(x)
                        x = None

        except Exception as e:
            raise e

        if is_root:
            line = self.split_line(canvas_line)

            gop_start = Coords(x=0, y=0)
            gop_size = Size(
                x=int(line[4]),
                y=int(line[5])
            )

            objects = self.filter_invisible_objects(objects, gop_start, gop_size)
            graphs = self.filter_invisible_graphs(graphs, gop_start, gop_size)

            return GraphRoot(
                size=gop_size,
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
            if cls.graph_is_empty(g):
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
    def graph_is_empty(cls, graph: Graph) -> bool:
        """ A graph is considered empty when it doesn't have any objects
            and all of it's child graphs are also empty.
        """
        g_empty: list[bool] = []

        for g in graph.graphs:
            g_empty.append(cls.graph_is_empty(g))

        return len(graph.objects) == 0 and (
            (len(g_empty) and all(g_empty)) or len(graph.graphs) == 0
        )

    @classmethod
    def filter_params(cls, param: str) -> Optional[str]:
        """ Only allow externed parameters
        """

        if "@hv_param" in param:
            return param.split(" ")[0]
        else:
            return None

    @classmethod
    def __resolve_object_args(
        cls,
        obj_args: list,
        graph_args: list,
        raise_on_failure: bool = True,
        is_root: bool = False
    ) -> list:
        """ Resolve object arguments against the given graph arguments.
            By default this function raises an Exception if it cannot resolve an
            argument.
            This behaviour may be disabled, in which case the unresolved argument
            is replaced with None (which is an otherwise invalid value). A value of
            None typically indicates to a HeavyObject that the default value
            may be used.
        """
        resolved_obj_args = list(obj_args)  # make a copy of the original obj_args
        for i, a in enumerate(obj_args):
            for m in set(cls.RE_DOLLAR.findall(a)):
                assert isinstance(a, str)
                x = int(m)  # the dollar index (i.e. $x)
                if len(graph_args) > x:
                    a = a.replace(fr"\${m}", str(graph_args[x]))

                elif is_root:
                    # NOTE(mhroth): this case is questionable, but since Pd
                    # defaults to this behavior without warning, so will we.
                    a = a.replace(fr"\${m}", "0")

                else:
                    if raise_on_failure:
                        # NOTE(mhroth): this case is questionable, but since Pd
                        # defaults to this behavior without warning, so will we.
                        a = a.replace(fr"\${m}", "0")
                    else:
                        a = None  # indicate that this argument could not be resolved by replacing it with None
            resolved_obj_args[i] = a
        return resolved_obj_args

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

    @classmethod
    def add_number(cls, line: list[str]) -> Optional[Number]:
        param = cls.filter_params(line[12])
        if param is None:
            return None

        label = Label(
            text=line[13],
            color=Color(line[20]),
            position=Coords(
                x=int(line[14]),
                y=int(line[15])
            ),
            font=Font(0),
            font_size=int(line[17])
        ) if line[13] != "empty" else None

        return Number(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[5])*int(line[17]),
                y=int(line[6])
            ),
            parameter=param,
            label=label,
            bg_color=Color(line[18]),
            fg_color=Color(line[19]),
            log_mode=bool(int(line[9])),
            log_height=int(line[21])
        )

    @classmethod
    def add_comment(cls, line: list[str]) -> Comment:
        text = " ".join(line[4:])
        return Comment(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            text=text,
            size=Size(
                x=10*len(text), y=10
            )
        )

    @classmethod
    def add_float(cls, line: list[str]) -> Optional[Float]:
        param = cls.filter_params(line[9])
        if param is None:
            return None

        return Float(
            position=Coords(
                x=int(line[2]),
                y=int(line[3])
            ),
            size=Size(
                x=int(line[4]) * int(line[11]),
                y=int(line[11])
            ),
            parameter=param,
            label_text=line[8],
            font_size=int(line[11]),
            label_pos=LabelPos(int(line[7])),
            min=float(line[5]),
            max=float(line[6])
        )
