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


from hvcc.types.IR import IRSignalList

from .HeavyObject import HeavyObject


class SignalTabreceive(HeavyObject):
    """Handles __tabreceive~f
    """

    c_struct = "SignalTabreceive"
    preamble = "sTabreceive"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalTabreceive.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalTabreceive.h", "HvSignalTabreceive.c"}

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: str, args: dict) -> list[str]:
        return []

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: dict) -> list[str]:
        return [
            "sTabreceive_init(&sTabreceive_{0}, &hTable_{1}, {2});".format(
                obj_id,
                args["table_id"],
                args["block_size"])
        ]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: str, inlet_index: int, args: dict) -> list[str]:
        return [f"sTabreceive_onMessage(_c, &Context(_c)->sTabreceive_{obj_id}, {inlet_index}, m, NULL);"]

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: dict) -> list[str]:

        return [
            "__hv_tabreceive_f(&sTabreceive_{0}, {1});".format(
                process_dict.id,
                ", ".join([f"VOf({cls._c_buffer(b)})" for b in process_dict.outputBuffers])
            )]
