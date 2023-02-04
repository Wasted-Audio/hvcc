# Copyright 2015,2016 Enzien Audio, Ltd. All Rights Reserved.

from typing import Optional, List

from .PdObject import PdObject


class PdLetObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ):
        assert obj_type in {"inlet", "inlet~", "outlet", "outlet~"}
        super().__init__(obj_type, obj_args, pos_x, pos_y)
        self.let_index = 0

    def get_outlet_connection_type(self, outlet_index: int) -> str:
        if len(self.obj_args) > 0 and self.obj_args[0] in {"-->", "~f>", "~i>", "-~>"}:
            return self.obj_args[0]
        else:
            return super().get_outlet_connection_type(outlet_index)

    def to_hv(self):
        return {
            "type": self.obj_type.strip("~"),
            "args": {
                "name": "",  # Pd does not give an inlet name
                "index": self.let_index,
                "type": self.get_outlet_connection_type(self.let_index)
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
