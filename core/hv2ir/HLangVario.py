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

from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject


class HLangVario(HeavyLangObject):

    def __init__(self, obj_type, args, graph, annotations=None):
        HeavyLangObject.__init__(self, "vario", args, graph, annotations=annotations)

    def reduce(self):
        var_obj = self.graph.resolve_object_for_name(self.name, "var")
        if var_obj is None:
            raise HeavyException("No corresponding \"var\" object found for object {0} in file {1}".format(
                self,
                self.graph.file))

        if self.has_inlet_connection_format("f") and self.has_outlet_connection_format("_"):
            x = HeavyIrObject("__varwrite~f", {"var_id": var_obj.id})
            return {x}, self.get_connection_move_list(x)

        elif self.has_inlet_connection_format("i") and self.has_outlet_connection_format("_"):
            x = HeavyIrObject("__varwrite~i", {"var_id": var_obj.id})
            return {x}, self.get_connection_move_list(x)

        elif self.has_inlet_connection_format("_") and self.has_outlet_connection_format("f"):
            x = HeavyIrObject("__varread~f", {"var_id": var_obj.id})
            return {x}, self.get_connection_move_list(x)

        elif self.has_inlet_connection_format("_") and self.has_outlet_connection_format("i"):
            x = HeavyIrObject("__varread~i", {"var_id": var_obj.id})
            return {x}, self.get_connection_move_list(x)

        else:
            raise Exception()
