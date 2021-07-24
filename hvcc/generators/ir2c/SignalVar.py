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


class SignalVar(HeavyObject):

    __OPERATION_DICT = {
        "__var~f": "sVarf",
        "__var~i": "sVari",
        "__var_k~f": "__hv_var_k_f",
        "__var_k~i": "__hv_var_k_i",
        "__varwrite~f": "__hv_varwrite_f",
        "__varwrite~i": "__hv_varwrite_i",
        "__varread~f": "__hv_varread_f",
        "__varread~i": "__hv_varread_i"
    }

    @classmethod
    def get_c_struct(clazz, obj_type):
        if obj_type == "__var~f":
            return "SignalVarf"
        elif obj_type == "__var~i":
            return "SignalVari"
        else:
            raise Exception()

    @classmethod
    def get_preamble(clazz, obj_type):
        return SignalVar.__OPERATION_DICT[obj_type]

    @classmethod
    def handles_type(clazz, obj_type):
        """Returns true if the object type can be handled by this class
        """
        return obj_type in SignalVar.__OPERATION_DICT

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalVar.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalVar.h", "HvSignalVar.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        assert obj_type in ["__var~f", "__var~i"], obj_type
        return [
            "{0}_init(&{0}_{1}, {2}, {3}, {4});".format(
                SignalVar.__OPERATION_DICT[obj_type],
                obj_id,
                "{0}f".format(float(args["k"])) if obj_type.endswith("f") else int(args["k"]),
                "{0}f".format(float(args["step"])) if obj_type.endswith("f") else int(args["step"]),
                "true" if args["reverse"] else "false")]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        assert obj_type in ["__var~f", "__var~i"]
        return [
            "{0}_onMessage(_c, &Context(_c)->{0}_{1}, m);".format(
                SignalVar.__OPERATION_DICT[obj_type],
                obj_id)]

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, args):
        fmt = obj_type[-1]
        if obj_type in ["__var~f", "__var~i"]:
            # NOTE(mhroth): signal rate variables do not process anything
            return []
        elif obj_type in ["__varwrite~f", "__varwrite~i"]:
            return [
                "__hv_varwrite_{1}(&sVar{1}_{0}, VI{1}({2}));".format(
                    args["var_id"],
                    fmt,
                    HeavyObject._c_buffer(process_dict["inputBuffers"][0])
                )]
        elif obj_type in ["__var_k~f", "__var_k~i"]:
            if args["k"] == 0.0 and args.get("step", 0.0) == 0.0:
                return ["__hv_zero_{0}(VO{0}({1}));".format(
                    fmt,
                    HeavyObject._c_buffer(process_dict["outputBuffers"][0]))]
            else:
                c = [float(args["k"] + i * args.get("step", 0.0)) for i in range(8)]
                cx = ", ".join(["{0}f".format(f) for f in c]) if fmt == "f" else ", ".join([str(int(i)) for i in c])
                return ["__hv_var_k_{0}{3}(VO{0}({1}), {2});".format(
                    fmt,
                    HeavyObject._c_buffer(process_dict["outputBuffers"][0]),
                    cx,
                    "_r" if args.get("reverse", False) else "")]
        elif obj_type in ["__varread~f", "__varread~i"]:
            return [
                "__hv_varread_{1}(&sVar{1}_{0}, VO{1}({2}));".format(
                    args["var_id"],
                    fmt,
                    HeavyObject._c_buffer(process_dict["outputBuffers"][0])
                )]
