from pydantic import BaseModel, RootModel
from typing import List, Optional, Union, Literal


IRConnectionType = Literal["-->", "~i>", "~f>", "signal"]


class IRArg(BaseModel):
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


class IRNode(BaseModel):
    inlets: List[IRConnectionType]
    ir: IR
    outlets: List[IRConnectionType]
    args: List[IRArg] = []
    perf: Optional[Perf] = Perf()
    # perf: Perf
    description: Optional[str] = None
    alias: List[str] = []
    tags: List[str] = []
    keywords: List[str] = []


class HeavyIRType(RootModel):
    root: dict[str, IRNode]


if __name__ == "__main__":
    import json
    with open('../../json/heavy.ir.json') as f:
        data = json.load(f)
        heavy_ir = HeavyIRType(root=data)
        print(heavy_ir.root.keys())
