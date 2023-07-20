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
from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


class HLangSystem(HeavyLangObject):
    """ Handles the HeavyLang "system" object.
    """

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: 'HeavyGraph',
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "system"
        super().__init__(obj_type, args, graph,
                         num_inlets=1,
                         num_outlets=1,
                         annotations=annotations)

    def reduce(self) -> tuple:
        x = HeavyIrObject("__system", self.args)
        return ({x}, self.get_connection_move_list(x))
