# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from enum import IntEnum
from typing import Literal, Optional, Union

from pydantic import BaseModel
from pydantic_extra_types.color import Color


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


class Base(BaseModel):
    type: str
    position: Coords
    size: Size


class BaseParam(Base):
    parameter: str


class Label(BaseModel):
    text: str
    position: Coords
    color: Color
    font: Font
    font_size: int


class Comment(Base):
    type: Literal["comment"] = "comment"
    text: str


class Canvas(Base):
    type: Literal["canvas"] = "canvas"
    label: Optional[Label] = None
    bg_color: Color


class Bang(BaseParam):
    type: Literal["bang"] = "bang"
    label: Optional[Label] = None
    fg_color: Color
    bg_color: Color


class Toggle(BaseParam):
    type: Literal["toggle"] = "toggle"
    label: Optional[Label] = None
    fg_color: Color
    bg_color: Color
    non_zero: float


class Radio(BaseParam):
    label: Optional[Label] = None
    fg_color: Color
    bg_color: Color
    options: int


class VRadio(Radio):
    type: Literal["vradio"] = "vradio"


class HRadio(Radio):
    type: Literal["hradio"] = "hradio"


class Slider(BaseParam):
    label: Optional[Label] = None
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
    label_show: Literal["n", "a", "wa", "wt"]
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
    read_only: bool
    jump: bool
    variable: str
    parameter: str
    square: bool
    arc: Color
    arc_start: float
    arc_show: bool


class Number(BaseParam):
    type: Literal["number"] = "number"
    label: Optional[Label] = None
    fg_color: Color
    bg_color: Color


class Float(BaseParam):
    type: Literal["float"] = "float"
    label_text: str
    label_height: int
    label_pos: Literal["l", "r", "t", "b"]
    min: float
    max: float


GUIObjects = Union[Bang, Toggle, Radio, Slider, Knob, Number, Float, Comment, Canvas]


class GraphBase(BaseModel):
    objects: list[GUIObjects]


class Graph(GraphBase):
    position: Coords
    gop_start: Coords
    gop_size: Size
    graphs: list["Graph"]


class GraphRoot(GraphBase):
    width: int
    height: int
    graphs: list["Graph"]
