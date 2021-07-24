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


class SignalTabread(HeavyObject):
    """Handles __tabread~if, __tabread~f, __tabreadu~f
    """

    c_struct = "SignalTabread"
    preamble = "sTabread"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalTabread.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalTabread.h", "HvSignalTabread.c"}

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            "sTabread_init(&sTabread_{0}, &hTable_{1}, {2});".format(
                obj_id,
                args["table_id"],
                "true" if obj_type == "__tabread~f" else "false")]

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        if obj_type in ["__tabread~f", "__tabreadu~f"]:
            return [
                "sTabread_onMessage(_c, &Context(_c)->sTabread_{0}, {1}, m, &sTabread_{0}_sendMessage);".format(
                    obj_id,
                    inlet_index)]
        else:  # "__tabread~if"
            return [
                "sTabread_onMessage(_c, &Context(_c)->sTabread_{0}, {1}, m, NULL);".format(
                    obj_id,
                    inlet_index)]

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        if obj_type == "__tabread~if":
            return [
                "__hv_tabread_if(&sTabread_{0}, {1}, {2});".format(
                    process_dict["id"],
                    ", ".join(["VIi({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["inputBuffers"]]),
                    ", ".join(["VOf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["outputBuffers"]])
                )]
        elif obj_type == "__tabread~f":
            return [
                "__hv_tabread_f(&sTabread_{0}, {1});".format(
                    process_dict["id"],
                    ", ".join(["VOf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["outputBuffers"]])
                )]
        elif obj_type == "__tabreadu~f":
            return [
                "__hv_tabreadu_f(&sTabread_{0}, {1});".format(
                    process_dict["id"],
                    ", ".join(["VOf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["outputBuffers"]])
                )]
        else:
            raise Exception()
