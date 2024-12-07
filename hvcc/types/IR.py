from pydantic import BaseModel, RootModel
from typing import Dict, List, Optional, Union

from hvcc.types.Lang import LangLetType


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


if __name__ == "__main__":
    import json
    import importlib_resources

    heavy_ir_json = importlib_resources.files('hvcc') / 'core/json/heavy.ir.json'
    with open(heavy_ir_json, "r") as f:
        data = json.load(f)
        heavy_ir = HeavyIRType(root=data)
        print(heavy_ir.root.keys())
