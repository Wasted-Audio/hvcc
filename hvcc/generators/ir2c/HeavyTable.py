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


class HeavyTable(HeavyObject):
    """Outputs code for the table object.
    """

    c_struct = "HvTable"
    preamble = "hTable"

    @classmethod
    def get_C_header_set(self) -> set:
        return {"HvTable.h"}

    @classmethod
    def get_C_file_set(self) -> set:
        return {"HvTable.h", "HvTable.c"}

    @classmethod
    def get_table_data_decl(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        if len(args.get("values", [])) > 0:
            return [
                "float hTable_{0}_data[{1}] = {{{2}}};".format(
                    obj_id,
                    len(args["values"]),
                    ", ".join([f"{float(v)}f" for v in args["values"]]))]
        else:
            return []

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        if len(args.get("values", [])) > 0:
            return [
                "hTable_initWithData(&hTable_{0}, {1}, hTable_{0}_data);".format(
                    obj_id,
                    len(args["values"]))]
        else:
            return [
                "hTable_init(&hTable_{0}, {1});".format(
                    obj_id,
                    int(args.get("size", 256)))]  # 1KB default memory allocation

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return ["{0}_free(&{0}_{1});".format(
            cls.preamble,
            obj_id)]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [
            f"hTable_onMessage(_c, &Context(_c)->hTable_{obj_id}, {inlet_index}, m, &hTable_{obj_id}_sendMessage);"
        ]
