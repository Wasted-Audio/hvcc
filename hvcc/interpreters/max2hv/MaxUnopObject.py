# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

from .MaxObject import MaxObject


class MaxUnopObject(MaxObject):
    # a translation dictionary from max object to corresponding heavy object
    __MAX_HEAVY_DICT = {
        "abs": "abs",
        "abs~": "abs",
        "sqrt": "sqrt",
        "sqrt~": "sqrt"
    }

    def __init__(self, obj_type, obj_args=None, obj_id=None, pos_x=0, pos_y=0):
        assert MaxUnopObject.is_unnop(obj_type)
        MaxObject.__init__(self, obj_type, obj_args, obj_id, pos_x, pos_y)

    @classmethod
    def is_unnop(clazz, obj_type):
        return obj_type in MaxUnopObject.__MAX_HEAVY_DICT

    @classmethod
    def get_supported_objects(clazz):
        return MaxUnopObject.__MAX_HEAVY_DICT.keys()

    def to_hv(self):
        return {
            "type": MaxUnopObject.__MAX_HEAVY_DICT[self.obj_type],
            "args": {},
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
