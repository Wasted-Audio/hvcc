# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import Optional, Union

from pydantic import BaseModel, RootModel

from hvcc.types.Lang import LangLetType
from hvcc.version import VERSION

# IR Object Definitions

IRValue = Union[float, int, str, list[float], list[int]]


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
    inlets: list[LangLetType]
    ir: IR
    outlets: list[LangLetType]
    args: list[IRArg] = []
    perf: Optional[Perf] = Perf()
    # perf: Perf
    description: Optional[str] = None
    alias: list[str] = []
    tags: list[str] = []
    keywords: list[str] = []


class HeavyIRType(RootModel):
    root: dict[str, IRNode]


# IR Graph Definitions

class IRName(BaseModel):
    escaped: str
    display: str


class IRObjectdict(BaseModel):
    args: dict
    type: str


class IRInit(BaseModel):
    order: list[str] = []


class IRReceiver(BaseModel):
    display: str
    hash: str
    extern: Optional[str] = None
    attributes: dict
    ids: list[str]


class IROnMessage(BaseModel):
    id: str
    inletIndex: Optional[int] = None


class IRSendMessage(BaseModel):
    """ This object is a mess and should be split up
    """
    id: str
    onMessage: list[list[IROnMessage]]  # TODO: why is it a nested List?
    type: Optional[str] = None
    extern: Optional[str] = ''
    attributes: Optional[Union[list, dict]] = None  # TODO: List from IR and Dict from Lang
    hash: Optional[str] = None
    display: Optional[str] = None
    name: str = ''


class IRTable(BaseModel):
    id: str
    display: str
    hash: str
    extern: Optional[bool] = None


class IRControl(BaseModel):
    receivers: dict[str, IRReceiver]
    sendMessage: list[IRSendMessage]


class IRNumTempBuffer(BaseModel):
    float: int
    integer: int


class IRBuffer(BaseModel):
    type: str
    index: int


class IRSignalList(BaseModel):
    id: str
    inputBuffers: list[IRBuffer]
    outputBuffers: list[IRBuffer]


class IRSignal(BaseModel):
    numInputBuffers: int
    numOutputBuffers: int
    numTemporaryBuffers: IRNumTempBuffer
    processOrder: list[IRSignalList]


class IRGraph(BaseModel):
    version: str = VERSION
    name: IRName
    objects: dict[str, IRObjectdict] = {}
    init: IRInit
    tables: dict[str, IRTable] = {}
    control: IRControl
    signal: IRSignal


if __name__ == "__main__":
    """ Test object definitions
    """
    import json
    from importlib import resources
    from pathlib import Path

    heavy_ir_json = str(resources.files('hvcc') / 'core/json/heavy.ir.json')
    with open(Path(heavy_ir_json), "r") as f:
        data = json.load(f)
        heavy_ir = HeavyIRType(root=data)
        print(heavy_ir.root.keys())
