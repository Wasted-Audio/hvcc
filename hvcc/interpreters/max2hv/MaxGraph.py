# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

import os

from .Connection import Connection
from .MaxObject import MaxObject


class MaxGraph(MaxObject):
    def __init__(self, obj_type=None, obj_args=None, obj_id=None, pos_x=0, pos_y=0, max_path=None):
        MaxObject.__init__(self, "patcher", obj_args, obj_id, pos_x, pos_y)

        # file location of this graph
        self.__max_path = max_path

        self.__objs = {}
        self.__connections = []

        self.__inlet_objects = []
        self.__outlet_objects = []

    def add_object(self, obj, obj_id=None):
        obj_id = obj_id or obj.obj_id
        assert obj_id not in self.__objs
        self.__objs[obj_id] = obj

        if obj.obj_type == "inlet":
            obj.set_index(len(self.__inlet_objects))
            self.__inlet_objects.append(obj)
        elif obj.obj_type == "outlet":
            obj.set_index(len(self.__outlet_objects))
            self.__outlet_objects.append(obj)

    def add_connection(self, from_id, from_outlet, to_id, to_inlet):
        assert from_id in self.__objs and to_id in self.__objs
        c = Connection(
            from_id, from_outlet,
            to_id, to_inlet,
            self.__objs[from_id].get_outlet_connection_type(from_outlet))
        self.__connections.append(c)

    def get_outlet_connection_type(self, outlet_index):
        return self.__outlet_objects[outlet_index].get_outlet_connection_type()

    def to_hv(self):
        return {
            "type": "graph",
            "imports": [],
            "args": [],
            "objects": {k: v.to_hv() for k, v in self.__objs.iteritems()},
            "connections": [c.to_hv() for c in self.__connections],
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }

    def __repr__(self):
        return "graph.{0}({1})".format(
            self.obj_id,
            os.path.basename(self.__max_path))
