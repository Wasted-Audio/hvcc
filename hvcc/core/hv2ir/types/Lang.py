from pydantic import BaseModel, RootModel
from typing import List, Optional, Dict, Literal, Union


LangConnectionType = Literal["-->", "-~>", "~f>"]


class LangArg(BaseModel):
    name: str
    value_type: Optional[str]
    description: str
    default: Union[float, int, str, Dict, List, None] = None
    required: bool


class Inlet(BaseModel):
    name: str
    connectionType: LangConnectionType
    description: str


class Outlet(BaseModel):
    name: str
    connectionType: LangConnectionType
    description: str


class LangNode(BaseModel):
    description: str
    inlets: List[Inlet]
    outlets: List[Outlet]
    args: List[LangArg]
    alias: List[str]
    tags: List[str]


class HeavyLangType(RootModel):
    root: dict[str, LangNode]


if __name__ == "__main__":
    import json
    with open('../../json/heavy.lang.json') as f:
        data = json.load(f)
        heavy_lang = HeavyLangType(root=data)
        print(heavy_lang.root.keys())
