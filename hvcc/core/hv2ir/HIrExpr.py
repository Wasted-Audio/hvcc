# Copyright (C) 2022-2025 Daniel Billotte, Wasted Audio
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

from .HeavyIrObject import HeavyIrObject
from .HeavyException import HeavyException
from .HeavyGraph import HeavyGraph


class HIrExpr(HeavyIrObject):
    """Just a stub to get it going..."""

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional[HeavyGraph] = None,
        annotations: Optional[Dict] = None
    ) -> None:
        super().__init__(obj_type, args=args, graph=graph,
                         num_inlets=args["num_inlets"] if args is not None else 1,
                         num_outlets=1,
                         annotations=annotations)

    def inlet_requires_signal(self, inlet_index: int = 0) -> bool:
        """ Overriding HeavyIrObject to deal with variable number of inlets
        """
        if inlet_index >= self.num_inlets:
            raise HeavyException(f"inlet_index: {inlet_index} is greater than number of inlets")
        return True
