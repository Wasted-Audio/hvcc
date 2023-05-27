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

from typing import Callable, Dict, List

from .HeavyObject import HeavyObject


class ControlPrint(HeavyObject):
    """Prints the first value in a message to the console"""

    preamble = "cPrint"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvControlPrint.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvControlPrint.h", "HvControlPrint.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [f"cPrint_onMessage(_c, m, \"{args['label']}\");"]

    @classmethod
    def get_C_decl(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_impl(
        cls,
        obj_type: str,
        obj_id: int,
        on_message_list: List,
        get_obj_class: Callable,
        objects: Dict
    ) -> List[str]:
        return []
