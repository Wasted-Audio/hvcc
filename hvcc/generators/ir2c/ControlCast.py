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


class ControlCast(HeavyObject):
    __OPERATION_DICT = {
        "__cast_b": "HV_CAST_BANG",
        "__cast_f": "HV_CAST_FLOAT",
        "__cast_s": "HV_CAST_SYMBOL"
    }

    c_struct = "ControlCast"
    preamble = "cCast"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvControlCast.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvControlCast.h", "HvControlCast.c"}

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "cCast_onMessage(_c, {1}, 0, m, &cCast_{0}_sendMessage);".format(
                obj_id,
                ControlCast.__OPERATION_DICT[obj_type])
        ]
