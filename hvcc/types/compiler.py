# Heavy Compiler Collection
# Copyright (C) 2021-2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from collections import Counter
from typing import Dict, List, Optional

from pydantic import BaseModel

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.meta import Meta
from hvcc.types.IR import IRGraph


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
    obj_perf: Dict[str, Counter] = {}
    ir: Optional[IRGraph] = None


class Generator(ABC):

    @classmethod
    @abstractmethod
    def compile(
        cls,
        c_src_dir: str,
        out_dir: str,
        externs: Dict,
        patch_name: Optional[str] = None,
        patch_meta: Meta = Meta(),
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> CompilerResp:
        raise NotImplementedError
