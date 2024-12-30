# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, RootModel
from typing import List, Optional, Dict, Literal, Union


LangConnectionType = Literal["-->", "-~>", "~f>"]
LangLetType = Literal["-->", "-~>", "~i>", "~f>", "signal"]
LangValueType = Literal["float", "int", "string", "bool", "dict", "floatarray", "intarray", "stringarray"]


class LangArg(BaseModel):
    name: str
    value_type: Optional[LangValueType] = None
    description: str
    default: Union[float, int, str, Dict, List, None] = None
    required: bool


class LangLet(BaseModel):
    name: str
    connectionType: LangConnectionType
    description: str


class LangNode(BaseModel):
    description: str
    inlets: List[LangLet]
    outlets: List[LangLet]
    args: List[LangArg]
    alias: List[str]
    tags: List[str]


class HeavyLangType(RootModel):
    root: Dict[str, LangNode]


if __name__ == "__main__":
    import json
    import importlib_resources

    heavy_lang_json = importlib_resources.files('hvcc') / 'core/json/heavy.lang.json'
    with open(heavy_lang_json, "r") as f:
        data = json.load(f)
        heavy_lang = HeavyLangType(root=data)
        print(heavy_lang.root.keys())
