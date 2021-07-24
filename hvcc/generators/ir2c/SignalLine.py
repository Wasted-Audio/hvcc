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


class SignalLine(HeavyObject):

    c_struct = "SignalLine"
    preamble = "sLine"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalLine.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalLine.h", "HvSignalLine.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            f"sLine_init(&sLine_{obj_id});"
        ]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []  # nothing to free

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            f"sLine_onMessage(_c, &Context(_c)->sLine_{obj_id}, {inlet_index}, m, NULL);"
        ]

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, args):
        return [
            "__hv_line_f(&sLine_{0}, VOf({1}));".format(
                process_dict["id"],
                HeavyObject._c_buffer(process_dict["outputBuffers"][0])
            )
        ]
