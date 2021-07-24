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


class HIrReceive(HeavyIrObject):
    """ A specific implementation of the __receive object.
    """

    def __init__(self, obj_type, args=None, graph=None, annotations=None):
        HeavyIrObject.__init__(self, "__receive", args=args, graph=graph, annotations=annotations)
        if args["extern"]:
            # externed receivers must contain only alphanumeric characters or underscores,
            # so that the names can be easily and transparently turned into code
            if re.search("\W", args["name"]):
                self.add_error("Parameter and Event names may only contain"
                               f"alphanumeric characters or underscore: '{args['name']}'")
