from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ConnectionType = Literal["~f>", "-->"]
ExternType = Literal["param", "event"]


class From(BaseModel):
    id: str
    outlet: int


class To(BaseModel):
    id: str
    inlet: int


class Connection(BaseModel):
    from_field: From = Field(..., alias="from")
    to: To
    type: ConnectionType


class HvProperties(BaseModel):
    x: int
    y: int


class HvArgs(BaseModel):
    extern: Optional[ExternType] = None
    index: int = 0
    name: Optional[str] = None
    priority: Optional[int] = None
    size: Optional[int] = None
    values: Optional[List] = None
    type: str = ""
    required: Optional[bool] = None
    default: Optional[List] = None
    value_type: Optional[str] = None
    length: Optional[int] = None


class HvObject(BaseModel):
    type: str
    annotations: Optional[Dict[str, str]] = None
    args: HvArgs
    properties: HvProperties


class HvGraph(BaseModel):
    type: str
    args: HvArgs
    connections: Optional[List[Connection]] = []
    imports: Optional[List[str]] = []
    objects: Optional[Dict[str, HvObject]] = {}
    route_Ymaxs: Optional[HvObject] = None
    properties: HvProperties
    annotations: Optional[Dict[str, str]] = None


# if __name__ == "__main__":
#     import json
#     import importlib_resources

#     heavy_graph_json = importlib_resources.files('hvcc') / 'interpreters/pd2hv/libs/heavy_converted/lorenz~.hv.json'
#     with open(heavy_graph_json, "r") as f:
#         data = json.load(f)
#         heavy_graph = HvGraph(**data)
#         print(heavy_graph.keys())
