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

from typing import Dict, List

from hvcc.types.IR import IRSignalList

from .expr.expr_c_writer import ExprCWriter
from .HeavyObject import HeavyObject


class SignalExpr(HeavyObject):
    """ Handles the math objects.
        Note: obj_eval_functions dict accumulates until reset!
    """

    preamble = "cExprSig"
    obj_eval_functions: Dict = {}

    @classmethod
    def handles_type(cls, obj_type: str) -> bool:
        """ Returns true if the object type can be handled by this class
        """
        return obj_type == "_expr~"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvMath.h"}

    @classmethod
    def get_C_class_header_code(cls, obj_type: str, args: Dict) -> List[str]:
        eval_funcs = ",\n\t\t".join(cls.obj_eval_functions.values())
        fptr_type = f"{cls.preamble}_evaluator"
        lines = [
            f"typedef void(*{fptr_type})(hv_bInf_t*, hv_bOutf_t);",
            f"{fptr_type} {cls.preamble}_evaluators[{len(cls.obj_eval_functions)}] = {{\n\t\t{eval_funcs}\n\t}};",
        ]
        return lines

    @classmethod
    def get_C_obj_header_code(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        lines = []
        func_name = f"{cls.preamble}_{obj_id}_evaluate"
        cls.obj_eval_functions[obj_id] = func_name
        lines.extend([
            f"static inline void {func_name}(hv_bInf_t* bIns, hv_bOutf_t bOut);",
        ])
        return lines

    @classmethod
    def get_C_obj_impl_code(cls, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        """ (Per object) this creates the _sendMessage function that other objects use to
            send messages to this object.
        """

        lines = []
        expr = args["expressions"][0]
        expr_parser = ExprCWriter(expr)
        expr_lines = expr_parser.to_c_simd("bIns", "bOut")[:-1]
        expr_line = "\n".join(
            [f"\t{line}" for line in expr_lines]
        )
        num_buffers = expr_parser.num_simd_buffers()
        buffer_declaration = "\t// no extra buffers needed"
        if num_buffers > 0:
            buffers = ", ".join([f"Bf{i}" for i in range(0, num_buffers)])
            buffer_declaration = f"\thv_bufferf_t {buffers};"

        func_name = f"Heavy_{{{{name}}}}::{cls.preamble}_{obj_id}_evaluate"
        lines.extend([
            "",
            f"void {func_name}(hv_bInf_t* bIns, hv_bOutf_t bOut) {{",

            buffer_declaration,
            expr_line,
            "}",

        ])
        return lines

    @classmethod
    def get_C_process(cls, process_dict: IRSignalList, obj_type: str, obj_id: str, args: Dict) -> List[str]:
        input_args = []
        for b in process_dict.inputBuffers:
            buf = HeavyObject._c_buffer(b)
            input_args.append(f"VIf({buf})")
        out_buf = HeavyObject._c_buffer(process_dict.outputBuffers[0])
        out_buf = f"VOf({out_buf})"

        call = [
            "",
            "\t// !!! declare this buffer once outside the loop",
            f"\thv_bInf_t input_args_{obj_id}[{args['num_inlets']}] = {{{', '.join(input_args)}}};",
            f"\t{cls.preamble}_evaluators[{len(cls.obj_eval_functions)}](input_args_{obj_id}, {out_buf});"
            "",
        ]

        return call
