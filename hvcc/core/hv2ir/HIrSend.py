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
from .HeavyIrObject import HeavyIrObject


class HIrSend(HeavyIrObject):
    """ A specific implementation of the __send object.
    """

    def __init__(self, obj_type, args=None, graph=None, annotations=None):
        HeavyIrObject.__init__(self, "__send", args=args, graph=graph, annotations=annotations)
        if args["extern"]:
            # output parameters must contain only alphanumeric characters or underscores,
            # so that the names can be easily and transparently turned into code
            if re.search("\W", args["name"]):
                self.add_error(f"Parameter and Event names may only contain \
                                alphanumeric characters or underscore: '{args['name']}'")

    def get_ir_control_list(self):
        receive_objs = self.graph.resolve_objects_for_name(self.name, "__receive")
        on_message_list = [x for o in receive_objs for x in o.get_ir_on_message(inlet_index=0)]
        return [{
            "id": self.id,
            "onMessage": [on_message_list],
            "extern": self.args["extern"],
            "hash": self.args["hash"],
            "display": self.args["name"],
            "name": (("_" + self.args["name"]) if re.match("\d", self.args["name"]) else self.args["name"])
        }]
