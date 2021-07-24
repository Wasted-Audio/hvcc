# Copyright (C) 2014-2018 Enzien Audio, Ltd.
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

from .HeavyObject import HeavyObject


class HeavyTable(HeavyObject):
    """Outputs code for the table object.
    """

    c_struct = "HvTable"
    preamble = "hTable"

    @classmethod
    def get_C_header_set(self):
        return {"HvTable.h"}

    @classmethod
    def get_C_file_set(self):
        return {"HvTable.h", "HvTable.c"}

    @classmethod
    def get_C_decl(clazz, obj_type, obj_id, args):
        return [
            f"{clazz.preamble}_{obj_id}_sendMessage(HeavyContextInterface *, int, const HvMessage *);"
        ]

    @classmethod
    def get_table_data_decl(clazz, obj_type, obj_id, args):
        if len(args.get("values", [])) > 0:
            return [
                "float hTable_{0}_data[{1}] = {{{2}}};".format(
                    obj_id,
                    len(args["values"]),
                    ", ".join(["{0}f".format(float(v)) for v in args["values"]]))]
        else:
            return []

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
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
    def get_C_free(clazz, obj_type, obj_id, args):
        return ["{0}_free(&{0}_{1});".format(clazz.preamble, obj_id)]

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "hTable_onMessage(_c, &Context(_c)->hTable_{0}, {1}, m, &hTable_{0}_sendMessage);".format(
                obj_id,
                inlet_index)
        ]
