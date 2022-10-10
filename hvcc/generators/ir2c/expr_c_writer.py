from .expr_arpeggio_parser import ExprArpeggioParser, ExprNode
import re


class ExprCWriter:
    def __init__(self, expression):
        self.expression = expression
        self.expr_tree = ExprArpeggioParser.parse_to_ast(expression)
        self.parse_tree = ExprArpeggioParser.parse(expression)
        self.num_buffers = None

    def to_ast(self):
        return self.expr_tree

    def to_parse_tree(self):
        return self.parse_tree

    def to_c_simd(self, vv_in, v_out):
        self._simd_bind_variables(vv_in)
        self._simd_replace_constants()
        return self._to_c_simd(v_out)

    def num_simd_buffers(self):
        if self.num_buffers is None:
            self.to_c_simd()
        return self.num_buffers

    def to_c_nested(self):
        return self._to_c_nested()

    def _simd_replace_constants(self):
        self._simd_replace_constants_R(self.expr_tree)

    def _simd_replace_constants_R(self, tree):
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

    def _simd_bind_variables(self, a_name="A"):
        self._bind_vars_R(self.expr_tree, a_name)

    def _bind_vars_R(self, tree, a_name):
        if tree.type == "var":
            self._bind_var_node(tree, a_name)
        else:
            for node in tree.nodes:
                self._bind_vars_R(node, a_name)

    def _bind_var_node(self, node, a_name):
        if node.type != "var":
            print("called on non-var node: ", node)
            return
        parts = re.match(r"\$(v|f)(\d+)", node.value)
        node.value = f"{a_name}[{int(parts[2])-1}]"
        node.type = "bound_var"

    class BufferAllocator:
        """Inner class for managing the swapping of buffers from
           output to input in successive calls.
        """
        def __init__(self):
            self._avail = set()
            self._next = 0

        def next(self):
            """If a buffer is available return it, otherwise
            allocate a new one and return it. """

            if len(self._avail) > 0:
                return self._avail.pop()
            nxt = self._next
            self._next += 1
            return nxt

        def free(self, n):
            """Return a buffer back to the pool to be reused"""
            self._avail.add(n)

        def num_allocated(self):
            """Return the buffers allocated in so far."""
            return self._next

    def _to_c_simd(self, v_out):
        ba = ExprCWriter.BufferAllocator()
        lines = []

        def _to_c_simd_R(expr_tree, r_vec=None):
            if expr_tree.type in ("num_i", "num_f", "var", "bound_var"):
                return expr_tree.value

            args = []
            buffers = []

            if (
                expr_tree.type == "func"
                and expr_tree.value.startswith("_load_")
            ):
                next_buf = f"Bf{ba.next()}"
                args.append("&" + next_buf)
                const_value = _to_c_simd_R(expr_tree.nodes[0])
                for i in range(8):
                    args.append(const_value)
            else:
                for node in expr_tree.nodes:
                    val = _to_c_simd_R(node)
                    args.append(val)
                    if type(val) == str and val.startswith("Bf"):
                        buffers.append(val)
                if r_vec:
                    next_buf = r_vec
                    args.append(next_buf)
                else:
                    next_buf = f"Bf{ba.next()}"
                    args.append("&" + next_buf)

            f_name = ExprOpMap.get_hv_func_simd(expr_tree.value)
            lines.append(f"{f_name}({', '.join(args)});")
            [ba.free(int(b[2])) for b in buffers]

            return next_buf

        lines.append(_to_c_simd_R(self.expr_tree, v_out))
        self.num_buffers = ba.num_allocated()
        return lines

    def _to_c_nested(self):
        """Output C-code as nested function calls"""

        def _to_c_nested_R(expr_tree):
            if expr_tree.type in ("num_i", "num_f", "var"):
                return expr_tree.value
            else:
                f_name = ExprOpMap.get_hv_func(expr_tree.value)
                args = [_to_c_nested_R(p) for p in expr_tree.nodes]
                return f"{f_name}({', '.join(args)})"

        return _to_c_nested_R(self.expr_tree) + ";"


class ExprOpMap:
    op_map = {
        "~": "hv_?_f",
        # "-": "hv_neg_f",
        "*": "hv_mul_f",
        "/": "hv_div_f",
        "%": "hv_?_f",
        "+": "hv_add_f",
        "-": "hv_sub_f",
        "<": "hv_lt_f",
        "<=": "hv_lte_f",
        ">": "hv_gt_f",
        ">=": "hv_gte_f",
        "!=": "hv_neq_f",
        "&&": "hv_and_f",
        "||": "hv_or_f",
        "abs": "hv_abs_f",
        "acos": "hv_acos_f",
        "acosh": "hv_acosh_f",
        "asin": "hv_asin_f",
        "asinh": "hv_asinh_f",
        "atan": "hv_atan_f",
        "atan2": "hv_atan2_f",
        "cbrt": "hv_?_f",
        "ceil": "hv_ceil_f",
        "copysign": "hv_?_f",  # does this just return +/- 1? It doesn't come up in pd...
        "cos": "hv_cos_f",
        "cosh": "hv_cosh_f",
        "drem": "hv_?_f",
        "erf": "hv_?_f",
        "erfc": "hv_?_f",
        "exp": "hv_exp_f",
        "expm1": "hv_?_f",
        "fact": "hv_?_f",
        "finite": "hv_?_f",
        "float": "hv_cast_if",
        "floor": "hv_floor_f",
        "fmod": "hv_?_f",
        "ldexp": "hv_?_f",
        "if": "hv_?_f",
        "imodf": "hv_?_f",
        "int": "hv_cast_fi",
        "isinf": "hv_?_f",
        "isnan": "hv_?_f",
        "ln": "hv_?_f",
        "log": "hv_?_f",
        "log10": "hv_?_f",
        "log1p": "hv_?_f",
        "max": "hv_max_f",
        "min": "hv_min_f",
        "modf": "hv_?_f",
        "pow": "hv_pow_f",
        "rint": "hv_?_f",  # round to nearest int
        "sin": "hv_sin_f",
        "sinh": "hv_sinh_f",
        "size": "hv_?_f",
        "sqrt": "hv_sqrt_f",
        "sum": "hv_?_f",  # sum of all elements of a table
        "Sum": "hv_?_f",  # sum of elemnets of a specified boundary of a table???
        "tan": "hv_tan_f",
        "tanh": "hv_tanh_f",
        "_load_f": "hv_var_k_f",
        "_load_i": "hv_var_k_i",
    }

    @classmethod
    def get_hv_func(cls, symbol):
        return cls.op_map[symbol]

    @classmethod
    def get_hv_func_simd(cls, symbol):
        return "__" + cls.op_map[symbol]
