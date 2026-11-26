# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import re
from enum import IntEnum
from typing import Literal

from pydantic import BaseModel, model_validator

DPFFormats = Literal['lv2', 'lv2_sep', 'vst2', 'vst3', 'clap', 'jack', 'dssi', 'ladspa', 'au']
DPFPortGroupConfig = dict[str, int | tuple[int, bool]]


def slugify(value: str) -> str:
    """Used for cleaning up portgroup names by replacing invalid characters with underscores"""
    return re.sub(r'[^A-Za-z0-9_]+', '_', str(value)).strip('_')


class DPFUISize(BaseModel):
    width: int
    height: int


class DPFUIType(IntEnum):
    NONE = 0
    IMGUI = 1
    NANOVG = 2


class DPFPortGroups(BaseModel):
    input: dict[str, DPFPortGroupConfig] = {}
    output: dict[str, DPFPortGroupConfig] = {}
    params: dict[str, list[str]] = {}

    @model_validator(mode='after')
    def check_groups(self) -> 'DPFPortGroups':
        # a parameter may only belong to a single group
        seen: dict[str, str] = {}

        for group, params in self.params.items():
            for param in params:
                if param in seen:
                    raise ValueError(f"Parameter '{param}' belongs to multiple groups: '{seen[param]}' and '{group}'")
                seen[param] = group

        # group names must be unique across input/output/params,
        # since they all become entries of the same PortGroups enum
        names = list(self.input) + list(self.output) + list(self.params)
        reserved = {"Count", "Mono", "Stereo"}
        for name in names:
            if slugify(name) in reserved:
                raise ValueError(f"Port group name '{name}' is reserved and cannot be used")

        symbols = [slugify(name).lower() for name in names]
        dups = {symbol for symbol in symbols if symbols.count(symbol) > 1}
        if dups:
            raise ValueError(f"Port group symbols(s) used more than once: {', '.join(sorted(dups))}")

        # a port index may only appear once per direction
        for direction in (self.input, self.output):
            iseen: dict[int, str] = {}
            for group, gConfig in direction.items():
                for port, value in gConfig.items():
                    index = value[0] if isinstance(value, (tuple, list)) else value
                    if not isinstance(index, int):
                        raise ValueError(  # noqa: TRY004
                            f"Port index for port '{port}' in group '{group}' must be an integer")
                    if index < 1:
                        raise ValueError(f"port index must start at 1 (PD numbering), got {index} in group '{group}'")
                    if index in iseen:
                        raise ValueError(
                            f"Port index '{index}' in group '{group}' is already used by group '{iseen[index]}'"
                        )
                    iseen[index] = group

        return self
