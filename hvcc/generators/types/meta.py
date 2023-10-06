from typing import Dict, Literal, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class DPFUISize(BaseModel):
    width: int
    height: int


class DPFPortGroups(BaseModel):
    input: Optional[Dict[str, Dict[str, int]]]
    output: Optional[Dict[str, Dict[str, int]]]


class DPF(BaseModel):
    dpf_path:       Optional[str]
    makefile_dep:   Optional[List[str]]
    enable_ui:      Optional[bool]
    ui_size:        Optional[DPFUISize]
    midi_input:     Optional[bool]
    midi_output:    Optional[bool]
    port_groups:    Optional[DPFPortGroups]
    version:        Optional[str]
    license:        Optional[str]
    homepage:       Optional[HttpUrl]
    plugin_uri:     Optional[str]
    plugin_clap_id: Optional[str]
    plugin_formats: Optional[List[Literal['lv2', 'lv2_sep', 'vst2', 'vst3', 'clap', 'jack']]]
    lv2_info:       Optional[str]
    vst3_info:      Optional[str]
    clap_info:      Optional[List[str]]


class Meta(BaseModel):
    name: Optional[str]
    dpf: Optional[DPF]