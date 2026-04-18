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

from typing import Optional
from pathlib import Path

from .HeavyObject import HeavyObject
from .SignalNamHeader import convert_nam_to_header, to_symbol_stem
from hvcc.types.IR import IRSignalList


class SignalNam(HeavyObject):

    c_struct = "SignalNam"
    preamble = "sNam"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalNam.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {
            "HvSignalNam.h",
            "HvSignalNam.c",
            "MicroNam/MicroNAM_C.h",
            "MicroNam/MicroNAM_C.cpp",
            "MicroNam/MicroNAM.h",
            "MicroNam/include/StandardNet.h",
            "MicroNam/include/NanoNet.h",
            "MicroNam/include/LiteNet.h",
            "MicroNam/include/FeatherNet.h"
        }

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: dict) -> list[str]:
        nam_file = Path(args["nam"])
        return [f"sNam_init(&sNam_{obj_id}, {to_symbol_stem(nam_file)}Weights);"]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: str, args: dict) -> list[str]:
        return []  # nothing to free

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: str, inlet_index: int, args: dict) -> list[str]:
        return [
            "sNam_onMessage(_c, &Context(_c)->sNam_{0}, {1}, m);".format(
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: dict) -> list[str]:
        return [
            "__hv_nam_f(&sNam_{0}, {1}, {2});".format(
                process_dict.id,
                cls._c_buffer(process_dict.inputBuffers[0]),
                cls._c_buffer(process_dict.outputBuffers[0]))
        ]

    @classmethod
    def get_C_gen_header_code(cls, obj_type: str, obj_id: str, args: dict) -> Optional[tuple[str, str]]:
        nam_file = Path(args["nam"])
        header_name = f"{to_symbol_stem(nam_file)}.h"

        header_str, _ = convert_nam_to_header(nam_file)

        return header_name, header_str
