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


class ControlVar(HeavyObject):
    """An object which holds a variable. In this case only a float.
    NOTE(mhroth): maybe in the future this can hold any data structure, such as
    a generic message. At the moment, the memory churn is deemed unnecessary.
    """

    c_struct = "ControlVar"
    preamble = "cVar"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvControlVar.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvControlVar.h", "HvControlVar.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        if isinstance(args["k"], str):
            return [
                "cVar_init_s(&cVar_{0}, \"{1}\");".format(
                    obj_id,
                    args["k"])]
        else:
            return [
                "cVar_init_f(&cVar_{0}, {1}f);".format(
                    obj_id,
                    float(args["k"]))]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "cVar_onMessage(_c, &Context(_c)->cVar_{0}, {1}, m, &cVar_{0}_sendMessage);".format(
                obj_id,
                inlet_index)
        ]
