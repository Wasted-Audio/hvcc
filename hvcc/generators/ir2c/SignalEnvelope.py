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


class SignalEnvelope(HeavyObject):

    c_struct = "SignalEnvelope"
    preamble = "sEnv"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalEnvelope.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalEnvelope.h", "HvSignalEnvelope.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            "sEnv_init(&sEnv_{0}, {1}, {2});".format(
                obj_id,
                int(args["windowSize"]),
                int(args["period"]))
        ]

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, args):
        return [
            "sEnv_process(this, &sEnv_{0}, VIf({1}), &sEnv_{0}_sendMessage);".format(
                process_dict["id"],
                HeavyObject._c_buffer(process_dict["inputBuffers"][0])
            )
        ]
