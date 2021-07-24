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

from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject


class HLangVar(HeavyLangObject):

    def __init__(self, obj_type, args, graph, annotations=None):
        HeavyLangObject.__init__(self, "var", args, graph, annotations=annotations)

    def reduce(self):
        if self.has_inlet_connection_format("_") and self.has_outlet_connection_format("f"):
            x = HeavyIrObject("__var_k~f", self.args)
        elif self.has_inlet_connection_format("_") and self.has_outlet_connection_format("i"):
            x = HeavyIrObject("__var_k~i", self.args)
        elif self.has_inlet_connection_format(["_", "c"]) and self.has_outlet_connection_format("f"):
            x = HeavyIrObject("__var~f", self.args)
            x.id = self.id
            y = HeavyIrObject("__varread~f", {"var_id": self.id})

            move_list = []
            for c in [c for cc in self.inlet_connections for c in cc]:
                move_list.append((c, [c.copy(to_object=x)]))
            for c in [c for cc in self.outlet_connections for c in cc]:
                move_list.append((c, [c.copy(from_object=y)]))

            return ({x, y}, move_list)
        elif self.has_inlet_connection_format(["_", "c"]) and self.has_outlet_connection_format("i"):
            x = HeavyIrObject("__var~i", self.args)
            x.id = self.id
            y = HeavyIrObject("__varread~i", {"var_id": self.id})

            move_list = []
            for c in [c for cc in self.inlet_connections for c in cc]:
                move_list.append((c, [c.copy(to_object=x)]))
            for c in [c for cc in self.outlet_connections for c in cc]:
                move_list.append((c, [c.copy(from_object=y)]))

            return ({x, y}, move_list)
        elif self.has_inlet_connection_format(["_", "c"]) and self.has_outlet_connection_format(["_", "c"]):
            x = HeavyIrObject("__var", self.args)
        else:
            raise Exception()

        return ({x}, self.get_connection_move_list(x))
