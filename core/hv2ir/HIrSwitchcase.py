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

class HIrSwitchcase(HeavyIrObject):
    """ A specific implementation of the __switchcase object.
    """

    def __init__(self, obj_type, args=None, graph=None, annotations=None):
        HeavyIrObject.__init__(self, "__switchcase",
            args=args,
            graph=graph,
            num_inlets=1,
            num_outlets=len(args["cases"])+1,
            annotations=annotations)
