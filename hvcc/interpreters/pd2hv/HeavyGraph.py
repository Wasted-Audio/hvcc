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

import json
import os

from .PdObject import PdObject
from .HeavyObject import HeavyObject


class HeavyGraph(PdObject):
    def __init__(self, hv_path, obj_args=None, pos_x=0, pos_y=0):
        PdObject.__init__(
            self,
            os.path.basename(hv_path).split(".")[0],
            obj_args,
            pos_x, pos_y)

        # read the heavy graph
        with open(hv_path, "r") as f:
            self.hv_json = json.load(f)

        # parse the heavy data structure to determine the outlet connection type
        outlets = [o for o in self.hv_json["objects"].values() if o["type"] == "outlet"]
        sorted(outlets, key=lambda o: o["args"]["index"])
        self.__outlet_connection_types = [o["args"]["type"] for o in outlets]

        # resolve the arguments
        for i, a in enumerate(self.hv_json["args"]):
            if i < len(self.obj_args):
                arg_value = self.obj_args[i]
            elif a["required"]:
                self.add_error("Required argument \"{0}\" not found.".format(a["name"]))
                continue
            else:
                arg_value = a["default"]

            try:
                arg_value = HeavyObject.force_arg_type(arg_value, a["value_type"])
            except Exception as e:
                self.add_error("Heavy {0} cannot convert argument \"{1}\" with value \"{2}\" to type {3}: {4}".format(
                               self.obj_type,
                               a["name"],
                               arg_value,
                               a["value_type"],
                               str(e)))

            # resolve all arguments for each object in the graph
            for o in self.hv_json["objects"].values():
                for k, v in o["args"].items():
                    # TODO(mhroth): make resolution more robust
                    if v == "$" + a["name"]:
                        o["args"][k] = arg_value

        # reset all arguments, as they have all been resolved
        # any required arguments would break hv2ir as they will no longer
        # be supplied (because they are resolved)
        self.hv_json["args"] = []

    def get_outlet_connection_type(self, outlet_index):
        return self.__outlet_connection_types[outlet_index]

    def to_hv(self):
        return self.hv_json
