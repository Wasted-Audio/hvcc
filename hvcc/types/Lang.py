# Heavy Compiler Collection
# Copyright (C) 2024 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from typing import Literal, Optional, Union

from pydantic import BaseModel, RootModel

LangConnectionType = Literal["-->", "-~>", "~f>"]
LangLetType = Literal["-->", "-~>", "~i>", "~f>", "signal"]
LangValueType = Literal["float", "int", "string", "bool", "dict", "floatarray", "intarray", "stringarray"]


class LangArg(BaseModel):
    name: str
    value_type: Optional[LangValueType] = None
    description: str
    default: Union[float, int, str, dict, list, None] = None
    required: bool


class LangLet(BaseModel):
    name: str
    connectionType: LangConnectionType
    description: str


class LangNode(BaseModel):
    description: str
    inlets: list[LangLet]
    outlets: list[LangLet]
    args: list[LangArg]
    alias: list[str]
    tags: list[str]


class HeavyLangType(RootModel):
    root: dict[str, LangNode]


if __name__ == "__main__":
    import json
    from importlib import resources
    from pathlib import Path

    heavy_lang_json = str(resources.files('hvcc') / 'core/json/heavy.lang.json')
    with open(Path(heavy_lang_json), "r") as f:
        data = json.load(f)
        heavy_lang = HeavyLangType(root=data)
        print(heavy_lang.root.keys())
