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

from typing import Dict, List

from .HeavyObject import HeavyObject


class ControlTabwrite(HeavyObject):

    c_struct = "ControlTabwrite"
    preamble = "cTabwrite"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvControlTabwrite.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvControlTabwrite.h", "HvControlTabwrite.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            "cTabwrite_init(&cTabwrite_{0}, &hTable_{1}); // {2}".format(
                obj_id,
                args["table_id"],
                args["table"])
        ]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [
            "cTabwrite_onMessage(_c, &Context(_c)->cTabwrite_{0}, {1}, m, &cTabwrite_{0}_sendMessage);".format(
                obj_id,
                inlet_index)
        ]
