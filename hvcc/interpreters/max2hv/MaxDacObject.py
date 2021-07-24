# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

from .MaxObject import MaxObject


class MaxDacObject(MaxObject):
    def __init__(self, obj_type, obj_args=None, obj_id=None, pos_x=0, pos_y=0):
        assert obj_type == "dac~"
        MaxObject.__init__(self, obj_type, obj_args, obj_id, pos_x, pos_y)

    def to_hv(self):
        return {
            "type": "dac",
            "args": {
                "channels": [1, 2] if len(self.obj_args) == 0 else [int(a) for a in self.obj_args]
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
