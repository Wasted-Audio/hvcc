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


class PdRouteObject(PdObject):
    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type == "route"
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)
        if len(obj_args) == 0:
            self.add_error("At least one argument is required.")
        # NOTE(joe): disabling this warning as it can be quite annoying.
        # if len(set(obj_args) & set(["bang", "list", "float", "symbol"])) > 0:
        #     self.add_warning(
        #         "Heavy interprets route arguments such as \"bang\", \"list\", \"float\", "
        #         "and \"symbol\" literally. They cannot be used to filter generic "
        #         "messages as in Pd.")
        if len(set(obj_args)) != len(obj_args):
            c = Counter(obj_args).most_common(1)
            self.add_error(
                "All arguments to [route] must be unique. Argument \"{0}\" is "
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
                "The right inlet of route is not supported. "
                "It will not do anything.")

    def to_hv(self):
        """Creates a graph dynamically based on the number of arguments.
        An unconnected right inlet is added.

        [inlet]                                         [inlet]
        |
        [@hv_obj switchcase [arg list (N elements)]           ]
        |                             |                       |
        [@hv_obj __slice 1 -1]        [@hv_obj __slice 1 -1]  |
        |        |                    |          |            |
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

        # add slices to graph
        for i, a in enumerate(self.obj_args):
            # add slices to graph
            route_graph["objects"]["slice_{0}".format(i)] = {
                "type": "slice",
                "args": {
                    "index": 1,
                    "length": -1
                },
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
                "to": {"id": "slice_{0}".format(i), "inlet": 0},
                "type": "-->"
            })

            # add connection from slice outlets 0 and 1 to outlet
            route_graph["connections"].append({
                "from": {"id": "slice_{0}".format(i), "outlet": 0},
                "to": {"id": "outlet_{0}".format(i), "inlet": 0},
                "type": "-->"
            })
            route_graph["connections"].append({
                "from": {"id": "slice_{0}".format(i), "outlet": 1},
                "to": {"id": "outlet_{0}".format(i), "inlet": 0},
                "type": "-->"
            })

        return route_graph
