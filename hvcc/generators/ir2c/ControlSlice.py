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


class ControlSlice(HeavyObject):

    c_struct = "ControlSlice"
    preamble = "cSlice"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvControlSlice.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvControlSlice.h", "HvControlSlice.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            "cSlice_init(&cSlice_{0}, {1}, {2});".format(
                obj_id,
                int(args["index"]),
                int(args["length"]))]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []  # nothing to free

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "cSlice_onMessage(_c, &Context(_c)->cSlice_{0}, {1}, m, &cSlice_{0}_sendMessage);".format(
                obj_id,
                inlet_index)
        ]
