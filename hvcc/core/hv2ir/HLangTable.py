# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023-2024 Wasted Audio
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
from typing import Optional, Dict

from .HeavyLangObject import HeavyLangObject
from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


class HLangTable(HeavyLangObject):
    """ Handles the HeavyLang "table" object.
    """

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: 'HeavyGraph',
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "table"
        super().__init__(obj_type, args, graph, annotations=annotations)

        # the values argument overrides the size argument
        if len(self.args.get("values", [])) > 0:
            self.args["size"] = len(self.args["values"])

        if self.args["extern"]:
            # externed tables must contain only alphanumeric characters or underscores,
            # so that the names can be easily and transparently turned into code
            if re.search(r"\W", args["name"]):
                self.add_error(f"Table names may only contain alphanumeric characters \
                                or underscore: '{args['name']}'")

    def reduce(self) -> tuple:
        x = HeavyIrObject("__table", self.args)
        # ensure that __table object maintains the same id as the original
        # table object. The latter is referenced by id from other objects.
        # Consistency must be maintained.
        x.id = self.id
        return ({x}, self.get_connection_move_list(x))
