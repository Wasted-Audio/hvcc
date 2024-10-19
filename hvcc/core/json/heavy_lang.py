from pydantic import BaseModel, RootModel
from typing import List, Optional, Any


class Inlet(BaseModel):
    name: str
    connectionType: str
    description: str


class Outlet(BaseModel):
    name: str
    connectionType: str
    description: str


class Arg(BaseModel):
    name: str
    value_type: Optional[str]
    description: str
    default: Any
    required: bool


class LangNode(BaseModel):
    description: str
    inlets: List[Inlet]
    outlets: List[Outlet]
    args: List[Arg]
    alias: List[str]
    tags: List[str]


class HeavyLang(RootModel):
    root: dict[str, LangNode]


# import json
# with open('heavy.lang.json') as f:
#     data = json.load(f)
#     heavy_lang = HeavyLang(root=data)
#     print(heavy_lang.root.keys())
