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


class UnknownModelException(Exception):
    def __str__(self):
        return "Unknown NAM model used."


class SignalNam(HeavyObject):

    preamble = "sNam"

    @classmethod
    def get_C_struct(cls, obj_type: str = "") -> str:
        if obj_type == '__nam_nano~f':
            return "SignalNamNano"
        elif obj_type == '__nam_feather~f':
            return "SignalNamFeather"
        elif obj_type == '__nam_lite~f':
            return "SignalNamLite"
        elif obj_type == '__nam_standard~f':
            return "SignalNamStandard"
        else:
            raise UnknownModelException()

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalNam.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {
            "HvSignalNam.h",
            "HvSignalNam.c",
            "MicroNAM_C.h",
            "MicroNAM_C.cpp",
            "MicroNam/MicroNAM.h",
            "MicroNam/include/StandardNet.h",
            "MicroNam/include/NanoNet.h",
            "MicroNam/include/LiteNet.h",
            "MicroNam/include/FeatherNet.h"
        }

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: dict) -> list[str]:
        nam_file = Path(args["nam"])
        weights = to_symbol_stem(nam_file)

        if obj_type == '__nam_nano~f':
            return [f"sNam_nano_init(&sNam_{obj_id}, {weights}Weights);"]
        elif obj_type == '__nam_feather~f':
            return [f"sNam_feather_init(&sNam_{obj_id}, {weights}Weights);"]
        elif obj_type == '__nam_lite~f':
            return [f"sNam_lite_init(&sNam_{obj_id}, {weights}Weights);"]
        elif obj_type == '__nam_standard~f':
            return [f"sNam_standard_init(&sNam_{obj_id}, {weights}Weights);"]
        else:
            raise UnknownModelException()

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: str, args: dict) -> list[str]:
        if obj_type == '__nam_nano~f':
            return [f"sNam_nano_free(&sNam_{obj_id});"]
        elif obj_type == '__nam_feather~f':
            return [f"sNam_feather_free(&sNam_{obj_id});"]
        elif obj_type == '__nam_lite~f':
            return [f"sNam_lite_free(&sNam_{obj_id});"]
        elif obj_type == '__nam_standard~f':
            return [f"sNam_standard_free(&sNam_{obj_id});"]
        else:
            raise UnknownModelException()

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: dict) -> list[str]:
        if obj_type == '__nam_nano~f':
            function = "__hv_nam_nano_f(&sNam_{0}, VIf({1}), VOf({2}));"
        elif obj_type == '__nam_feather~f':
            function = "__hv_nam_feather_f(&sNam_{0}, VIf({1}), VOf({2}));"
        elif obj_type == '__nam_lite~f':
            function = "__hv_nam_lite_f(&sNam_{0}, VIf({1}), VOf({2}));"
        elif obj_type == '__nam_standard~f':
            function = "__hv_nam_standard_f(&sNam_{0}, VIf({1}), VOf({2}));"
        else:
            raise UnknownModelException()

        return [
            function.format(
                process_dict.id,
                cls._c_buffer(process_dict.inputBuffers[0]),
                cls._c_buffer(process_dict.outputBuffers[0]))
        ]

    @classmethod
    def get_C_gen_header_code(cls, obj_type: str, obj_id: str, args: dict) -> Optional[tuple[str, str]]:
        nam_file = Path(args["nam"])
        header_name = f"{to_symbol_stem(nam_file)}.h"

        header_str = convert_nam_to_header(nam_file)

        return header_name, header_str
