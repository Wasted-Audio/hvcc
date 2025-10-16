# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import Literal

from pydantic import BaseModel
from pydantic_extra_types.color import Color


class Coords(BaseModel):
    x: int = 0
    y: int = 0


class Size(BaseModel):
    x: int = 0
    y: int = 0


class Base(BaseModel):
    type: str
    position: Coords


class BaseParam(Base):
    parameter: str


class Label(BaseModel):
    type: str = "label"
    text: str
    color: int
    pos: Coords
    height: int


class Bang(BaseParam):
    type: str = "bang"
    label: Label
    size: int
    fg_color: Color
    bg_color: Color


class Toggle(BaseParam):
    type: str = "toggle"
    label: Label
    size: int
    fg_color: Color
    bg_color: Color
    non_zero: float


class Radio(BaseParam):
    label: Label
    size: int
    fg_color: Color
    bg_color: Color
    options: int


class VRadio(Radio):
    type: str = "vradio"


class HRadio(Radio):
    type: str = "hradio"


class Slider(BaseParam):
    label: Label
    size: Coords
    min: float
    max: float
    fg_color: Color
    bg_color: Color
    logarithmic: bool
    steady: bool


class VSlider(Slider):
    type: str = "vslider"


class HSlider(Slider):
    type: str = "hslider"


class Knob(BaseParam):
    type: str = "knob"
    label_size: int
    label_pos: Size
    label_show: Literal["n", "a", "wa", "wt"]
    size: int
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
    type: str = "number"
    label: Label
    width: int
    fg_color: Color
    bg_color: Color


class Float(BaseParam):
    type: str = "float"
    label_text: str
    label_height: int
    label_pos: Literal["l", "r", "t", "b"]
    size: int
    min: float
    max: float


class Comment(Base):
    type: str = "comment"
    text: str


class Canvas(Base):
    type: str = "canvas"
    label: Label
    size: Size
    bg_color: Color


GUIObjects = Bang | Toggle | Radio | Slider | Knob | Number | Float | Comment | Canvas


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
