# Heavy Compiler Collection
# Copyright (C) 2025 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import List, Literal, Union, Tuple

from pydantic import BaseModel
from pydantic_extra_types.color import Color


class Coords(BaseModel):
    x: int
    y: int


class Size(BaseModel):
    x: int
    y: int


class Base(BaseModel):
    position: Coords


class Label(BaseModel):
    text: str
    color: int
    pos: Coords
    height: int


class Bang(Base):
    label: Label
    size: int
    fg_color: Color
    bg_color: Color


class Toggle(Base):
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
    type: str = "v"


class HRadio(Radio):
    type: str = "h"


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
    type: str = "v"


class HSlider(Slider):
    type: str = "h"


class Knob(Base):
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
    label: Label
    width: int
    fg_color: Color
    bg_color: Color


class Float(Base):
    label_text: str
    label_height: int
    label_pos: Literal["l", "r", "t", "b"]
    size: int
    min: float
    max: float


class Comment(Base):
    text: str


class Canvas(Base):
    label: Label
    size: Size
    bg_color: Color


class GraphBase(BaseModel):
    width: int
    height: int
    hide_name_args: bool
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]
    objects: List[Union[Bang, Toggle, Radio, Slider, Knob, Number, Float, Comment, Canvas]]


class Graph(GraphBase):
    pos: Coords
    graphs: List["Graph"]


class GraphTop(GraphBase):
    graphs: List["Graph"]
