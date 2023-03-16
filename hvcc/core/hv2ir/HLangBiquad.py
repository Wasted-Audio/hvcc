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

import re
from typing import Optional, Dict

from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject
from .HeavyGraph import HeavyGraph


class HLangBiquad(HeavyLangObject):
    """ Translates HeavyLang object biquad to HeavyIR biquad~.
    """

    # used to detect valid connection configuration formats
    __re_fmt_k = re.compile("[f_][c_]+")
    __re_fmt_f = re.compile("[f_]+")

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: 'HeavyGraph',
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "biquad"
        super().__init__(obj_type, args, graph,
                         num_inlets=6,
                         num_outlets=1,
                         annotations=annotations)

    def reduce(self) -> tuple:
        fmt = self._get_connection_format(self.inlet_connections)
        if self.__re_fmt_k.search(fmt):
            x = HeavyIrObject("__biquad_k~f", self.args)
            return {x}, self.get_connection_move_list(x)

        elif self.__re_fmt_f.search(fmt):
            x = HeavyIrObject("__biquad~f", self.args)
            return {x}, self.get_connection_move_list(x)

        else:
            raise HeavyException(f"Unsupported connection format to biquad: {fmt}")
