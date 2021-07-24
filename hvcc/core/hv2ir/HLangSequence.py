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

from .Connection import Connection
from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject


class HLangSequence(HeavyLangObject):
    def __init__(self, obj_type, args, graph, annotations=None):
        # get the number of outlets that this object has
        num_outlets = len(args[HeavyLangObject._HEAVY_LANG_DICT[obj_type]["args"][0]["name"]])
        HeavyLangObject.__init__(self, obj_type, args, graph,
                                 num_inlets=1,
                                 num_outlets=num_outlets,
                                 annotations=annotations)

    def reduce(self):
        cast_objs = []
        for a in self.args[self.name_for_arg()]:
            if a in ["a", "anything", "l", "list"]:
                cast_objs.append(None)  # pass through
            elif a in ["b", "bang"]:
                cast_objs.append(HeavyIrObject("__cast_b", {}))
            elif a in ["f", "float"]:
                cast_objs.append(HeavyIrObject("__cast_f", {}))
            elif a in ["s", "symbol"]:
                cast_objs.append(HeavyIrObject("__cast_s", {}))
            else:
                raise HeavyException(f"Unsupported cast type '{a}'.")

        connections = []

        # establish connections from inlet objects to the cast objects
        for ci in self.inlet_connections[0]:
            c_list = []
            for i in range(self.num_outlets - 1, -1, -1):
                if cast_objs[i] is not None:
                    c_list.append(Connection.copy(ci, to_object=cast_objs[i], inlet_index=0))
                else:
                    # for anything casts, establish a connection directly to the target
                    for co in self.outlet_connections[i]:
                        c_list.append(Connection.copy(ci, to_object=co.to_object, inlet_index=co.inlet_index))
            connections.append((ci, c_list))

        # establish connections from the cast objects
        for i in range(self.num_outlets - 1, -1, -1):
            if cast_objs[i] is not None:
                for c in self.outlet_connections[i]:
                    connections.append((c, [c.copy(from_object=cast_objs[i], outlet_index=0)]))

        # remove None objects from cast_objs. It was only used as a placeholder
        # to indicate that a cast passthrough
        objects = set(cast_objs)
        objects.discard(None)

        return (objects, connections)
