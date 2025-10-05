# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import Dict, Literal, List, Optional, Tuple, Union
from typing_extensions import Self
from pydantic import BaseModel, HttpUrl, model_validator


DaisyBoards = Literal['pod', 'petal', 'patch', 'patch_init', 'field']
DaisyBootloader = Literal['BOOT_NONE', 'BOOT_SRAM', 'BOOT_QSPI']
DPFFormats = Literal['lv2', 'lv2_sep', 'vst2', 'vst3', 'clap', 'jack', 'dssi', 'ladspa', 'au']


class Daisy(BaseModel):
    board:          DaisyBoards = 'pod'
    board_file:     Optional[str] = None
    libdaisy_path:  Union[str, int] = 2
    usb_midi:       bool = False
    debug_printing: bool = False
    samplerate:     int = 48000
    blocksize:      Optional[int] = None
    linker_script:  str = ''
    bootloader:     Optional[DaisyBootloader] = None


class DPFUISize(BaseModel):
    width: int
    height: int


class DPFPortGroups(BaseModel):
    input: Dict[str, Dict[str, Union[int, Tuple[int, bool]]]] = {}
    output: Dict[str, Dict[str, Union[int, Tuple[int, bool]]]] = {}


class DPF(BaseModel):
    dpf_path:           str = ""
    description:        Optional[str] = None
    makefile_dep:       List[str] = []
    enable_ui:          bool = False
    enable_modgui:      bool = False
    ui_size:            Optional[DPFUISize] = None
    midi_input:         bool = False
    midi_output:        bool = False
    port_groups:        Optional[DPFPortGroups] = None
    enumerators:        Optional[Dict[str, List[str]]] = None
    denormals:          bool = True
    version:            Optional[str] = None
    license:            Optional[str] = None
    maker:              Optional[str] = None
    brand_id:           Optional[str] = None
    brand_id_no_vst3:   Optional[bool] = False
    unique_id:          Optional[str] = None
    homepage:           Optional[HttpUrl] = None
    plugin_uri:         Optional[str] = None
    plugin_clap_id:     Optional[str] = None
    plugin_formats:     List[DPFFormats] = []
    lv2_info:           Optional[str] = None
    vst3_info:          Optional[str] = None
    clap_info:          List[str] = []

    @model_validator(mode='after')
    def au_required(self) -> Self:
        if 'au' in self.plugin_formats:
            if self.brand_id is None:
                raise ValueError("brand_id is required for au plugins")
            if self.unique_id is  None:
                raise ValueError("unique_id is required for au plugins")
        return self


class Meta(BaseModel):
    name: Optional[str] = None
    nosimd: Optional[bool] = False
    daisy: Daisy = Daisy()
    dpf: DPF = DPF()
    external: Optional[Dict] = None
