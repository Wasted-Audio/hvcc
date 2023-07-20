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


from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


class HIrTabhead(HeavyIrObject):
    """ __tabhead~f and __tabhead
    """

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional[HeavyGraph] = None,
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type in {"__tabhead~f", "__tabhead"}
        super().__init__(obj_type, args=args, graph=graph, annotations=annotations)

    def reduce(self) -> Optional[tuple]:
        if self.graph is not None:
            table_obj = self.graph.resolve_object_for_name(
                self.args["table"],
                ["table", "__table"])
            if table_obj is not None:
                self.args["table_id"] = table_obj.id
                return ({self}, [])
            else:
                self.add_error(f"Can't find table with name \"{self.args['table']}\".")

        return None
