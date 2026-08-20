# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.color import Color


class XY(BaseModel):
    x: int
    y: int


class Coords(XY):
    pass


class Size(XY):
    pass


class Knob(BaseModel):
    param: str
    coords: Optional[Coords] = None
    image: Path = Field(default=Path(__file__).parent / 'assets/knob.png')


class Jack(BaseModel):
    id: int
    name: Optional[str] = None
    coords: Optional[Coords] = None
    image: Path = Field(default=Path(__file__).parent / 'assets/jack.png')


class Input(Jack):
    pass


class Output(Jack):
    pass


class Led(BaseModel):
    led: str
    coords: Optional[Coords] = None
    image: Path = Field(default=Path(__file__).parent / 'assets/led.png')


class Panel(BaseModel):
    image: Optional[Path] = None
    size: Optional[Size] = None
    color: Optional[Color] = None

    @field_validator('size', mode='before')
    def validate_size(cls, v):
        if v is not None and (v.y != 240):
            raise ValueError('Panel height must be 240 pixels')
        return v

class Assets(BaseModel):
    panel: Optional[Panel] = None
    knobs: list[Knob] = []
    inputs: list[Input] = []
    outputs: list[Output] = []
    leds: list[Led] = []


UIElement = Union[Knob, Input, Output, Led]
