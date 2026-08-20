# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023-2024 Wasted Audio
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

from typing import Dict, Optional

from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph

from hvcc.types.Lang import LangLetType
from hvcc.types.IR import IROnMessage

class HIrInlet(HeavyIrObject):
    """ A specific implementation of the inlet object.
    """

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional[HeavyGraph] = None,
        annotations: Optional[Dict] = None
    ) -> None:
        super().__init__("__inlet", args=args, graph=graph, annotations=annotations)

    def get_ir_on_message(self, inlet_index: int = 0) -> list[IROnMessage]:
        """ Parse incoming message and send to the control outlet connections.
        """
        x = []
        for outlet in self.outlet_connections:
            for c in outlet:
                if c.is_control:
                    x.extend(c.to_object.get_ir_on_message(c.inlet_index))
        return x

    def _resolved_outlet_type(self, outlet_index: int = 0) -> Optional[LangLetType]:
        if outlet_index == 1:
            return "-->"
        if self.graph is not None:
            connections = self.graph.inlet_connections[self.args["index"]]
            signal_types = {c.type for c in connections if c.is_signal}
            if len(signal_types) == 1:
                return list(signal_types)[0]
            elif len(signal_types) > 1:
                raise HeavyException(
                    f"{self} has multiple incident signal connections of differing type. "
                    "The outlet type cannot be explicitly resolved.")
            else:
                connection_type_set = {c.type for c in connections}
                if len(connection_type_set) == 0:
                    # object has no incident connections.
                    return "-->"  # outlet type defaults to control (-->)
                elif len(connection_type_set) == 1:
                    return list(connection_type_set)[0]
                else:
                    control_types = [t for t in connection_type_set if t == "-->"]
                    if control_types:
                        return "-->"
                    return list(connection_type_set)[0]
        return None
