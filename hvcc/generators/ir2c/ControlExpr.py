# Copyright (C) 2022-2025 Daniel Billotte, Wasted Audio
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

import re
from typing import Callable, Dict, List, Tuple

from .HeavyObject import HeavyObject


class ControlExpr(HeavyObject):
    c_struct = "ControlExpr"
    preamble = "cExpr"

    @classmethod
    def get_C_header_set(self) -> set:
        return {"HvControlExpr.h"}

    @classmethod
    def get_C_file_set(self) -> set:
        return {"HvControlExpr.h", "HvControlExpr.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        """ (Per object) code that gets inserted into from the Heavy_heavy ctor.
            Only if "ir[init]" == true
        """

        eval_f = f"&Heavy_{{{{name}}}}::{cls.preamble}_{obj_id}_evaluate"
        return [f"cExpr_init(&cExpr_{obj_id}, {eval_f});"]

    @classmethod
    def get_C_def(cls, obj_type: str, obj_id: str) -> List[str]:
        """ (Per object) code that gets inserted into the header file
            Only if "ir[init]" == true
        """

        lines = super().get_C_def(obj_type, obj_id)
        lines.append(f"static float {cls.preamble}_{obj_id}_evaluate(const float* args);")
        return lines

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: str, inlet_index: int, args: Dict) -> List[str]:
        """ (Per object) code that gets inserted into the c<PREAMBLE>_<OBJID>_sendMessage
            method in the .cpp file

            The get_C_onMessage method returns the code that will get inserted into
            the cReceive_<UID>_sendMessage method
        """

        return [
            "cExpr_onMessage(_c, &Context(_c)->cExpr_{0}, {1}, m, &cExpr_{0}_sendMessage);".format(
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_impl(
        cls,
        obj_type: str,
        obj_id: str,
        on_message_list: List,
        get_obj_class: Callable,
        objects: Dict,
        args: Dict
    ) -> List[str]:
        """
        (Per object) this creates the _sendMessage function that other objects use to
        send messages to this object.
        """

        lines = super().get_C_impl(obj_type, obj_id, on_message_list, get_obj_class, objects, args)
        expr = args["expressions"][0]
        bound_expr = bind_expr(expr, "args")
        lines.extend([
            "",
            f"float Heavy_{{{{name}}}}::{cls.preamble}_{obj_id}_evaluate(const float* args) {{",
            f"\treturn {bound_expr};",
            "}",
        ])
        return lines


"""
Below is code to rewrite the input expression into one that uses local variables
that have been cast to either float or int
"""


# todo(dgb): need to handle the 's' type
def var_n(a_name: str, var: str) -> str:
    parts = re.match(r"\$([fi])(\d+)", var)
    assert parts
    type = "float" if parts[1] == "f" else "int"
    return f"(({type})({a_name}[{int(parts[2])-1}]))"


def internal_expr(exp: str) -> str:
    """ Convert function names to C or internal names
    """

    internal: List[Tuple[str, str]] = [
        (r"\\,",            ","),
        (r"\bfact(?=\()",       "expr_fact"),
        (r"\bimodf(?=\()",      "expr_imodf"),
    ]

    for r in internal + hv_utils:
        exp = re.sub(r[0], r[1], exp)

    return exp


def bind_expr(exp: str = "$f1+2", a_name: str = "a") -> str:
    vars = re.findall(r"\$[fis]\d+", exp)
    exp = internal_expr(exp)

    if vars:
        # reverse list so we start replacing the bigger variables
        # and don't get conflicts
        vars.sort(reverse=True)
        for var in vars:
            exp = exp.replace(var, var_n(a_name, var))

    return exp


hv_utils: List[Tuple[str, str]] = [
    (r"\babs(?=\()",        "hv_abs_f"),
    (r"\bacos(?=\()",       "hv_acos_f"),
    (r"\bacosh(?=\()",      "hv_acosh_f"),
    (r"\basin(?=\()",       "hv_asin_f"),
    (r"\basinh(?=\()",      "hv_asinh_f"),
    (r"\batan(?=\()",       "hv_atan_f"),
    (r"\batanh(?=\()",      "hv_atanh_f"),
    (r"\batan2(?=\()",      "hv_atan2_f"),
    (r"\bcbrt(?=\()",       "hv_cbrt_f"),
    (r"\bceil(?=\()",       "hv_ceil_f"),
    (r"\bcopysign(?=\()",   "hv_copysign_f"),
    (r"\bcos(?=\()",        "hv_cos_f"),
    (r"\bcosh(?=\()",       "hv_cosh_f"),
    (r"\berf(?=\()",        "hv_erf_f"),
    (r"\berfc(?=\()",       "hv_erfc_f"),
    (r"\bexp(?=\()",        "hv_exp_f"),
    (r"\bexpm1(?=\()",      "hv_expm1_f"),
    (r"\bfinite(?=\()",     "hv_finite_f"),
    (r"\bfloor(?=\()",      "hv_floor_f"),
    (r"\bif(?=\()",         "hv_if_f"),
    (r"\bisinf(?=\()",      "hv_isinf_f"),
    (r"\bisnan(?=\()",      "hv_isnan_f"),
    (r"\bfmod(?=\()",       "hv_fmod_f"),
    (r"\bldexp(?=\()",      "hv_ldexp_f"),
    (r"\bln(?=\()",         "hv_ln_f"),
    (r"\blog(?=\()",        "hv_log_f"),
    (r"\blog10(?=\()",      "hv_log10_f"),
    (r"\blog1p(?=\()",      "hv_log1p_f"),
    (r"\bmax(?=\()",        "hv_max_f"),
    (r"\bmin(?=\()",        "hv_min_f"),
    (r"\bmodf(?=\()",       "hv_modf_f"),
    (r"\bpow(?=\()",        "hv_pow_f"),
    (r"\bremainder(?=\()",  "hv_remainder_f"),
    (r"\brint(?=\()",       "hv_rint_f"),
    (r"\bround(?=\()",      "hv_round_f"),
    (r"\bsin(?=\()",        "hv_sin_f"),
    (r"\bsinh(?=\()",       "hv_sinh_f"),
    (r"\bsqrt(?=\()",       "hv_sqrt_f"),
    (r"\btan(?=\()",        "hv_tan_f"),
    (r"\btanh(?=\()",       "hv_tanh_f"),
]
