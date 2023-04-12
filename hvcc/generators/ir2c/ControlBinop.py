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


class ControlBinop(HeavyObject):
    # a dictionary translating from the operation argument to the C case
    __OPERATION_DICT = {
        "__add": "HV_BINOP_ADD",
        "__add_k": "HV_BINOP_ADD",
        "__sub": "HV_BINOP_SUBTRACT",
        "__sub_k": "HV_BINOP_SUBTRACT",
        "__mul": "HV_BINOP_MULTIPLY",
        "__mul_k": "HV_BINOP_MULTIPLY",
        "__div": "HV_BINOP_DIVIDE",
        "__div_k": "HV_BINOP_DIVIDE",
        "__intdiv": "HV_BINOP_INT_DIV",
        "__intdiv_k": "HV_BINOP_INT_DIV",
        "__shiftleft": "HV_BINOP_BIT_LEFTSHIFT",
        "__shiftleft_k": "HV_BINOP_BIT_LEFTSHIFT",
        "__shiftright": "HV_BINOP_BIT_RIGHTSHIFT",
        "__shiftright_k": "HV_BINOP_BIT_RIGHTSHIFT",
        "__and": "HV_BINOP_BIT_AND",
        "__and_k": "HV_BINOP_BIT_AND",
        "__or": "HV_BINOP_BIT_OR",
        "__or_k": "HV_BINOP_BIT_OR",
        "__^": "HV_BINOP_BIT_XOR",
        "__==": "HV_BINOP_EQL_EQL",
        "__!=": "HV_BINOP_NOT_EQL",
        "__logand": "HV_BINOP_LOGICAL_AND",
        "__logand_k": "HV_BINOP_LOGICAL_AND",
        "__logor": "HV_BINOP_LOGICAL_OR",
        "__logor_k": "HV_BINOP_LOGICAL_OR",
        "__eq": "HV_BINOP_EQ",
        "__eq_k": "HV_BINOP_EQ",
        "__neq": "HV_BINOP_NEQ",
        "__neq_k": "HV_BINOP_NEQ",
        "__lt": "HV_BINOP_LESS_THAN",
        "__lt_k": "HV_BINOP_LESS_THAN",
        "__lte": "HV_BINOP_LESS_THAN_EQL",
        "__lte_k": "HV_BINOP_LESS_THAN_EQL",
        "__gt": "HV_BINOP_GREATER_THAN",
        "__gt_k": "HV_BINOP_GREATER_THAN",
        "__gte": "HV_BINOP_GREATER_THAN_EQL",
        "__gte_k": "HV_BINOP_GREATER_THAN_EQL",
        "__max": "HV_BINOP_MAX",
        "__max_k": "HV_BINOP_MAX",
        "__min": "HV_BINOP_MIN",
        "__min_k": "HV_BINOP_MIN",
        "__pow": "HV_BINOP_POW",
        "__pow_k": "HV_BINOP_POW",
        "__atan2": "HV_BINOP_ATAN2",
        "__atan2_k": "HV_BINOP_ATAN2",
        "__unimod": "HV_BINOP_MOD_UNIPOLAR",
        "__unimod_k": "HV_BINOP_MOD_UNIPOLAR",
        "__bimod": "HV_BINOP_MOD_BIPOLAR",
        "__bimod_k": "HV_BINOP_MOD_BIPOLAR"
    }

    c_struct = "ControlBinop"
    preamble = "cBinop"

    @classmethod
    def handles_type(cls, obj_type: str) -> bool:
        """Returns true if the object type can be handled by this class
        """
        return obj_type in cls.__OPERATION_DICT

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvControlBinop.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvControlBinop.h", "HvControlBinop.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        if obj_type.endswith("_k"):
            return []
        else:
            obj_arg = float(list(args.values())[0])
            return [f"cBinop_init(&cBinop_{obj_id}, {obj_arg}f); // {obj_type}"]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []  # no need to free any control binop objects

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        if obj_type.endswith("_k"):
            return [
                "cBinop_k_onMessage(_c, NULL, {0}, {1}f, {2}, m, &cBinop_{3}_sendMessage);".format(
                    cls.__OPERATION_DICT[obj_type[:-2]],
                    float(args["k"]),
                    inlet_index,
                    obj_id)
            ]
        else:
            return [
                "cBinop_onMessage(_c, &Context(_c)->cBinop_{0}, {1}, {2}, m, &cBinop_{0}_sendMessage);".format(
                    obj_id,
                    cls.__OPERATION_DICT[obj_type],
                    inlet_index)
            ]
