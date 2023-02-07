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

from typing import Dict, List, Optional

from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


class HIrOutlet(HeavyIrObject):
    """ A specific implementation of the outlet object.
    """

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional[HeavyGraph] = None,
        annotations: Optional[Dict] = None
    ) -> None:
        super().__init__("__outlet", args=args, graph=graph, annotations=annotations)

    def get_ir_on_message(self, inlet_index: int = 0) -> List:
        x = []
        if self.graph is not None:
            for c in self.graph.outlet_connections[self.args["index"]]:
                x.extend(c.to_object.get_ir_on_message(c.inlet_index))
        return x
