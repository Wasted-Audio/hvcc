# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

from .MaxObject import MaxObject


class MaxBinopObject(MaxObject):
    # a translation dictionary from max object to corresponding heavy object
    __MAX_HEAVY_DICT = {
        "+": "+",
        "+~": "+",
        "-": "-",
        "-~": "-",
        "*": "*",
        "*~": "*"
    }

    def __init__(self, obj_type, obj_args=None, obj_id=None, pos_x=0, pos_y=0):
        assert MaxBinopObject.is_binop(obj_type)
        MaxObject.__init__(self, obj_type, obj_args, obj_id, pos_x, pos_y)

    @classmethod
    def is_binop(clazz, obj_type):
        return obj_type in MaxBinopObject.__MAX_HEAVY_DICT

    @classmethod
    def get_supported_objects(clazz):
        return MaxBinopObject.__MAX_HEAVY_DICT.keys()

    def to_hv(self):
        return {
            "type": MaxBinopObject.__MAX_HEAVY_DICT[self.obj_type],
            "args": {
                "k": float(self.obj_args[0]) if len(self.obj_args) > 0 else 0.0
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
