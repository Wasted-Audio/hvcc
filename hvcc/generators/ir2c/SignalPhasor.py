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


class SignalPhasor(HeavyObject):

    c_struct = "SignalPhasor"
    preamble = "sPhasor"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalPhasor.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalPhasor.h", "HvSignalPhasor.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        if obj_type == "__phasor~f":
            return [
                "sPhasor_init(&sPhasor_{0}, sampleRate);".format(obj_id)
            ]
        elif obj_type == "__phasor_k~f":
            return [
                "sPhasor_k_init(&sPhasor_{0}, {1}f, sampleRate);".format(
                    obj_id,
                    args["frequency"])
            ]
        else:
            raise Exception()

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        if obj_type == "__phasor~f":
            return [
                "sPhasor_onMessage(_c, &Context(_c)->sPhasor_{0}, {1}, m);".format(
                    obj_id,
                    inlet_index)]
        elif obj_type == "__phasor_k~f":
            return [
                "sPhasor_k_onMessage(_c, &Context(_c)->sPhasor_{0}, {1}, m);".format(
                    obj_id,
                    inlet_index)]
        else:
            raise Exception()

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, args):
        if obj_type == "__phasor~f":
            return [
                "__hv_phasor_f(&sPhasor_{0}, VIf({1}), VOf({2}));".format(
                    process_dict["id"],
                    HeavyObject._c_buffer(process_dict["inputBuffers"][0]),
                    HeavyObject._c_buffer(process_dict["outputBuffers"][0])
                )
            ]
        elif obj_type == "__phasor_k~f":
            return [
                "__hv_phasor_k_f(&sPhasor_{0}, VOf({1}));".format(
                    process_dict["id"],
                    HeavyObject._c_buffer(process_dict["outputBuffers"][0])
                )
            ]
        else:
            raise Exception("Unknown object type \"{0}\".".format(obj_type))
