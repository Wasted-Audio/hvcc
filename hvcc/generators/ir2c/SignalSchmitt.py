# Copyright (C) 2026 Wasted Audio
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


class SignalSchmitt(HeavyObject):

    c_struct = "SignalSchmitt"
    preamble = "sSchmitt"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalSchmitt.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalSchmitt.h", "HvSignalSchmitt.c"}

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return [
            "sSchmitt_init(&sSchmitt_{0}, {1}, {2}, {3}, {4});".format(
                obj_id,
                float(args["trigValue"]),
                float(args["trigDebounce"]),
                float(args["restValue"]),
                float(args["restDebounce"]))
        ]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: str, inlet_index: int, args: Dict) -> List[str]:
        return [
            "{0}_onMessage(_c, &Context(_c)->{0}_{1}, {2}, m);".format(
                cls.preamble,
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return [
            "__hv_schmitt_f(this, &sSchmitt_{0}, VIf({1}), &sSchmitt_{0}_sendMessage);".format(
                process_dict.id,
                cls._c_buffer(process_dict.inputBuffers[0])
            )
        ]
