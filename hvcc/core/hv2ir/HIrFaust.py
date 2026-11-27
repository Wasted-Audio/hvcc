# Copyright (C) 2026 Wasted Audio
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


from .HeavyGraph import HeavyGraph
from .HeavyIrObject import HeavyIrObject


class HIrFaust(HeavyIrObject):
    """ This needs little logic as the implementation is forwarded to ir2c
    """

    def __init__(
        self,
        obj_type: str,
        args: dict | None = None,
        graph: HeavyGraph | None = None,
        annotations: dict | None = None
    ) -> None:
        assert obj_type == "__faustgen2~"
        assert args is not None
        super().__init__(obj_type, args=args, graph=graph,
                         num_inlets=args["num_inlets"] if args is not None else 1,
                         num_outlets=args["num_outlets"] if args is not None else 1,
                         annotations=annotations)

    def inlet_requires_signal(self, inlet_index: int = 0) -> bool:
        # Inlets above 0 require a signal
        return inlet_index > 0

    def outlet_requires_signal(self, outlet_index: int = 0) -> bool:
        # Outlets above 0 require a signal
        return outlet_index > 0
