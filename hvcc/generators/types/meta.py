from typing import Dict, Literal, List, Optional
from pydantic import BaseModel, HttpUrl


DPFFormats = Literal['lv2', 'lv2_sep', 'vst2', 'vst3', 'clap', 'jack', 'dssi', 'ladspa']


class DPFUISize(BaseModel):
    width: int
    height: int


class DPFPortGroups(BaseModel):
    input: Dict[str, Dict[str, int]] = {}
    output: Dict[str, Dict[str, int]] = {}


class DPF(BaseModel):
    dpf_path:       Optional[str] = ""
    description:    Optional[str] = None
    makefile_dep:   List[str] = []
    enable_ui:      Optional[bool] = False
    enable_modgui:  Optional[bool] = False
    ui_size:        Optional[DPFUISize] = None
    midi_input:     Optional[bool] = None
    midi_output:    Optional[bool] = None
    port_groups:    Optional[DPFPortGroups] = None
    enumerators:    Optional[Dict[str, List[str]]] = None
    version:        Optional[str] = None
    license:        Optional[str] = None
    maker:          Optional[str] = None
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
