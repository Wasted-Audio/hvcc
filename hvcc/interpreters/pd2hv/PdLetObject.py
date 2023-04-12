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

from typing import Optional, List, Dict

from .PdObject import PdObject


class PdLetObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type in {"inlet", "inlet~", "outlet", "outlet~"}
        super().__init__(obj_type, obj_args, pos_x, pos_y)
        self.let_index = 0

    def get_outlet_connection_type(self, outlet_index: int) -> Optional[str]:
        if len(self.obj_args) > 0 and self.obj_args[0] in {"-->", "~f>", "~i>", "-~>"}:
            return self.obj_args[0]
        else:
            return super().get_outlet_connection_type(outlet_index)

    def to_hv(self) -> Dict:
        return {
            "type": self.obj_type.strip("~"),
            "args": {
                "name": "",  # Pd does not give an inlet name
                "index": self.let_index,
                "type": self.get_outlet_connection_type(self.let_index)
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
