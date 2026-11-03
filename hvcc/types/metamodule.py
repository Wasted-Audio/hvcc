# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_extra_types.color import Color


class XY(BaseModel):
    x: int | None = None
    y: int | None = None

    @model_validator(mode='after')
    def validate_xy(self) -> 'XY':
        if self.x is None and self.y is None:
            return self
        if self.x is None or self.y is None:
            raise ValueError('Both x and y must be specified')
        return self


class Knob(XY, BaseModel):
    param: str
    image: Path = Field(default=Path(__file__).parent / '../generators/c2meta/assets/knob.png')


class Jack(XY, BaseModel):
    id: int
    name: str | None = None
    image: Path = Field(default=Path(__file__).parent / '../generators/c2meta/assets/jack.png')


class Input(Jack):
    pass


class Output(Jack):
    pass


class Led(XY, BaseModel):
    led: str
    image: Path = Field(default=Path(__file__).parent / '../generators/c2meta/assets/led.png')


class Panel(XY, BaseModel):
    image: Path | None = None
    color: Color | None = None

    @field_validator('y', mode='before')
    def validate_size_y(cls, y: int | None) -> int | None:
        if y is not None and (y != 240):
            raise ValueError('Panel height must be 240 pixels')
        return y


class Assets(BaseModel):
    panel: Panel | None = None
    knobs: list[Knob] = []
    inputs: list[Input] = []
    outputs: list[Output] = []
    leds: list[Led] = []

    @model_validator(mode='after')
    def check_ports(self) -> 'Assets':
        def _probe_jack_ids(ports: list[Input] | list[Output]) -> None:
            ids: list[int] = []
            for port in ports:
                if port.id < 1:
                    raise ValueError('Jack index must start at 1 (PD numbering)')
                if port.id in ids:
                    raise ValueError(f"Jack index '{port.id}' used more than once")
                ids.append(port.id)

        _probe_jack_ids(self.inputs)
        _probe_jack_ids(self.outputs)

        return self


UIElement = Knob | Input | Output| Led
