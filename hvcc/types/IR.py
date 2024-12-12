# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, RootModel
from typing import Dict, List, Optional, Union

from hvcc.types.Lang import LangLetType
from hvcc.version import VERSION


# IR Object Definitions

IRValue = Union[float, int, str, List[float], List[int]]


class IRArg(BaseModel):
    name: str
    value_type: str
    description: str = ""
    default: Optional[IRValue] = None
    required: bool


class IR(BaseModel):
    control: bool
    signal: bool
    init: bool


class Perf(BaseModel):
    avx: float = 0
    sse: float = 0
    neon: float = 0


class IRNode(BaseModel):
    inlets: List[LangLetType]
    ir: IR
    outlets: List[LangLetType]
    args: List[IRArg] = []
    perf: Optional[Perf] = Perf()
    # perf: Perf
    description: Optional[str] = None
    alias: List[str] = []
    tags: List[str] = []
    keywords: List[str] = []


class HeavyIRType(RootModel):
    root: Dict[str, IRNode]


# IR Graph Definitions

class IRName(BaseModel):
    escaped: str
    display: str


class IRObjectdict(BaseModel):
    args: Dict
    type: str


class IRInit(BaseModel):
    order: List[str] = []


class IRReceiver(BaseModel):
    display: str
    hash: str
    extern: Optional[str] = None
    attributes: Dict
    ids: List[str]


class IROnMessage(BaseModel):
    id: str
    inletIndex: Optional[int] = None


class IRSendMessage(BaseModel):
    """ This object is a mess and should be split up
    """
    id: str
    onMessage: List[List[IROnMessage]]  # TODO: why is it a nested List?
    type: Optional[str] = None
    extern: Optional[str] = ''
    attributes: Optional[Union[List, Dict]] = None  # TODO: List from IR and Dict from Lang
    hash: Optional[str] = None
    display: Optional[str] = None
    name: str = ''


class IRTable(BaseModel):
    id: str
    display: str
    hash: str
    extern: Optional[bool] = None


class IRControl(BaseModel):
    receivers: Dict[str, IRReceiver]
    sendMessage: List[IRSendMessage]


class IRNumTempBuffer(BaseModel):
    float: int
    integer: int


class IRBuffer(BaseModel):
    type: str
    index: int


class IRSignalList(BaseModel):
    id: str
    inputBuffers: List[IRBuffer]
    outputBuffers: List[IRBuffer]


class IRSignal(BaseModel):
    numInputBuffers: int
    numOutputBuffers: int
    numTemporaryBuffers: IRNumTempBuffer
    processOrder: List[IRSignalList]


class IRGraph(BaseModel):
    version: str = VERSION
    name: IRName
    objects: Dict[str, IRObjectdict] = {}
    init: IRInit
    tables: Dict[str, IRTable] = {}
    control: IRControl
    signal: IRSignal


if __name__ == "__main__":
    """ Test object definitions
    """
    import json
    import importlib_resources

    heavy_ir_json = importlib_resources.files('hvcc') / 'core/json/heavy.ir.json'
    with open(heavy_ir_json, "r") as f:
        data = json.load(f)
        heavy_ir = HeavyIRType(root=data)
        print(heavy_ir.root.keys())
