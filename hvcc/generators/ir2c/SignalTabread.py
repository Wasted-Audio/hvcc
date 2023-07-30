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


class SignalTabread(HeavyObject):
    """Handles __tabread~if, __tabread~f, __tabreadu~f, __tabread_stoppable~f
    """

    c_struct = "SignalTabread"
    preamble = "sTabread"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalTabread.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalTabread.h", "HvSignalTabread.c"}

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            "sTabread_init(&sTabread_{0}, &hTable_{1}, {2});".format(
                obj_id,
                args["table_id"],
                "true" if obj_type in {"__tabread~f", "__tabread_stoppable~f"} else "false")]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        if obj_type in ["__tabread~f", "__tabreadu~f", "__tabread_stoppable~f"]:
            return [
                "sTabread_onMessage(_c, &Context(_c)->sTabread_{0}, {1}, m, &sTabread_{0}_sendMessage);".format(
                    obj_id,
                    inlet_index)]
        else:  # "__tabread~if"
            return [f"sTabread_onMessage(_c, &Context(_c)->sTabread_{obj_id}, {inlet_index}, m, NULL);"]

    @classmethod
    def get_C_process(cls, process_dict: Dict, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        if obj_type == "__tabread~if":
            return [
                "__hv_tabread_if(&sTabread_{0}, {1}, {2});".format(
                    process_dict["id"],
                    ", ".join([f"VIi({cls._c_buffer(b)})" for b in process_dict["inputBuffers"]]),
                    ", ".join([f"VOf({cls._c_buffer(b)})" for b in process_dict["outputBuffers"]])
                )]
        elif obj_type == "__tabread~f":
            return [
                "__hv_tabread_f(&sTabread_{0}, {1});".format(
                    process_dict["id"],
                    ", ".join([f"VOf({cls._c_buffer(b)})" for b in process_dict["outputBuffers"]])
                )]
        elif obj_type == "__tabread_stoppable~f":
            return [
                "__hv_tabread_stoppable_f(this, &sTabread_{0}, {1}, &{2}_{0}_sendMessage);".format(
                    process_dict["id"],
                    ", ".join([f"VOf({cls._c_buffer(b)})" for b in process_dict["outputBuffers"]]),
                    cls.preamble
                )]
        elif obj_type == "__tabreadu~f":
            return [
                "__hv_tabreadu_f(&sTabread_{0}, {1});".format(
                    process_dict["id"],
                    ", ".join([f"VOf({cls._c_buffer(b)})" for b in process_dict["outputBuffers"]])
                )]
        else:
            raise Exception()
