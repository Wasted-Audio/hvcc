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


class SignalLine(HeavyObject):

    c_struct = "SignalLine"
    preamble = "sLine"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalLine.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalLine.h", "HvSignalLine.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            f"sLine_init(&sLine_{obj_id});"
        ]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []  # nothing to free

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [
            f"sLine_onMessage(_c, &Context(_c)->sLine_{obj_id}, {inlet_index}, m, NULL);"
        ]

    @classmethod
    def get_C_process(cls, process_dict: Dict, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            "__hv_line_f(&sLine_{0}, VOf({1}));".format(
                process_dict["id"],
                cls._c_buffer(process_dict["outputBuffers"][0])
            )
        ]
