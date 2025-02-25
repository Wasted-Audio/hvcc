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

from typing import Dict, List

from .HeavyObject import HeavyObject

from hvcc.types.IR import IRSignalList


class SignalRPole(HeavyObject):
    """Handles the __rpole~f object.
    """

    c_struct = "SignalRpole"
    preamble = "sRPole"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalRPole.h", "HvSignalDel1.h", "HvMath.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {
            "HvSignalRPole.h", "HvSignalRPole.c",
            "HvSignalDel1.h", "HvSignalDel1.c",
            "HvMath.h"
        }

    @classmethod
    def get_C_def(cls, obj_type: str, obj_id: str) -> List[str]:
        return [f"SignalRPole sRPole_{obj_id};"]

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return [f"sRPole_init(&sRPole_{obj_id});"]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return [
            "__hv_rpole_f(&sRPole_{0}, VIf({1}), VIf({2}), VOf({3}));".format(
                process_dict.id,
                cls._c_buffer(process_dict.inputBuffers[0]),
                cls._c_buffer(process_dict.inputBuffers[1]),
                cls._c_buffer(process_dict.outputBuffers[0]))]
