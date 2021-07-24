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

import random

from .HeavyLangObject import HeavyLangObject
from .HeavyIrObject import HeavyIrObject


class HLangRandom(HeavyLangObject):
    """ Handles the HeavyLang "print" object.
    """

    def __init__(self, obj_type, args, graph, annotations=None):
        assert obj_type == "random"
        HeavyLangObject.__init__(self, obj_type, args, graph,
                                 num_inlets=2,
                                 num_outlets=1,
                                 annotations=annotations)

    def reduce(self):
        self.args["seed"] = int(random.uniform(-2147483647, 2147483648))
        x = HeavyIrObject("__random", self.args)
        return ({x}, self.get_connection_move_list(x))
