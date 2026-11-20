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

from typing import Any

from hvcc.types.Heavy import Heavy, HvPos

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class PdTriggerObject(PdObject):
    def __init__(
        self,
        obj_type: str,
        obj_args: list | None = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type in {"trigger", "t"}
        obj_args = self.__convert_args(obj_args) if obj_args is not None else []
        super().__init__("trigger", obj_args, pos_x, pos_y)

        # convert all numeric casts to "f"
        for i, a in enumerate(self.obj_args):
            self.obj_args[i] = "f" if self.__is_float(a) else a

        if len(self.obj_args) == 0:
            self.obj_args = ["b", "b"]
            self.add_warning("A trigger with no arguments defualts to [t b b].")
        if obj_args is not None and not (set(obj_args) <= {"a", "f", "s", "b"}):
            self.add_error(
                "Heavy only supports arguments 'a', 'f', 's', and 'b'.",
                NotificationEnum.ERROR_TRIGGER_ABFS)

    def to_hv(self) -> Heavy:
        return Heavy(
            type="sequence",
            args={
                "casts": self.obj_args
            },
            properties=HvPos(x=self.pos_x, y=self.pos_y)
        )

    @classmethod
    def __is_float(cls, x: Any) -> bool:
        """ Returns True if the input can be converted to a float. False otherwise.
        """
        try:
            float(x)
            return True
        except ValueError:
            return False

    @classmethod
    def __convert_args(cls, args: list) -> list:
        """ Converts full argument types to their corresponding shorthand notation.
        """
        shorthand_map = {
            "any": "a",
            "float": "f",
            "symbol": "s",
            "bang": "b"
        }
        return [shorthand_map.get(arg, arg) for arg in args]
