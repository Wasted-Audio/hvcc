# Heavy Compiler Collection
# Copyright (C) 2024-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import Literal

from pydantic import BaseModel, HttpUrl, model_validator

from hvcc.types.dpf import DPFFormats, DPFPortGroups, DPFUISize, DPFUIType
from hvcc.types.GUI import Theme
from hvcc.types.metamodule import Assets

DaisyBoards = Literal[
    'pod', 'petal', 'patch', 'patch_init', 'field',
    'desktop_devkit', 'eurorack_devkit', 'pedal_devkit'
]
DaisyBootloader = Literal['BOOT_NONE', 'BOOT_SRAM', 'BOOT_QSPI']


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


class metaPlugin(BaseModel):
    slug:        str = "module-slug"
    name:        str = "Module Name"
    description: str = "Description of the module"
    tags:        list[str] = []
    assets:      Assets | None = None


class MetaModule(BaseModel):
    sdk_path:    str | None = None
    slug:        str = "plugin-slug"
    name:        str = "Plugin Name"
    version:     str = "1.0.0"
    license:     str = "GPL-3.0-only"
    brand:       str = "Heavy"
    author:      str = "Heavy User"
    email:       str = "developer@wasted.audio"
    url:         str = "https://wasted.audio"
    description: str = "Description of the plugin"
    modules:     list[metaPlugin] = [metaPlugin()]


class Meta(BaseModel):
    name:     str | None = None
    nosimd:   bool | None = False
    daisy:    Daisy = Daisy()
    dpf:      DPF = DPF()
    meta:     MetaModule = MetaModule()
    external: dict | None = None
