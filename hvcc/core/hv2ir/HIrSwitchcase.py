# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023 Wasted Audio
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

from typing import Dict, Optional

from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


class HIrSwitchcase(HeavyIrObject):
    """ A specific implementation of the __switchcase object.
    """

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional[HeavyGraph] = None,
        annotations: Optional[Dict] = None
    ) -> None:
        if args is not None:
            num_cases = len(args["cases"])
        else:
            num_cases = 0

        super().__init__("__switchcase",
                         args=args,
                         graph=graph,
                         num_inlets=1,
                         num_outlets=num_cases + 1,
                         annotations=annotations)
