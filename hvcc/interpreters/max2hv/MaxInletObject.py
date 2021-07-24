# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

from .MaxObject import MaxObject


class MaxInletObject(MaxObject):
    def __init__(self, outlet_type=None, obj_id=None, pos_x=0, pos_y=0):
        MaxObject.__init__(self, "inlet", None, obj_id, pos_x, pos_y)
        self.__outlet_type = "~f>" if outlet_type == "signal" else "-->"

    def set_index(self, index):
        """Sets the index order of this inlet.
        """
        self.__index = index

    def get_outlet_connection_type(self, outlet_index=0):
        return self.__outlet_type

    def to_hv(self):
        return {
            "type": "inlet",
            "args": {
                "name": "",  # max does not give an inlet name
                "index": self.__index,
                "type": self.__outlet_type
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
