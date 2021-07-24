# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

import json
import os
import re

from .MaxObject import MaxObject


class HeavyObject(MaxObject):

    with open(os.path.join(os.path.dirname(__file__), "../../core/json/heavy.lang.json"), "r") as f:
        __HEAVY_LANG_OBJS = json.loads(f.read())

    with open(os.path.join(os.path.dirname(__file__), "../../core/json/heavy.ir.json"), "r") as f:
        __HEAVY_IR_OBJS = json.loads(f.read())

    __re_dollar = re.compile("\$(\d+)")

    def __init__(self, obj_type, obj_args=None, obj_id=None, pos_x=0, pos_y=0):
        MaxObject.__init__(self, obj_type, obj_args, obj_id, pos_x, pos_y)

        # get the object dictionary (note that it is NOT a copy)
        if self.is_hvlang:
            self.__obj_dict = HeavyObject.__HEAVY_LANG_OBJS[obj_type]
        elif self.is_hvir:
            self.__obj_dict = HeavyObject.__HEAVY_IR_OBJS[obj_type]
        else:
            raise Exception("{0} is not a Heavy Lang or IR object.".format(obj_type))

        # resolve arguments
        obj_args = obj_args or []
        self.obj_args = {}
        for i, a in enumerate(self.__obj_dict["args"]):
            # if the argument exists and is not an unresolved dollar argument
            if len(obj_args) > i and not HeavyObject.__re_dollar.findall(obj_args[i]):
                # TODO(mhroth): need to force type of argument?
                self.obj_args[a["name"]] = obj_args[i]
            else:
                # the default argument is required
                if a["required"]:
                    raise Exception("Required argument \"{0}\" to object {1} not present: {2}".format(
                        a["name"],
                        obj_type,
                        obj_args))
                else:
                    self.obj_args[a["name"]] = a["default"]

    @classmethod
    def is_heavy(clazz, obj_type):
        return (obj_type in HeavyObject.__HEAVY_LANG_OBJS) or \
            (obj_type in HeavyObject.__HEAVY_IR_OBJS)

    @property
    def is_hvlang(self):
        return self.obj_type in HeavyObject.__HEAVY_LANG_OBJS

    @property
    def is_hvir(self):
        return self.obj_type in HeavyObject.__HEAVY_IR_OBJS

    def get_outlet_connection_type(self, outlet_index):
        # TODO(mhroth): it's stupid that hvlang and hvir json have different
        # data formats here
        if self.is_hvlang:
            return self.__obj_dict["outlets"][outlet_index]["connectionType"]
        elif self.is_hvir:
            return self.__obj_dict["outlets"][outlet_index]
        else:
            raise Exception()

    def to_hv(self):
        return {
            "type": self.obj_type,
            "args": self.obj_args,
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
