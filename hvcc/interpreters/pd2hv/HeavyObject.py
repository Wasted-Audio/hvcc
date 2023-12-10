# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023 Wasted Audio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import decimal
import json
import importlib_resources
from typing import Optional, List, Dict, Any

from .Connection import Connection
from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class HeavyObject(PdObject):

    heavy_lang_json = importlib_resources.files('hvcc') / 'core/json/heavy.lang.json'
    with open(heavy_lang_json, "r") as f:
        __HEAVY_LANG_OBJS = json.load(f)

    heavy_ir_json = importlib_resources.files('hvcc') / 'core/json/heavy.ir.json'
    with open(heavy_ir_json, "r") as f:
        __HEAVY_IR_OBJS = json.load(f)

    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        # get the object dictionary (note that it is NOT a copy)
        if self.is_hvlang:
            self.__obj_dict = self.__HEAVY_LANG_OBJS[obj_type]
        elif self.is_hvir:
            self.__obj_dict = self.__HEAVY_IR_OBJS[obj_type]
        else:
            assert False, f"{obj_type} is not a Heavy Lang or IR object."

        # resolve arguments
        obj_args = obj_args or []
        self.obj_dict = {}
        for i, a in enumerate(self.__obj_dict["args"]):
            # if the argument exists (and has been correctly resolved)
            if i < len(obj_args) and obj_args[i] is not None:
                # force the Heavy argument type
                # Catch type errors as early as possible
                try:
                    self.obj_dict[a["name"]] = self.force_arg_type(
                        obj_args[i],
                        a["value_type"])
                except Exception as e:
                    self.add_error(
                        f"Heavy {obj_type} cannot convert argument \"{a['name']}\""
                        f" with value \"{obj_args[i]}\" to type {a['value_type']}: {e}")
            else:
                # the default argument is required
                if a["required"]:
                    self.add_error(
                        f"Required argument \"{a['name']}\" to object {obj_type} not present: {obj_args}")
                else:
                    # don't worry about supplying a default,
                    # let hv2ir take care of it. pd2hv only passes on the
                    # provided parameters.
                    # self.obj_args[a["name"]] = a["default"]
                    pass

        self.__annotations = {}

        # send/receive, table, etc. must have public scope
        # TODO(mhroth): dirty
        if obj_type in ["table", "__table", "send", "__send", "receive", "__receive"]:
            self.__annotations["scope"] = "public"

    @classmethod
    def force_arg_type(cls, value: str, value_type: str) -> Any:
        # TODO(mhroth): add support for mixedarray?
        if value_type == "auto":
            try:
                return float(value)
            except Exception:
                return str(value)
        elif value_type == "float":
            return float(value)
        elif value_type == "int":
            return int(decimal.Decimal(value))
        elif value_type == "string":
            return str(value)
        elif value_type == "boolean":
            if isinstance(value, str):
                return value.strip().lower() not in {"false", "f", "0"}
            else:
                return bool(value)
        elif value_type == "floatarray":
            if isinstance(value, list):
                return [float(v) for v in value]
            if isinstance(value, str):
                return [float(v) for v in value.split()]
            else:
                raise Exception(f"Cannot convert value to type floatarray: {value}")
        elif value_type == "intarray":
            if isinstance(value, list):
                return [int(v) for v in value]
            if isinstance(value, str):
                return [int(v) for v in value.split()]
            else:
                raise Exception(f"Cannot convert value to type intarray: {value}")
        elif value_type == "stringarray":
            if isinstance(value, list):
                return [str(v) for v in value]
            if isinstance(value, str):
                return [str(v) for v in value.split()]
            else:
                raise Exception(f"Cannot convert value to type stringarray: {value}")
        else:
            # NOTE(mhroth): if value_type is not a known type or None, that is
            # not necessarily an error. It may simply be that the value should
            # not be resolved to anything other than what it already is.
            # This happens most often with message objects.
            return value

    @property
    def is_hvlang(self) -> bool:
        return self.obj_type in self.__HEAVY_LANG_OBJS

    @property
    def is_hvir(self) -> bool:
        return self.obj_type in self.__HEAVY_IR_OBJS

    def get_inlet_connection_type(self, inlet_index: int) -> Optional[str]:
        """ Returns the inlet connection type, None if the inlet does not exist.
        """
        # TODO(mhroth): it's stupid that hvlang and hvir json have different data formats here
        if self.is_hvlang:
            if len(self.__obj_dict["inlets"]) > inlet_index:
                return self.__obj_dict["inlets"][inlet_index]["connectionType"]
            else:
                return None
        elif self.is_hvir:
            if len(self.__obj_dict["inlets"]) > inlet_index:
                return self.__obj_dict["inlets"][inlet_index]
            else:
                return None
        else:
            return None

    def get_outlet_connection_type(self, outlet_index: int) -> Optional[str]:
        """ Returns the outlet connection type, None if the inlet does not exist.
        """
        # TODO(mhroth): it's stupid that hvlang and hvir json have different data formats here
        if self.is_hvlang:
            if len(self.__obj_dict["outlets"]) > outlet_index:
                return self.__obj_dict["outlets"][outlet_index]["connectionType"]
            else:
                return None
        elif self.is_hvir:
            if len(self.__obj_dict["outlets"]) > outlet_index:
                return self.__obj_dict["outlets"][outlet_index]
            else:
                return None
        else:
            return None

    def add_connection(self, c: Connection) -> None:
        """ Adds a connection, either inlet or outlet, to this object.
        """
        if c.from_id == self.obj_id:
            if self.get_outlet_connection_type(c.outlet_index) is not None:
                self._outlet_connections[str(c.outlet_index)].append(c)
            else:
                self.add_error(
                    f"Connection made from non-existent outlet at {self.obj_type}:{c.outlet_index}.",
                    enum=NotificationEnum.ERROR_UNABLE_TO_CONNECT_OBJECTS)
        elif c.to_id == self.obj_id:
            if self.get_inlet_connection_type(c.inlet_index) is not None:
                self._inlet_connections[str(c.inlet_index)].append(c)
            else:
                self.add_error(
                    f"Connection made to non-existent inlet at [{self.obj_type} {self.obj_dict}]:{c.inlet_index}.",
                    enum=NotificationEnum.ERROR_UNABLE_TO_CONNECT_OBJECTS)
        else:
            raise Exception("Adding a connection to the wrong object!")

    def to_hv(self) -> Dict:
        return {
            "type": self.obj_type,
            "args": self.obj_dict,
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            },
            "annotations": self.__annotations
        }
