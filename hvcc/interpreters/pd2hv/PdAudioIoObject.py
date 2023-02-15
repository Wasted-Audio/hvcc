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


class PdAudioIoObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type in {"adc~", "dac~"}
        super().__init__(obj_type, obj_args, pos_x, pos_y)

    def validate_configuration(self) -> None:
        # ensure that only signal connections are made to the dac
        for i, connections in self._inlet_connections.items():
            if any(c.conn_type == "-->" for c in connections):
                self.add_error(
                    f"{self.obj_type} does not support control connections (inlet {i}). They should be removed.",
                    NotificationEnum.ERROR_UNSUPPORTED_CONNECTION)

    def to_hv(self) -> Dict:
        return {
            "type": self.obj_type.strip("~"),
            "args": {
                "channels": [1, 2] if len(self.obj_args) == 0 else [int(a) for a in self.obj_args]
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
