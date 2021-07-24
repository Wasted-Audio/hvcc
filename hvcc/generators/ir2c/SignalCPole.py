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


class SignalCPole(HeavyObject):
    """Handles the __cpole~f object.
    """

    c_struct = "SignalCPole"
    preamble = "sCPole"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalCPole.h", "HvSignalDel1.h", "HvMath.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {
            "HvSignalCPole.h", "HvSignalCPole.c",
            "HvSignalDel1.h", "HvSignalDel1.c",
            "HvMath.h"
        }

    @classmethod
    def get_C_def(clazz, obj_type, obj_id):
        return ["SignalCPole sCPole_{0};".format(obj_id)]

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return ["sCPole_init(&sCPole_{0});".format(obj_id)]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        return [
            "__hv_cpole_f(&sCPole_{0}, VIf({1}), VIf({2}), VIf({3}), VIf({4}), VOf({5}), VOf({6}));".format(
                process_dict["id"],
                HeavyObject._c_buffer(process_dict["inputBuffers"][0]),
                HeavyObject._c_buffer(process_dict["inputBuffers"][1]),
                HeavyObject._c_buffer(process_dict["inputBuffers"][2]),
                HeavyObject._c_buffer(process_dict["inputBuffers"][3]),
                HeavyObject._c_buffer(process_dict["outputBuffers"][0]),
                HeavyObject._c_buffer(process_dict["outputBuffers"][1]))]
