# Copyright 2015,2016 Enzien Audio, Ltd. All Rights Reserved.

from .PdObject import PdObject


class PdLetObject(PdObject):
    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type in ["inlet", "inlet~", "outlet", "outlet~"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)
        self.let_index = 0

    def get_outlet_connection_type(self, outlet_index=0):
        if len(self.obj_args) > 0 and self.obj_args[0] in ["-->", "~f>", "~i>", "-~>"]:
            return self.obj_args[0]
        else:
            return PdObject.get_outlet_connection_type(self)

    def to_hv(self):
        return {
            "type": self.obj_type.strip("~"),
            "args": {
                "name": "",  # Pd does not give an inlet name
                "index": self.let_index,
                "type": self.get_outlet_connection_type()
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
