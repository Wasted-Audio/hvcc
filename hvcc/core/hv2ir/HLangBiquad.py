# Copyright (C) 2014-2018 Enzien Audio, Ltd.
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

from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject


class HLangBiquad(HeavyLangObject):
    """ Translates HeavyLang object biquad to HeavyIR biquad~.
    """

    # used to detect valid connection configuration formats
    __re_fmt_k = re.compile("[f_][c_]+")
    __re_fmt_f = re.compile("[f_]+")

    def __init__(self, obj_type, args, graph, annotations=None):
        HeavyLangObject.__init__(self, "biquad", args, graph, num_inlets=6, num_outlets=1, annotations=annotations)

    def reduce(self):
        fmt = self._get_connection_format(self.inlet_connections)
        if HLangBiquad.__re_fmt_k.search(fmt):
            x = HeavyIrObject("__biquad_k~f", self.args)
            return {x}, self.get_connection_move_list(x)

        elif HLangBiquad.__re_fmt_f.search(fmt):
            x = HeavyIrObject("__biquad~f", self.args)
            return {x}, self.get_connection_move_list(x)

        else:
            raise HeavyException("Unsupported connection format to biquad: {0}".format(fmt))
