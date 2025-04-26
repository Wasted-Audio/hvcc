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
from typing import Callable, Dict, List

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
    replace = [
        (r"\\,", ","),
        (r"\bmin\(", "fmin("),
        (r"\bmax\(", "fmax("),
        (r"\bln\(", "log("),
        (r"\bif\(", "hv_if_f("),
        (r"\bfact\(", "expr_fact("),
        (r"\bmodf\(", "hv_modf_f("),
        (r"\bimodf\(", "expr_imodf("),
        (r"\bround\(", "rint("),
        (r"\bnearbyint\(", "rint("),
    ]

    for r in replace:
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
