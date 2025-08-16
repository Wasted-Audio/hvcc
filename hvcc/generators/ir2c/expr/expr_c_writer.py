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
from typing import List, Union

from .expr_arpeggio_parser import ExprArpeggioParser, ExprNode, ParseExpr


class ExprCWriter:
    def __init__(self, expression: str):
        self.expression = expression
        self.expr_tree: ExprNode = ExprArpeggioParser.parse_to_ast(expression)
        self.parse_tree: ParseExpr = ExprArpeggioParser.parse(expression)
        self.num_buffers: Union[int, None] = None

    def to_ast(self) -> ExprNode:
        return self.expr_tree

    def to_parse_tree(self) -> ParseExpr:
        return self.parse_tree

    def to_c_simd(
        self,
        vv_in: Union[str, None] = None,
        v_out: str = ""
    ) -> List[str]:
        self._simd_bind_variables(vv_in)
        self._simd_replace_constants()
        return self._to_c_simd(v_out)

    def num_simd_buffers(self) -> int:
        if self.num_buffers is None:
            return len(self.to_c_simd())
        return self.num_buffers

    def to_c_nested(self) -> str:
        return self._to_c_nested()

    def _simd_replace_constants(self) -> None:
        self._simd_replace_constants_R(self.expr_tree)

    def _simd_replace_constants_R(self, tree: ExprNode) -> None:
        if tree.type == "func" and tree.value.startswith("_load_"):
            return  # don't re-replace anything

        for i in range(len(tree.nodes)):
            node = tree.nodes[i]
            if node.type == "num_i":
                tree.nodes[i] = ExprNode("func", "_load_i", [node])
            elif node.type == "num_f":
                tree.nodes[i] = ExprNode("func", "_load_f", [node])
            else:
                self._simd_replace_constants_R(node)

    def _simd_bind_variables(self, a_name: Union[str, None] = "A") -> None:
        assert a_name
        self._bind_vars_R(self.expr_tree, a_name)

    def _bind_vars_R(self, tree: ExprNode, a_name: str) -> None:
        if tree.type == "var":
            self._bind_var_node(tree, a_name)
        else:
            for node in tree.nodes:
                self._bind_vars_R(node, a_name)

    def _bind_var_node(self, node: ExprNode, a_name) -> None:
        if node.type != "var":
            print("called on non-var node: ", node)
            pass
        parts = re.match(r"\$(v|f)(\d+)", node.value)
        assert parts
        node.value = f"{a_name}[{int(parts[2])-1}]"
        node.type = "bound_var"

    class BufferAllocator:
        """Inner class for managing the swapping of buffers from
           output to input in successive calls.
        """
        def __init__(self) -> None:
            self._avail: set = set()
            self._next: int = 0

        def next(self) -> int:
            """If a buffer is available return it, otherwise
            allocate a new one and return it. """

            if len(self._avail) > 0:
                return self._avail.pop()
            nxt = self._next
            self._next += 1
            return nxt

        def free(self, n: int) -> None:
            """Return a buffer back to the pool to be reused"""
            self._avail.add(n)

        def num_allocated(self) -> int:
            """Return the buffers allocated in so far."""
            return self._next

    def _to_c_simd(self, v_out: str) -> List[str]:
        ba = self.BufferAllocator()
        lines: List[str] = []

        def _to_c_simd_R(expr_tree: ExprNode, r_vec: Union[str, None] = None) -> str:
            if expr_tree.type in ("num_i", "num_f", "var", "bound_var"):
                return expr_tree.value

            args = []
            buffers = []

            if (
                expr_tree.type == "func"
                and expr_tree.value.startswith("_load_")
            ):
                next_buf = f"Bf{ba.next()}"
                args.append(f"&{next_buf}")
                const_value = _to_c_simd_R(expr_tree.nodes[0])
                for i in range(8):
                    args.append(const_value)
            else:
                for node in expr_tree.nodes:
                    val = _to_c_simd_R(node)
                    args.append(val)
                    if isinstance(val, str) and val.startswith("Bf"):
                        buffers.append(val)
                if r_vec is not None:
                    next_buf = r_vec
                    args.append(next_buf)
                else:
                    next_buf = f"Bf{ba.next()}"
                    args.append(f"&{next_buf}")

            f_name = ExprOpMap.get_hv_func_simd(expr_tree.value)
            lines.append(f"{f_name}({', '.join(args)});")
            for b in buffers:
                ba.free(int(b[2]))

            return next_buf

        lines.append(_to_c_simd_R(self.expr_tree, v_out))
        self.num_buffers = ba.num_allocated()
        return lines

    def _to_c_nested(self) -> str:
        """Output C-code as nested function calls"""

        def _to_c_nested_R(expr_tree: ExprNode) -> str:
            if expr_tree.type in ("num_i", "num_f", "var"):
                return expr_tree.value
            else:
                f_name = ExprOpMap.get_hv_func(expr_tree.value)
                args = [_to_c_nested_R(p) for p in expr_tree.nodes]
                return f"{f_name}({', '.join(args)})"

        return f"{_to_c_nested_R(self.expr_tree)};"


class ExprOpMap:
    op_map = {
        "~":            "hv_bit_not_f",
        "!":            "hv_not_f",
        "*":            "hv_mul_f",
        "/":            "hv_div_f",
        "%":            "hv_modulo_f",
        "+":            "hv_add_f",
        "-":            "hv_sub_f",
        "<":            "hv_lt_f",
        "<=":           "hv_lte_f",
        ">":            "hv_gt_f",
        ">=":           "hv_gte_f",
        "<<":           "hv_shl_f",
        ">>":           "hv_shr_f",
        "==":           "hv_eq_f",
        "!=":           "hv_neq_f",
        "^":            "hv_exc_or_f",
        "&":            "hv_bit_and_f",
        "&&":           "hv_log_and_f",
        "|":            "hv_bit_or_f",
        "||":           "hv_log_or_f",
        "abs":          "hv_abs_f",
        "acos":         "hv_acos_f",
        "acosh":        "hv_acosh_f",
        "asin":         "hv_asin_f",
        "asinh":        "hv_asinh_f",
        "atan":         "hv_atan_f",
        "atan2":        "hv_atan2_f",
        "atanh":        "hv_atanh_f",
        "cbrt":         "hv_cbrt_f",
        "ceil":         "hv_ceil_f",
        "copysign":     "hv_copysign_f",
        "cos":          "hv_cos_f",
        "cosh":         "hv_cosh_f",
        "erf":          "hv_erf_f",
        "erfc":         "hv_erfc_f",
        "exp":          "hv_exp_f",
        "expm1":        "hv_expm1_f",
        # "fact":         "hv_?_f",
        "finite":       "hv_finite_f",
        "float":        "hv_cast_if_expr",
        "floor":        "hv_floor_f",
        "fmod":         "hv_fmod_f",
        "if":           "hv_if_f",
        # "imodf":        "hv_?_f",
        "int":          "hv_cast_fi_expr",
        "isinf":        "hv_isinf_f",
        "isnan":        "hv_isnan_f",
        "ldexp":        "hv_ldexp_f",
        "ln":           "hv_ln_f",
        "log":          "hv_log_f",
        "log10":        "hv_log10_f",
        "log1p":        "hv_log1p_f",
        "max":          "hv_max_f",
        "min":          "hv_min_f",
        "modf":         "hv_modf_f",
        "pow":          "hv_pow_f",
        "remainder":    "hv_remainder_f",
        "rint":         "hv_rint_f",        # round to nearest int
        "round":        "hv_round_f",       # round to nearest int
        "nearbyint":    "hv_rint_f",        # round to nearest int
        "sin":          "hv_sin_f",
        "sinh":         "hv_sinh_f",
        # "size":         "hv_?_f",           # size of a table
        "sqrt":         "hv_sqrt_f",
        # "sum":          "hv_?_f",            # sum of all elements of a table
        # "Sum":          "hv_?_f",            # sum of elemnets of a specified boundary of a table???
        "tan":          "hv_tan_f",
        "tanh":         "hv_tanh_f",
        "_load_f":      "hv_var_k_f",
        "_load_i":      "hv_var_k_i",
    }

    @classmethod
    def get_hv_func(cls, symbol: str) -> str:
        return cls.op_map[symbol]

    @classmethod
    def get_hv_func_simd(cls, symbol: str) -> str:
        return f"__{cls.op_map[symbol]}"
