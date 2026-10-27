# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import re
from enum import IntEnum
from typing import Literal

from pydantic import BaseModel, HttpUrl, model_validator

from hvcc.types.GUI import Theme

DaisyBoards = Literal['pod', 'petal', 'patch', 'patch_init', 'field']
DaisyBootloader = Literal['BOOT_NONE', 'BOOT_SRAM', 'BOOT_QSPI']
DPFFormats = Literal['lv2', 'lv2_sep', 'vst2', 'vst3', 'clap', 'jack', 'dssi', 'ladspa', 'au']

DPFPortGroupConfig = dict[str, int | tuple[int, bool]]


def slugify(value: str) -> str:
    """Used for cleaning up portgroup names by replacing invalid characters with underscores"""
    return re.sub(r'[^A-Za-z0-9_]+', '_', str(value)).strip('_')


class Daisy(BaseModel):
    board:          DaisyBoards = 'pod'
    board_file:     str | None = None
    libdaisy_path:  str | int = 2
    usb_midi:       bool = False
    debug_printing: bool = False
    samplerate:     int = 48000
    blocksize:      int | None = None
    linker_script:  str = ''
    bootloader:     DaisyBootloader | None = None


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


class DPF(BaseModel):
    dpf_path:           str = ""
    description:        str | None = None
    makefile_dep:       list[str] = []
    enable_ui:          DPFUIType | None = DPFUIType.NONE
    enable_modgui:      bool = False
    ui_size:            DPFUISize | None = None
    ui_theme_set:       bool = False
    ui_theme:           str | None = None
    ui_themes:          dict[str, Theme] | None = None
    midi_input:         bool = False
    midi_output:        bool = False
    port_groups:        DPFPortGroups | None = None
    enumerators:        dict[str, list[str]] | None = None
    denormals:          bool = True
    version:            str | None = None
    license:            str | None = None
    maker:              str | None = None
    brand_id:           str | None = None
    brand_id_no_vst3:   bool | None = False
    unique_id:          str | None = None
    homepage:           HttpUrl | None = None
    plugin_uri:         str | None = None
    plugin_clap_id:     str | None = None
    plugin_formats:     list[DPFFormats] = []
    lv2_info:           str | None = None
    vst3_info:          str | None = None
    clap_info:          list[str] = []

    @model_validator(mode='after')
    def au_required(self) -> 'DPF':
        if 'au' in self.plugin_formats:
            if self.brand_id is None:
                raise ValueError("brand_id is required for au plugins")
            if self.unique_id is None:
                raise ValueError("unique_id is required for au plugins")
        return self


class Meta(BaseModel):
    name: str | None = None
    nosimd: bool | None = False
    daisy: Daisy = Daisy()
    dpf: DPF = DPF()
    external: dict | None = None
