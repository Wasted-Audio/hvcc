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


class SignalExpr(HeavyObject):
    """Handles the math objects.
    """

    preamble = "cExprSig"

    obj_eval_functions = {}

    @classmethod
    def handles_type(clazz, obj_type):
        """Returns true if the object type can be handled by this class
        """
        return obj_type == "_expr~"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvMath.h"}

    @classmethod
    def get_C_class_header_code(clazz, obj_type, obj_id, args):
        """
            typedef int(*fptr)(int, int);
            fptr test = &Foo::evaluate;
        """
        print("args", args)
        eval_funcs = ", ".join(clazz.obj_eval_functions.values())
        fptr_type = f"{clazz.preamble}_evaluator"
        lines = [
            f"typedef void(*{fptr_type})(hv_bInf_t*, hv_bOutf_t);",
            f"{fptr_type} {clazz.preamble}_evaluators[{args['num_inlets']}] = {{{eval_funcs}}};",
        ]
        
        return lines

    @classmethod
    def get_C_obj_header_code(clazz, obj_type, obj_id, args):
        lines = super().get_C_obj_header_code(obj_type, obj_id, args)
        func_name = f"{clazz.preamble}_{obj_id}_evaluate"
        clazz.obj_eval_functions[obj_id] = func_name
        # idx = 0
        lines.extend([
            f"static inline void {func_name}(hv_bInf_t* bIns, hv_bOutf_t bOut);",
        ])
        return lines

    @classmethod
    def get_C_obj_impl_code(clazz, obj_type, obj_id, args):
        """
        (Per object) this creates the _sendMessage function that other objects use to
        send messages to this object.
        """
        
        lines = super().get_C_obj_impl_code(obj_type, obj_id, args)
        
        # expr = args["expressions"][0]
        bound_expr = ""  # bind_expr(expr, "args")
        func_name = f"Heavy_heavy::{clazz.preamble}_{obj_id}_evaluate"
        lines.extend([
            "",
            f"void {func_name}(hv_bInf_t* bIns, hv_bOutf_t bOut) {{",
            f"\t// per-obj expression evaluation code here;",
            "}",
            
        ])
        return lines

    # @classmethod
    # def get_C_def(clazz, obj_type, obj_id):
    #     """(Per object) code that gets inserted into the header file"""

    #     lines = super().get_C_def(obj_type, obj_id)
    #     # ["{0} {1}_{2};".format(
    #     #     clazz.get_c_struct(obj_type),
    #     #     clazz.get_preamble(obj_type),
    #     #     obj_id)]
    #     lines.append("// --------------- big ol' comment ------------")
    #     lines.append(f"static float {clazz.preamble}_{obj_id}_evaluate(float* args);")
    #     return lines

    @classmethod
    def get_C_process(clazz, process_dict, obj_type, obj_id, args):
        print("------------- calling get_C_process() ------------------")
        print(args)

        #  example: __hv_mul_f(VIf(Bf0), VIf(Bf1), VOf(Bf1));
        input_args = []
        for b in process_dict["inputBuffers"]:
            buf = HeavyObject._c_buffer(b)
            input_args.append(f"VIf({buf})")
        out_buf = HeavyObject._c_buffer(process_dict["outputBuffers"][0])
        out_buf = f"VOf({out_buf})"
        
        call = f"""
        cExprSig_evaluator eval = {clazz.preamble}_evaluators[0];
        /* instead of having one of these for each step, create one (outside of the loop)
         * that is big enough for all of the steps and then use it for every step */
        hv_bInf_t input_args[{args["num_inlets"]}] = {{{", ".join(input_args)}}}; // jam the b's in here
        eval(input_args, {out_buf});
        //{clazz.preamble}_evaluators[0](input_args, {out_buf});
        """

        # f"{clazz.preamble}_evaluators[0]"
        # call = f";//__hv_expr_f(" + ", ".join(args) + ");"
        return [call]


"""
Sample code and stuff

// C code impl for abs from HvMath.h
static inline void __hv_abs_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  *bOut = _mm256_andnot_ps(_mm256_set1_ps(-0.0f), bIn);
#elif HV_SIMD_SSE
  *bOut = _mm_andnot_ps(_mm_set1_ps(-0.0f), bIn); // == 1 << 31
#elif HV_SIMD_NEON
  *bOut = vabsq_f32(bIn);
#else // HV_SIMD_NONE
  *bOut = hv_abs_f(bIn);
#endif
}

// Heavy_heavy.cpp calling above function
__hv_abs_f(VIf(Bf1), VOf(Bf1));

"""