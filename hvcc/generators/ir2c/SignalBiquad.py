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


class SignalBiquad(HeavyObject):
    """Handles the biquad~ object.
    """

    c_struct = "SignalBiquad"
    preamble = "sBiquad"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalBiquad.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalBiquad.h", "HvSignalBiquad.c"}

    @classmethod
    def get_C_def(cls, obj_type: str, obj_id: int) -> List[str]:
        if obj_type == "__biquad_k~f":
            return [f"SignalBiquad_k sBiquad_k_{obj_id};"]
        elif obj_type == "__biquad~f":
            return [f"SignalBiquad sBiquad_s_{obj_id};"]
        else:
            raise Exception()

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        if obj_type == "__biquad_k~f":
            return ["sBiquad_k_init(&sBiquad_k_{0}, {1}f, {2}f, {3}f, {4}f, {5}f);".format(
                obj_id,
                float(args["ff0"]),
                float(args["ff1"]),
                float(args["ff2"]),
                float(args["fb1"]),
                float(args["fb2"]))]
        elif obj_type == "__biquad~f":
            return [f"sBiquad_init(&sBiquad_s_{obj_id});"]
        else:
            raise Exception()

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [f"sBiquad_k_onMessage(&Context(_c)->sBiquad_k_{obj_id}, {inlet_index}, m);"]

    @classmethod
    def get_C_process(cls, process_dict: Dict, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        if obj_type == "__biquad_k~f":
            return [
                "__hv_biquad_k_f(&sBiquad_k_{0}, VIf({1}), VOf({2}));".format(
                    process_dict["id"],
                    cls._c_buffer(process_dict["inputBuffers"][0]),
                    cls._c_buffer(process_dict["outputBuffers"][0])
                )]
        elif obj_type == "__biquad~f":
            return [
                "__hv_biquad_f(&sBiquad_s_{0}, {1}, {2});".format(
                    process_dict["id"],
                    ", ".join([f"VIf({cls._c_buffer(b)})" for b in process_dict["inputBuffers"]]),
                    ", ".join([f"VOf({cls._c_buffer(b)})" for b in process_dict["outputBuffers"]])
                )]
        else:
            raise Exception(f"Incorrect obj_type {obj_type} for SignalBiquad")
