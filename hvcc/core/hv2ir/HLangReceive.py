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

from typing import Optional, Dict

from .HeavyLangObject import HeavyLangObject
from .HIrReceive import HIrReceive
from .HeavyGraph import HeavyGraph


class HLangReceive(HeavyLangObject):
    """ Translates HeavyLang object [receive] to HeavyIR [__receive if control,
        otherwise for signal connections it will remove the send~/receive~ objects
        and reorder the graph.
    """

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: 'HeavyGraph',
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "receive"
        super().__init__(obj_type, args, graph, annotations=annotations)

    def reduce(self) -> Optional[tuple]:
        if self.has_outlet_connection_format(["c"]):
            x = HIrReceive("__receive", self.args, annotations=self.annotations)
            return ({x}, self.get_connection_move_list(x))

        elif self.has_outlet_connection_format(["f"]):
            # this case should be handled already in HeavyGraph.remap_send_receive()
            # clean up just in case
            return (set(), [])

        elif self.has_outlet_connection_format("_"):
            self.add_warning("receive~ object doesn't have any outputs, this one is being removed.")
            return (set(), [])

        else:
            fmt = self._get_connection_format(self.outlet_connections)
            self.add_error(f"Unknown outlet configuration: {fmt}")
            return None
