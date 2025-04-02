# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, RootModel

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.meta import Meta
from hvcc.types.IR import IRGraph, IRReceiver, IRSendMessage, IRTable


class CompilerMsg(BaseModel):
    enum: NotificationEnum = NotificationEnum.EMPTY
    message: str


class CompilerNotif(BaseModel, arbitrary_types_allowed=True):
    has_error: bool = False
    exception: Optional[Exception] = None
    warnings: List[CompilerMsg] = []
    errors: List[CompilerMsg] = []


class CompilerResp(BaseModel):
    stage: str
    notifs: CompilerNotif = CompilerNotif()
    in_dir: str = ""
    in_file: str = ""
    out_dir: str = ""
    out_file: str = ""
    compile_time: float = 0.0
    obj_counter: Counter = Counter()
    obj_perf: Dict[str, Counter] = defaultdict(Counter)
    ir: Optional[IRGraph] = None


class CompilerResults(RootModel):
    root: Dict[str, CompilerResp]


class ExternParams(BaseModel):
    inParam: List[Tuple[str, IRReceiver]] = []
    outParam: List[Tuple[str, IRSendMessage]] = []


class ExternEvents(BaseModel):
    inEvent: List[Tuple[str, IRReceiver]] = []
    outEvent: List[Tuple[str, IRSendMessage]] = []


class ExternMidi(BaseModel):
    inMidi: List[str] = []
    outMidi: List[str] = []


class ExternMemoryPool(BaseModel):
    internal: int = 0
    inputQueue: int = 0
    outputQueue: int = 0


class ExternInfo(BaseModel):
    parameters: ExternParams = ExternParams()
    events: ExternEvents = ExternEvents()
    midi: ExternMidi = ExternMidi()
    tables: List[Tuple[str, IRTable]] = []
    memoryPoolSizesKb: ExternMemoryPool = ExternMemoryPool()


class Generator(ABC):

    @classmethod
    @abstractmethod
    def compile(
        cls,
        c_src_dir: str,
        out_dir: str,
        externs: ExternInfo,
        patch_name: Optional[str] = None,
        patch_meta: Meta = Meta(),
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> CompilerResp:
        raise NotImplementedError
