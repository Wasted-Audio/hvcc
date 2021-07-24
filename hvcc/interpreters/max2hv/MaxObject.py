# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

import random
import string


class MaxObject:
    def __init__(self, obj_type, obj_args=None, obj_id=None, pos_x=0, pos_y=0):
        self.obj_type = obj_type
        self.obj_args = obj_args or []
        self.obj_id = obj_id or "".join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
        self.pos_x = int(pos_x)
        self.pos_y = int(pos_y)

    def get_outlet_connection_type(self, outlet_index=0):
        """Returns the outlet connection type of this Max object.
        For the sake of convenience, the connection type is reported in
        Heavy's format.
        """
        return "~f>" if self.obj_type.endswith("~") else "-->"

    @classmethod
    def get_supported_objects(clazz):
        """Returns a list of Max objects that this class can parse.
        """
        # TODO(mhroth): return [] ?
        raise NotImplementedError()

    def to_hv(self):
        """Returns the HeavyLang JSON representation of this object.
        """
        raise NotImplementedError()
