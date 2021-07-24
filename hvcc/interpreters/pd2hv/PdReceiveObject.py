# Copyright (C) 2014-2018 Enzien Audio, Ltd.
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

from .PdObject import PdObject
from .pdowl import parse_pd_owl_args, PdOwlException


class PdReceiveObject(PdObject):

    __INSTANCE_COUNTER = 0

    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type in ["r", "r~", "receive", "receive~", "catch~"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

        self.__receiver_name = ""
        self.__extern_type = None
        self.__attributes = {}
        self.__priority = None  # priority is not set

        PdReceiveObject.__INSTANCE_COUNTER += 1
        self.__instance = PdReceiveObject.__INSTANCE_COUNTER

        try:
            # receive objects don't necessarily need to have a name
            self.__receiver_name = self.obj_args[0]

            # only extern control rate receivers
            if obj_type in ["r", "receive"]:
                # NOTE(mhroth): the second argument is _either_ externing the receiver or setting the priority
                # This means that right now priority cannot be set on externed receivers
                if self.obj_args[1] == "@hv_param":
                    self.__extern_type = "param"
                elif self.obj_args[1] == "@hv_event":
                    self.__extern_type = "event"
                elif int(self.obj_args[1]):
                    self.__priority = int(self.obj_args[1])
        except Exception:
            pass

        if self.__extern_type == "param":
            try:
                self.__attributes = {
                    "min": 0.0,
                    "max": 1.0,
                    "default": 0.5,
                    "type": "float"
                }
                self.__attributes["min"] = float(self.obj_args[2])
                self.__attributes["max"] = float(self.obj_args[3])
                self.__attributes["default"] = float(self.obj_args[4])
                self.__attributes["type"] = str(self.obj_args[5])
            except ValueError:
                self.add_warning(
                    f"Minimum, maximum, and default values for Parameter {self.__receiver_name}  must be numbers.")
            except Exception:
                pass

            if not (self.__attributes["min"] <= self.__attributes["default"]):
                self.add_error("Default parameter value is less than the minimum. "
                               "Receiver will not be exported: {0:g} < {1:g}".format(
                                   self.__attributes["default"],
                                   self.__attributes["min"]))
                self.__extern_type = None
            if not (self.__attributes["default"] <= self.__attributes["max"]):
                self.add_error("Default parameter value is greater than the maximum. "
                               "Receiver will not be exported: {0:g} > {1:g}".format(
                                   self.__attributes["default"],
                                   self.__attributes["max"]))
                self.__extern_type = None

        if '@owl' in self.obj_args or '@owl_param' in self.obj_args:
            try:
                pd_owl_args = parse_pd_owl_args(self.obj_args)
                self.__attributes.update(pd_owl_args)
                self.__extern_type = "param"  # make sure output code is generated
            except PdOwlException as e:
                self.add_error(e)

    def validate_configuration(self):
        if self.obj_type in ["r~", "receive~"]:
            if len(self._inlet_connections.get("0", [])) > 0:
                self.add_error("[receive~] inlet connections are not supported.")

    def to_hv(self):
        # note: control rate send objects should not modify their name argument
        names = {
            "r": "",
            "receive": "",
            "r~": "sndrcv_sig_",
            "receive~": "sndrcv_sig_",
            "catch~": "thrwctch_sig_"
        }

        # NOTE(mhroth): we follow Pd's execution rule: deeper receivers fire first.
        # Receivers on the same level fire in the order of instantiation.
        if (self.__priority is None) or (self.__receiver_name == "__hv_init" and self.__priority == 0):
            self.__priority = (self.parent_graph.get_depth() * 1000) - self.__instance

        return {
            "type": "receive",
            "args": {
                "name": names[self.obj_type] + self.__receiver_name,
                "extern": self.__extern_type,
                "attributes": self.__attributes,
                "priority": self.__priority
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            },
            "annotations": {
                "scope": "public"
            }
        }
