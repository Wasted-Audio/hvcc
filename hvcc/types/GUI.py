# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import Literal

from pydantic import BaseModel
from pydantic_extra_types.color import Color


class Coords(BaseModel):
    x: int
    y: int


class Size(BaseModel):
    x: int
    y: int


class Base(BaseModel):
    type: str
    position: Coords


class Label(BaseModel):
    type: str = "label"
    text: str
    color: int
    pos: Coords
    height: int


class Bang(Base):
    type: str = "bang"
    label: Label
    size: int
    fg_color: Color
    bg_color: Color


class Toggle(Base):
    type: str = "toggle"
    label: Label
    size: int
    fg_color: Color
    bg_color: Color
    non_zero: float


class Radio(Base):
    label: Label
    size: int
    fg_color: Color
    bg_color: Color
    options: int


class VRadio(Radio):
    type: str = "vradio"


class HRadio(Radio):
    type: str = "hradio"


class Slider(Base):
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


class Knob(Base):
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


class Number(Base):
    type: str = "number"
    label: Label
    width: int
    fg_color: Color
    bg_color: Color


class Float(Base):
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


class GraphBase(BaseModel):
    width: int
    height: int
    objects: list[Bang | Toggle | Radio | Slider | Knob | Number | Float | Comment | Canvas]


class Graph(GraphBase):
    x_range: tuple[float, float]
    y_range: tuple[float, float]
    position: Coords
    graphs: list["Graph"]


class GraphTop(GraphBase):
    graphs: list["Graph"]
