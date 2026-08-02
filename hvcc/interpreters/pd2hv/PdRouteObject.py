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
from typing import Optional

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject

from hvcc.types.Heavy import Heavy, HvPos, HvConn, HvConnFrom, HvConnTo


class PdRouteObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[list] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type == "route"
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        if obj_args is not None:
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
                    f"All arguments to [route] must be unique. Argument \"{c[0][0]}\" is repeated {c[0][1]} times.",
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
            self.add_warning("The right inlet of route is not supported. It will not do anything.")

    def to_hv(self) -> Heavy:
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

        route_graph = Heavy(
            type="graph",
            args=[],
            objects={
                "inlet": Heavy(
                    type="inlet",
                    args={
                        "type": "-->",
                        "index": 0
                    }
                ),
                "inlet_right": Heavy(
                    type="inlet",
                    args={
                        "type": "-->",
                        "index": 1
                    }
                ),
                "switchcase": Heavy(
                    type="__switchcase",
                    args={
                        "cases": self.obj_args,
                        "is_route": True
                    }
                ),
                "outlet_right": Heavy(
                    type="outlet",
                    args={
                        "type": "-->",
                        "index": len(self.obj_args)
                    }
                )
            },
            connections=[
                HvConn(
                    type="-->",
                    conn_from=HvConnFrom(id="inlet", outlet=0),
                    conn_to=HvConnTo(id="switchcase", inlet=0)
                ),
                HvConn(
                    type="-->",
                    conn_from=HvConnFrom(id="switchcase", outlet=len(self.obj_args)),
                    conn_to=HvConnTo(id="outlet_right", inlet=0)
                )
            ],
            properties=HvPos(x=self.pos_x, y=self.pos_y)
        )

        # add slices to graph
        for i, a in enumerate(self.obj_args):
            # add slices to graph
            route_graph.objects[f"slice_{i}"] = Heavy(
                type="slice",
                args={
                    "index": 1,
                    "length": -1
                }
            )

            # add outlets to graph
            route_graph.objects[f"outlet_{i}"] = Heavy(
                type="outlet",
                args={
                    "type": "-->",
                    "index": i
                }
            )
            # add connection from switchcase to slice
            route_graph.connections.append(
                HvConn(
                    type="-->",
                    conn_from=HvConnFrom(id="switchcase", outlet=i),
                    conn_to=HvConnTo(id=f"slice_{i}", inlet=0)
                )
            )

            # add connection from slice outlets 0 and 1 to outlet
            route_graph.connections.append(
                HvConn(
                    type="-->",
                    conn_from=HvConnFrom(id=f"slice_{i}", outlet=0),
                    conn_to=HvConnTo(id=f"outlet_{i}", inlet=0)
                )
            )
            route_graph.connections.append(
                HvConn(
                    type="-->",
                    conn_from=HvConnFrom(id=f"slice_{i}", outlet=1),
                    conn_to=HvConnTo(id=f"outlet_{i}", inlet=0)
                )
            )

        return route_graph
