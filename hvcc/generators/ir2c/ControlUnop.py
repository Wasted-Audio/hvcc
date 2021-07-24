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


class ControlUnop(HeavyObject):
    # a dictionary translating from the operation argument to the C case
    __OPERATION_DICT = {
        "__cos": "HV_UNOP_COS",
        "__acos": "HV_UNOP_ACOS",
        "__cosh": "HV_UNOP_COSH",
        "__acosh": "HV_UNOP_ACOSH",
        "__sin": "HV_UNOP_SIN",
        "__asin": "HV_UNOP_ASIN",
        "__sinh": "HV_UNOP_SINH",
        "__asinh": "HV_UNOP_ASINH",
        "__tan": "HV_UNOP_TAN",
        "__atan": "HV_UNOP_ATAN",
        "__tanh": "HV_UNOP_TANH",
        "__atanh": "HV_UNOP_ATANH",
        "__log": "HV_UNOP_LOG",
        "__log10": "HV_UNOP_LOG10",
        "__log2": "HV_UNOP_LOG2",
        "__exp": "HV_UNOP_EXP",
        "__abs": "HV_UNOP_ABS",
        "__sqrt": "HV_UNOP_SQRT",
        "__ceil": "HV_UNOP_CEIL",
        "__floor": "HV_UNOP_FLOOR",
        "__round": "HV_UNOP_ROUND"
    }

    c_struct = "ControlUnop"
    preamble = "cUnop"

    @classmethod
    def handles_type(clazz, obj_type):
        """Returns true if the object type can be handled by this class
        """
        return obj_type in ControlUnop.__OPERATION_DICT

    @classmethod
    def get_C_header_set(clazz):
        return {"HvControlUnop.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvControlUnop.h", "HvControlUnop.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "cUnop_onMessage(_c, {1}, m, &cUnop_{0}_sendMessage);".format(
                obj_id,
                ControlUnop.__OPERATION_DICT[obj_type])
        ]
