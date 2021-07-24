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


class SignalTabwrite(HeavyObject):
    """Handles __tabwrite~f
    """

    c_struct = "SignalTabwrite"
    preamble = "sTabwrite"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalTabwrite.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalTabwrite.h", "HvSignalTabwrite.c"}

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            "sTabwrite_init(&sTabwrite_{0}, &hTable_{1});".format(
                obj_id,
                args["table_id"])]

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "sTabwrite_onMessage(_c, &Context(_c)->sTabwrite_{0}, {1}, m, NULL);".format(
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        if obj_type == "__tabwrite~f":
            return [
                "__hv_tabwrite_f(&sTabwrite_{0}, {1});".format(
                    process_dict["id"],
                    ", ".join(["VIf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["inputBuffers"]])
                )]
        elif obj_type == "__tabwrite_stoppable~f":
            return [
                "__hv_tabwrite_stoppable_f(&sTabwrite_{0}, {1});".format(
                    process_dict["id"],
                    ", ".join(["VIf({0})".format(HeavyObject._c_buffer(b)) for b in process_dict["inputBuffers"]])
                )]
        else:
            raise Exception()
