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

from .HeavyLangObject import HeavyLangObject
from .HIrSend import HIrSend


class HLangSend(HeavyLangObject):
    """ Translates HeavyLang object [send] to HeavyIR [__send] if control,
        otherwise for signal connections it will remove the send~/receive~ objects
        and reorder the graph.
    """

    def __init__(self, obj_type, args, graph, annotations=None):
        HeavyLangObject.__init__(self, "send", args, graph, annotations=annotations)

    def reduce(self):
        if self.has_inlet_connection_format("c"):
            ir_args = dict(self.args)
            ir_args["hash"] = "0x{0:X}".format(HeavyLangObject.get_hash(ir_args["name"]))
            x = HIrSend("__send", ir_args, annotations=self.annotations)
            return ({x}, self.get_connection_move_list(x))

        elif self.has_inlet_connection_format("f"):
            # this case should be handled already in HeavyGraph.remap_send_receive()
            # clean up just in case
            return (set(), [])

        elif self.has_inlet_connection_format("_"):
            self.add_warning("send~ object doesn't have any inputs, this one is being removed.")
            return (set(), [])

        elif self.has_inlet_connection_format("m"):
            self.add_error(
                "Inlet can support either control or signal connections, "
                "but not both at the same time.")

        else:
            fmt = self._get_connection_format(self.inlet_connections)
            self.add_error("Unknown inlet configuration: {0}".format(fmt))
