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


class SignalBiquad(HeavyObject):
    """Handles the biquad~ object.
    """

    c_struct = "SignalBiquad"
    preamble = "sBiquad"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalBiquad.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalBiquad.h", "HvSignalBiquad.c"}

    @classmethod
    def get_C_def(clazz, obj_type, obj_id):
        if obj_type == "__biquad_k~f":
            return ["SignalBiquad_k sBiquad_k_{0};".format(obj_id)]
        elif obj_type == "__biquad~f":
            return ["SignalBiquad sBiquad_s_{0};".format(obj_id)]
        else:
            raise Exception()

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        if obj_type == "__biquad_k~f":
            return ["sBiquad_k_init(&sBiquad_k_{0}, {1}f, {2}f, {3}f, {4}f, {5}f);".format(
                obj_id,
                float(args["ff0"]),
                float(args["ff1"]),
                float(args["ff2"]),
                float(args["fb1"]),
                float(args["fb2"]))]
        elif obj_type == "__biquad~f":
            return ["sBiquad_init(&sBiquad_s_{0});".format(obj_id)]
        else:
            raise Exception()

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return ["sBiquad_k_onMessage(&Context(_c)->sBiquad_k_{0}, {1}, m);".format(
            obj_id,
            inlet_index)]

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        if obj_type == "__biquad_k~f":
            return [
                "__hv_biquad_k_f(&sBiquad_k_{0}, VIf({1}), VOf({2}));".format(
                    process_dict["id"],
                    HeavyObject._c_buffer(process_dict["inputBuffers"][0]),
                    HeavyObject._c_buffer(process_dict["outputBuffers"][0])
                )]
        elif obj_type == "__biquad~f":
            return [
                "__hv_biquad_f(&sBiquad_s_{0}, {1}, {2});".format(
                    process_dict["id"],
                    ", ".join(["VIf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["inputBuffers"]]),
                    ", ".join(["VOf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["outputBuffers"]])
                )]
