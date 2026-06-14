# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only


from pydantic import BaseModel, Field, ConfigDict


class HvPos(BaseModel):
    x: int
    y: int


class HvConnFrom(BaseModel):
    id: str
    outlet: int


class HvConnTo(BaseModel):
    id: str
    inlet: int


class HvConn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    conn_from: HvConnFrom = Field(..., alias='from')
    conn_to: HvConnTo = Field(..., alias='to')


class Heavy(BaseModel):
    type: str
    imports: list = []
    args: dict = {}
    objects: dict[str, "Heavy"] = {}
    connections: list[HvConn] = []
    properties: HvPos = HvPos(x=0, y=0)
    annotations: dict = {}
