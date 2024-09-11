from typing import Dict, Literal, List, Optional
from pydantic import BaseModel, Field, HttpUrl


DPFFormats = Literal['lv2', 'lv2_sep', 'vst2', 'vst3', 'clap', 'jack', 'dssi', 'ladspa']

class DPFUISize(BaseModel):
    width: int
    height: int


class DPFPortGroups(BaseModel):
    input: Dict[str, Dict[str, int]] = {}
    output: Dict[str, Dict[str, int]] = {}


class DPF(BaseModel):
    dpf_path:       Optional[str] = None
    description:    Optional[str] = None
    makefile_dep:   List[str] = []
    enable_ui:      bool = False
    ui_size:        Optional[DPFUISize] = None
    midi_input:     Optional[bool] = None
    midi_output:    Optional[bool] = None
    port_groups:    Optional[DPFPortGroups] = None
    version:        Optional[str] = None
    license:        Optional[str] = None
    homepage:       Optional[HttpUrl] = None
    plugin_uri:     Optional[str] = None
    plugin_clap_id: Optional[str] = None
    plugin_formats: List[DPFFormats] = []
    lv2_info:       Optional[str] = None
    vst3_info:      Optional[str] = None
    clap_info:      List[str] = []


class Meta(BaseModel):
    name: Optional[str] = None
    dpf: DPF = DPF()