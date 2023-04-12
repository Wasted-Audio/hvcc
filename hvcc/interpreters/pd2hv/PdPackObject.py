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

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class PdPackObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type == "pack"
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        self.values = []

        if len(self.obj_args) == 0:
            self.values = [0.0, 0.0]

        for x in self.obj_args:
            try:
                self.values.append(float(x))
            except Exception:
                if x in {"f", "float"}:
                    self.values.append(0.0)
                else:
                    self.add_error(
                        f"\"{x}\" argument to [pack] object not supported.",
                        NotificationEnum.ERROR_PACK_FLOAT_ARGUMENTS)

    def to_hv(self) -> Dict:
        return {
            "type": "__pack",
            "args": {
                "values": self.values
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
