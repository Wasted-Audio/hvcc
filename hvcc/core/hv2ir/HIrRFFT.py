# Copyright (C) 2023-2026 Wasted Audio
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


class HIrRFFT(HeavyIrObject):
    """ __rfft~f
    """

    def __init__(
        self,
        obj_type: str,
        args: dict | None = None,
        graph: HeavyGraph | None = None,
        annotations: dict | None = None
    ) -> None:
        assert obj_type in {"__rfft~f", "__rifft~f"}
        super().__init__(obj_type, args=args, graph=graph, annotations=annotations)

    def reduce(self) -> tuple | None:
        if self.graph is not None:
            self.args["block_size"] = self.graph.args["block_size"]
            return ({self}, [])

        return None
