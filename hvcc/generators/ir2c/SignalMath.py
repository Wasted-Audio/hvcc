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


class SignalMath(HeavyObject):
    """Handles the math objects.
    """

    # translation from operation to function preamble
    __OPERATION_DICT = {
        "__add~f": "__hv_add_f",
        "__add~i": "__hv_add_i",
        "__sub~f": "__hv_sub_f",
        "__sub~i": "__hv_sub_i",
        "__mul~f": "__hv_mul_f",
        "__mul~i": "__hv_mul_i",
        "__div~f": "__hv_div_f",
        "__div~i": "__hv_div_i",
        "__log2~f": "__hv_log2_f",
        "__cos~f": "__hv_cos_f",
        "__acos~f": "__hv_acos_f",
        "__cosh~f": "__hv_cosh_f",
        "__acosh~f": "__hv_acosh_f",
        "__sin~f": "__hv_sin_f",
        "__asin~f": "__hv_asin_f",
        "__sinh~f": "__hv_sinh_f",
        "__asinh~f": "__hv_asinh_f",
        "__tan~f": "__hv_tan_f",
        "__atan~f": "__hv_atan_f",
        "__atan2~f": "__hv_atan2_f",
        "__tanh~f": "__hv_tanh_f",
        "__atanh~f": "__hv_atanh_f",
        "__exp~f": "__hv_exp_f",
        "__pow~f": "__hv_pow_f",
        "__pow~i": "__hv_pow_i",
        "__sqrt~f": "__hv_sqrt_f",
        "__rsqrt~f": "__hv_rsqrt_f",
        "__abs~f": "__hv_abs_f",
        "__abs~i": "__hv_abs_i",
        "__max~f": "__hv_max_f",
        "__max~i": "__hv_max_i",
        "__min~f": "__hv_min_f",
        "__min~i": "__hv_min_i",
        "__neg~f": "__hv_neg_f",
        "__gt~f": "__hv_gt_f",
        "__gt~i": "__hv_gt_i",
        "__gte~f": "__hv_gte_f",
        "__gte~i": "__hv_gte_i",
        "__lt~f": "__hv_lt_f",
        "__lt~i": "__hv_lt_i",
        "__lte~f": "__hv_lte_f",
        "__lte~i": "__hv_lte_i",
        "__neq~f": "__hv_neq_f",
        "__fma~f": "__hv_fma_f",
        "__fms~f": "__hv_fms_f",
        "__floor~f": "__hv_floor_f",
        "__ceil~f": "__hv_ceil_f",
        "__cast~fi": "__hv_cast_fi",
        "__cast~if": "__hv_cast_if",
        "__and~f": "__hv_and_f",  # binary and
        "__andnot~f": "__hv_andnot_f",
        "__or~f": "__hv_or_f",  # binary or
    }

    @classmethod
    def handles_type(clazz, obj_type):
        """Returns true if the object type can be handled by this class
        """
        return obj_type in SignalMath.__OPERATION_DICT

    @classmethod
    def get_C_header_set(clazz):
        return {"HvMath.h"}

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        return [
            "{0}({1}, {2});".format(
                SignalMath.__OPERATION_DICT[obj_type],
                ", ".join(["VI{0}({1})".format(
                    "i" if b["type"] == "~i>" else "f",
                    HeavyObject._c_buffer(b)) for b in process_dict["inputBuffers"]]),
                ", ".join(["VO{0}({1})".format(
                    "i" if b["type"] == "~i>" else "f",
                    HeavyObject._c_buffer(b)) for b in process_dict["outputBuffers"]])
            )]
