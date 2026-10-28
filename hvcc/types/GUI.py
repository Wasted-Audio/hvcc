# Heavy Compiler Collection
# Copyright (C) 2025-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from enum import IntEnum
from typing import Literal

from pydantic import BaseModel
from pydantic_extra_types.color import Color

from hvcc.version import VERSION


class Coords(BaseModel):
    x: int = 0
    y: int = 0


class Size(BaseModel):
    x: int = 0
    y: int = 0


class Font(IntEnum):
    courier = 0
    helvetica = 1
    times = 2


class LabelShow(IntEnum):
    never = 0
    always = 1
    active = 2
    typing = 3


class LabelPos(IntEnum):
    left = 0
    right = 1
    top = 2
    bottom = 3


class Base(BaseModel):
    type: str
    position: Coords
    size: Size


class BaseUI(Base):
    id: str = ""


class BaseParam(Base):
    parameter: str
    send: bool = False


class Label(BaseModel):
    text: str
    position: Coords
    color: Color
    font: Font
    font_size: int


class Comment(BaseUI):
    type: Literal["comment"] = "comment"
    text: str
    width: int | None = 0


class Canvas(BaseUI):
    type: Literal["canvas"] = "canvas"
    label: Label | None = None
    bg_color: Color


class Bang(BaseParam):
    type: Literal["bang"] = "bang"
    label: Label | None = None
    flash_time: int
    fg_color: Color
    bg_color: Color


class Toggle(BaseParam):
    type: Literal["toggle"] = "toggle"
    label: Label | None = None
    fg_color: Color
    bg_color: Color
    non_zero: float


class Radio(BaseParam):
    label: Label | None = None
    fg_color: Color
    bg_color: Color
    options: int


class VRadio(Radio):
    type: Literal["vradio"] = "vradio"


class HRadio(Radio):
    type: Literal["hradio"] = "hradio"


class Slider(BaseParam):
    label: Label | None = None
    min: float
    max: float
    fg_color: Color
    bg_color: Color
    logarithmic: bool
    steady: bool


class VSlider(Slider):
    type: Literal["vslider"] = "vslider"


class HSlider(Slider):
    type: Literal["hslider"] = "hslider"


class Knob(BaseParam):
    type: Literal["knob"] = "knob"
    label_size: int
    label_pos: Coords
    label_show: LabelShow
    min: float
    max: float
    fg_color: Color
    bg_color: Color
    init_val: float
    ang_range: int
    ang_offset: int
    log_mode: Literal["lin", "log", "exp"]
    exp_fact: float
    discrete: bool
    ticks: bool
    steps: int
    circular: bool
    jump: bool
    square: bool
    arc_color: Color
    arc_start: float
    arc_show: bool


class Number(BaseParam):
    type: Literal["number"] = "number"
    label: Label | None = None
    fg_color: Color
    bg_color: Color
    log_mode: bool
    log_height: int
    min: float
    max: float


class Float(BaseParam):
    type: Literal["float"] = "float"
    font_height: int
    label_text: str
    label_pos: LabelPos
    min: float
    max: float


class Popmenu(BaseParam):
    type: Literal["popmenu"] = "popmenu"
    font_height: int
    no_select: str
    fg_color: Color
    bg_color: Color
    options: list[str]


GUIObjects = Bang | Toggle | Radio | Slider | Knob | Number | Float | Comment | Canvas | Popmenu


class Theme(BaseModel):
    obj_corner_radius: float | None = None
    cnv_color: Color | None = None
    cnv_txt_color: Color | None = None
    io_color: Color | None = None
    bg_color: Color | None = None
    sel_color: Color | None = None
    com_txt_color: Color | None = None
    out_color: Color | None = None


class GraphBase(BaseModel):
    id: str = "mainPatch"
    objects: list[GUIObjects]
    graphs: list["Graph"]


class Graph(GraphBase):
    position: Coords
    gop_start: Coords
    gop_size: Size


class GraphRoot(GraphBase):
    size: Size
    theme: Theme | None = Theme()
    version: str = VERSION
