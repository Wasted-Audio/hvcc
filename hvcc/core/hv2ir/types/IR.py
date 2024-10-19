from pydantic import BaseModel, RootModel
from typing import List, Optional, Union, Literal


ConnectionType = Literal["-->", "~i>", "~f>", "signal"]


class IndexableBaseModel(BaseModel):
    """Allows a BaseModel to return its fields by string variable indexing"""
    def __getitem__(self, item):
        return getattr(self, item)


class Arg(IndexableBaseModel):
    name: str
    value_type: str
    description: str = ""
    default: Union[float, int, str, List[float], List[int], None] = None
    required: bool


class IR(BaseModel):
    control: bool
    signal: bool
    init: bool


class Perf(BaseModel):
    avx: float = 0
    sse: float = 0
    neon: float = 0


class IRNode(IndexableBaseModel):
    inlets: List[ConnectionType]
    ir: IR
    outlets: List[ConnectionType]
    args: List[Arg] = []
    perf: Optional[Perf] = Perf()
    # perf: Perf
    description: Optional[str] = None
    alias: List[str] = []
    tags: List[str] = []
    keywords: List[str] = []


class HeavyIRType(RootModel):
    root: dict[str, IRNode]


# import json
# with open('heavy.ir.json') as f:
#     data = json.load(f)
#     heavy_ir = HeavyIR(root=data)
#     print(heavy_ir.root.keys())
