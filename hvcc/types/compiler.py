# Heavy Compiler Collection
# Copyright (C) 2024-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from pathlib import Path

from pydantic import BaseModel, RootModel

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.IR import IRGraph, IRReceiver, IRSendMessage, IRTable
from hvcc.types.meta import Meta


class CompilerMsg(BaseModel):
    enum: NotificationEnum = NotificationEnum.EMPTY
    message: str


class CompilerNotif(BaseModel, arbitrary_types_allowed=True):
    has_error: bool = False
    exception: Exception | None = None
    warnings: list[CompilerMsg] = []
    errors: list[CompilerMsg] = []


class CompilerResp(BaseModel):
    stage: str
    notifs: CompilerNotif = CompilerNotif()
    in_dir: Path = Path()
    in_file: Path = Path()
    out_dir: Path = Path()
    out_file: Path = Path()
    compile_time: float = 0.0
    obj_counter: Counter = Counter()
    obj_perf: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    ir: IRGraph | None = None


class CompilerResults(RootModel):
    root: dict[str, CompilerResp]


class ExternParams(BaseModel):
    inParam: list[tuple[str, IRReceiver]] = []
    outParam: list[tuple[str, IRSendMessage]] = []


class ExternEvents(BaseModel):
    inEvent: list[tuple[str, IRReceiver]] = []
    outEvent: list[tuple[str, IRSendMessage]] = []


class ExternMidi(BaseModel):
    inMidi: list[str] = []
    outMidi: list[str] = []


class ExternMemoryPool(BaseModel):
    internal: int = 0
    inputQueue: int = 0
    outputQueue: int = 0


class ExternInfo(BaseModel):
    parameters: ExternParams = ExternParams()
    events: ExternEvents = ExternEvents()
    midi: ExternMidi = ExternMidi()
    tables: list[tuple[str, IRTable]] = []
    memoryPoolSizesKb: ExternMemoryPool = ExternMemoryPool()


class Generator(ABC):

    @classmethod
    @abstractmethod
    def compile(
        cls,
        c_src_dir: Path,
        out_dir: Path,
        externs: ExternInfo,
        patch_name: str,
        patch_meta: Meta,
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: str | None = None,
        verbose: bool | None = False
    ) -> CompilerResp:
        raise NotImplementedError
