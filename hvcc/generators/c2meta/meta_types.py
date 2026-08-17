# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field


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
    image: Path = Field(default=Path(Path(__file__).parent, 'assets/knob.png'))


class Jack(BaseModel):
    id: int
    coords: Optional[Coords] = None
    image: Path = Field(default=Path(Path(__file__).parent, 'assets/jack.png'))


class Input(Jack):
    pass


class Output(Jack):
    pass


class Led(BaseModel):
    led: str
    coords: Optional[Coords] = None
    image: Path = Field(default=Path(Path(__file__).parent, 'assets/led.png'))


class Panel(BaseModel):
    image: Optional[Path] = None
    size: Optional[Size] = None


class Assets(BaseModel):
    panel: Optional[Panel] = None
    knobs: list[Knob] = []
    inputs: list[Input] = []
    outputs: list[Output] = []
    leds: list[Led] = []


UIElement = Union[Knob, Input, Output, Led]
