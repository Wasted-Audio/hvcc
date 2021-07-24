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

from collections import Counter
from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class PdSelectObject(PdObject):
    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type in ["select", "sel"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

        if len(obj_args) == 0:
            self.add_error("At least one argument is required.")
        if len(set(obj_args)) != len(obj_args):
            c = Counter(obj_args).most_common(1)
            self.add_error(
                "All arguments to [select] must be unique. Argument \"{0}\" is "
                "repeated {1} times.".format(c[0][0], c[0][1]),
                NotificationEnum.ERROR_UNIQUE_ARGUMENTS_REQUIRED)

        # convert to obj_args to mixedarray, such that correct switchcase hash
        # is generated
        for i, a in enumerate(self.obj_args):
            try:
                self.obj_args[i] = float(a)
            except Exception:
                pass

    def validate_configuration(self):
        if len(self._inlet_connections.get("1", [])) > 0:
            self.add_warning(
                "The right inlet of select is not supported. "
                "It will not do anything.")

    def to_hv(self):
        """ Creates a graph dynamically based on the number of arguments.
            An unconnected right inlet is added.

            [inlet]                                         [inlet]
            |
            [@hv_obj switchcase [arg list (N elements)]           ]
            |                             |                       |
            [@hv_obj __cast_b]            [@hv_obj __cast_b]      |
            |                             |                       |
            [outlet_0]                    [outlet_N-1]            [outlet_right]
        """

        route_graph = {
            "type": "graph",
            "imports": [],
            "args": [],
            "objects": {
                "inlet": {
                    "type": "inlet",
                    "args": {
                        "type": "-->",
                        "index": 0
                    },
                    "properties": {"x": 0, "y": 0}
                },
                "inlet_right": {
                    "type": "inlet",
                    "args": {
                        "type": "-->",
                        "index": 1
                    },
                    "properties": {"x": 0, "y": 0}
                },
                "switchcase": {
                    "type": "__switchcase",
                    "args": {
                        "cases": self.obj_args
                    },
                    "properties": {"x": 0, "y": 0}
                },
                "outlet_right": {
                    "type": "outlet",
                    "args": {
                        "type": "-->",
                        "index": len(self.obj_args)
                    },
                    "properties": {"x": 0, "y": 0}
                },
            },
            "connections": [
                {
                    "from": {"id": "inlet", "outlet": 0},
                    "to": {"id": "switchcase", "inlet": 0},
                    "type": "-->"
                },
                {
                    "from": {"id": "switchcase", "outlet": len(self.obj_args)},
                    "to": {"id": "outlet_right", "inlet": 0},
                    "type": "-->"
                }
            ],
            "properties": {"x": self.pos_x, "y": self.pos_y}
        }

        for i in range(len(self.obj_args)):
            # add __cast_b to graph
            route_graph["objects"]["__cast_b_{0}".format(i)] = {
                "type": "__cast_b",
                "args": {},
                "properties": {"x": 0, "y": 0}
            }

            # add outlets to graph
            route_graph["objects"]["outlet_{0}".format(i)] = {
                "type": "outlet",
                "args": {
                    "type": "-->",
                    "index": i
                },
                "properties": {"x": 0, "y": 0}
            }

            # add connection from switchcase to slice
            route_graph["connections"].append({
                "from": {"id": "switchcase", "outlet": i},
                "to": {"id": "__cast_b_{0}".format(i), "inlet": 0},
                "type": "-->"
            })

            # add connection from slice to outlet
            route_graph["connections"].append({
                "from": {"id": "__cast_b_{0}".format(i), "outlet": 0},
                "to": {"id": "outlet_{0}".format(i), "inlet": 0},
                "type": "-->"
            })

        return route_graph
