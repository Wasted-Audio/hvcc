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

from typing import Dict, Optional

from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


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

    def _resolved_outlet_type(self, outlet_index: int = 0) -> Optional[str]:
        if self.graph is not None:
            connections = self.graph.inlet_connections[self.args["index"]]
            connection_type_set = {c.type for c in connections}
            if len(connection_type_set) == 0:
                # object has no incident connections.
                return "-->"  # outlet type defaults to control (-->)
            elif len(connection_type_set) == 1:
                return list(connection_type_set)[0]
            else:
                raise HeavyException(
                    f"{self} has multiple incident connections of differing type. "
                    "The outlet type cannot be explicitly resolved.")
        return None
