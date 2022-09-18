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

    @classmethod
    def handles_type(clazz, obj_type):
        """Returns true if the object type can be handled by this class
        """
        return obj_type in SignalMath.__OPERATION_DICT

    # @classmethod
    # def get_C_header_set(clazz):
    #     return {"HvMath.h"}

    @classmethod
    def get_C_class_header_code(clazz, obj_type, obj_id, args):
        lines = super().get_C_class_header_code(obj_type, obj_id, args)
        print("args", args)
        lines.append(f"hv_bInf_t {clazz.preamble}_evaluators[{args['num_inlets']}] = {{}};")
        return lines

    @classmethod
    def get_C_obj_header_code(clazz, obj_type, obj_id, args):
        lines = super().get_C_obj_header_code(obj_type, obj_id, args)
        lines.append(f"static inline void {clazz.preamble}_{obj_id}_evaluate(hv_bInf_t* bIns, hv_bInf_t bOut);")
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
        
        lines.extend([
            "",
            f"void Heavy_heavy::{clazz.preamble}_{obj_id}_evaluate(hv_bInf_t* bIns, hv_bInf_t bOut) {{",
            f"\t// per-obj expression evaluation code here;",
            "}",
        ])
        return lines

    @classmethod
    def get_C_def(clazz, obj_type, obj_id):
        """(Per object) code that gets inserted into the header file"""

        lines = super().get_C_def(obj_type, obj_id)
        # ["{0} {1}_{2};".format(
        #     clazz.get_c_struct(obj_type),
        #     clazz.get_preamble(obj_type),
        #     obj_id)]
        lines.append("// --------------- big ol' comment ------------")
        lines.append(f"static float {clazz.preamble}_{obj_id}_evaluate(float* args);")
        return lines

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        print("------------- calling get_C_process() ------------------")
        print(objects)

        #  example: __hv_mul_f(VIf(Bf0), VIf(Bf1), VOf(Bf1));
        args = []
        for b in process_dict["inputBuffers"]:
            buf = HeavyObject._c_buffer(b)
            args.append(f"VIf({buf})")
        args.append("VOf(Bf0)")
        
        call = f";//__hv_expr_f(" + ", ".join(args) + ");"
        return [call]


