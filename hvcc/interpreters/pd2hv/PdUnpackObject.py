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

from typing import Optional, List, Dict

from .PdObject import PdObject


class PdUnpackObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type == "unpack"
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        if len(self.obj_args) == 0:
            self.add_error("Unpack requires at least one argument.")
        if not (set(self.obj_args) <= set(["f", "s"])):
            self.add_warning("Heavy only supports arguments 'f' and 's' to unpack.")

    def to_hv(self) -> Dict:
        """ Creates a graph dynamically based on the number of arguments.

            [inlet                                                ]
            |                        |      |
            [@hv_obj __slice 0 1]    ...    [@hv_obj __slice N-1 1]
            |                        |      |
            [outlet_0]               ...    [outlet_N-1]
        """

        hv_graph: Dict = {
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
                }
            },
            "connections": [],
            "properties": {"x": self.pos_x, "y": self.pos_y}
        }

        # NOTE(mhroth): reverse the iteration such that connections are
        # added in the correct order
        for i in reversed(range(len(self.obj_args))):
            # add slices to graph
            hv_graph["objects"][f"slice_{i}"] = {
                "type": "slice",
                "args": {
                    "index": i,
                    "length": 1
                },
                "properties": {"x": 0, "y": 0}
            }

            # add outlets to graph
            hv_graph["objects"][f"outlet_{i}"] = {
                "type": "outlet",
                "args": {
                    "type": "-->",
                    "index": i
                },
                "properties": {"x": 0, "y": 0}
            }

            # add connection from inlet to slice
            hv_graph["connections"].append({
                "from": {"id": "inlet", "outlet": 0},
                "to": {"id": f"slice_{i}", "inlet": 0},
                "type": "-->"
            })

            # add connection from slice to outlet
            hv_graph["connections"].append({
                "from": {"id": f"slice_{i}", "outlet": 0},
                "to": {"id": f"outlet_{i}", "inlet": 0},
                "type": "-->"
            })

        return hv_graph
