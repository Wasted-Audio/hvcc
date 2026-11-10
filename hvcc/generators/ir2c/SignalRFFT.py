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

from hvcc.types.IR import IRSignalList


class SignalRFFT(HeavyObject):

    c_struct = "SignalRFFT"
    preamble = "sRFFT"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalRFFT.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalRFFT.h", "HvSignalRFFT.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return [
            "sRFFT_init(&sRFFT_{0}, {1});".format(
                obj_id,
                args["block_size"])
        ]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: str, inlet_index: int, args: Dict) -> List[str]:
        return [
            "sRFFT_onMessage(_c, &Context(_c)->sRFFT_{0}, {1}, m, NULL);".format(
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        if obj_type == "__rfft~f":
            return [
                "__hv_rfft_f(&sRFFT_{0}, VIf({1}), VOf({2}), VOf({3}));".format(
                    process_dict.id,
                    cls._c_buffer(process_dict.inputBuffers[0]),
                    cls._c_buffer(process_dict.outputBuffers[0]),
                    cls._c_buffer(process_dict.outputBuffers[1])
                )
            ]
        else:
            raise Exception


class SignalRIFFT(HeavyObject):

    c_struct = "SignalRIFFT"
    preamble = "sRIFFT"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalRFFT.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalRFFT.h", "HvSignalRFFT.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        return [
            "sRIFFT_init(&sRIFFT_{0}, {1});".format(
                obj_id,
                args["block_size"])
        ]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: str, inlet_index: int, args: Dict) -> List[str]:
        return [
            "sRIFFT_onMessage(_c, &Context(_c)->sRIFFT_{0}, {1}, m, NULL);".format(
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        if obj_type == "__rifft~f":
            return [
                "__hv_rifft_f(&sRIFFT_{0}, VIf({1}), VIf({2}), VOf({3}));".format(
                    process_dict.id,
                    cls._c_buffer(process_dict.inputBuffers[0]),
                    cls._c_buffer(process_dict.inputBuffers[1]),
                    cls._c_buffer(process_dict.outputBuffers[0])
                )
            ]
        else:
            raise Exception
