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

from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject
from .HeavyGraph import HeavyGraph


class HLangLine(HeavyLangObject):
    """ Translates HeavyLang object [line] to HeavyIR [__line] or [__line~f].
    """

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: 'HeavyGraph',
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "line"
        super().__init__("line", args, graph,
                         num_inlets=2,
                         num_outlets=1,
                         annotations=annotations)

    def reduce(self) -> tuple:
        if self.has_outlet_connection_format("f"):
            x = HeavyIrObject("__line~f", self.args)
        elif self.has_outlet_connection_format("c"):
            x = HeavyIrObject("__line", self.args)
        else:
            self.add_error("Unknown inlet configuration.")

        return ({x}, self.get_connection_move_list(x))
