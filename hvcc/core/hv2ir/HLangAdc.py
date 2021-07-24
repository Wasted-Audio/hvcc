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


class HLangAdc(HeavyLangObject):
    """ adc
    """

    def __init__(self, obj_type, args, graph, annotations=None):
        HeavyLangObject.__init__(
            self,
            obj_type,
            args, graph,
            num_inlets=0,
            num_outlets=len(args[HeavyLangObject._HEAVY_LANG_DICT[obj_type]["args"][0]["name"]]),
            annotations=annotations)

    def _resolved_outlet_type(self, outlet_index=0):
        return "~f>"

    def reduce(self):
        objects = set()
        connections = []

        # reduce a HeavyLang adc to a number of individual HeavyIR __inlet objects
        for i, channel_index in enumerate(self.args["channels"]):
            if len(self.outlet_connections[i]) > 0:  # if there are any connections to this inlet
                x = HeavyIrObject("__inlet", args={
                    "index": 127 + channel_index
                })
                x.outlet_buffers[0] = ("input", channel_index - 1)  # channel indicies are one-indexed
                objects.add(x)

                for c in self.outlet_connections[i]:
                    connections.append((c, [c.copy(from_object=x, outlet_index=0)]))

        return (objects, connections)
