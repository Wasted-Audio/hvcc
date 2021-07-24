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


class HLangDac(HeavyLangObject):
    """ Translates HeavyLang [dac] to HeavyIR [__add~f].
    """

    def __init__(self, obj_type, args, graph, annotations=None):
        assert obj_type == "dac"
        HeavyLangObject.__init__(
            self,
            obj_type,
            args, graph,
            num_inlets=len(args[HeavyLangObject._HEAVY_LANG_DICT["dac"]["args"][0]["name"]]),
            num_outlets=0,
            annotations=annotations)

    def reduce(self):
        objects = set()
        connections = []

        # reduce a HeavyLang dac to a number of individual HeavyIR __add~f objects
        for i, channel_index in enumerate(self.args["channels"]):
            if len(self.inlet_connections[i]) > 0:  # if there are any connections to this inlet
                x = HeavyIrObject("__add~f")
                x.inlet_buffers[1] = ("output", channel_index - 1)  # channel indicies are one-indexed
                x.outlet_buffers[0] = ("output", channel_index - 1)
                objects.add(x)

                for c in self.inlet_connections[i]:
                    connections.append((c, [c.copy(to_object=x, inlet_index=0)]))

        return (objects, connections)
