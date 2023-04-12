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

from collections import Counter
from typing import Optional, List, Dict

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class PdSelectObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type in {"select", "sel"}
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        if not obj_args:
            obj_args = []

        if len(self.obj_args) == 0:
            self.add_error("At least one argument is required.")
        if len(set(self.obj_args)) != len(obj_args):
            c = Counter(obj_args).most_common(1)
            self.add_error(
                f"All arguments to [select] must be unique. Argument \"{c[0][0]}\" is repeated {c[0][1]} times.",
                NotificationEnum.ERROR_UNIQUE_ARGUMENTS_REQUIRED)

        # convert to obj_args to mixedarray, such that correct switchcase hash
        # is generated
        for i, a in enumerate(self.obj_args):
            try:
                self.obj_args[i] = float(a)
            except Exception:
                pass

    def validate_configuration(self) -> None:
        if len(self._inlet_connections.get("1", [])) > 0:
            self.add_warning("The right inlet of select is not supported. It will not do anything.")

    def to_hv(self) -> Dict:
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

        route_graph: Dict = {
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
            route_graph["objects"][f"__cast_b_{i}"] = {
                "type": "__cast_b",
                "args": {},
                "properties": {"x": 0, "y": 0}
            }

            # add outlets to graph
            route_graph["objects"][f"outlet_{i}"] = {
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
                "to": {"id": f"__cast_b_{i}", "inlet": 0},
                "type": "-->"
            })

            # add connection from slice to outlet
            route_graph["connections"].append({
                "from": {"id": f"__cast_b_{i}", "outlet": 0},
                "to": {"id": f"outlet_{i}", "inlet": 0},
                "type": "-->"
            })

        return route_graph
