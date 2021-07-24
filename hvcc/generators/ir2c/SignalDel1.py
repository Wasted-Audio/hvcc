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


class SignalDel1(HeavyObject):
    """Handles the __del1~f object.
    """

    c_struct = "SignalDel1"
    preamble = "sDel1"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvSignalDel1.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvSignalDel1.h", "HvSignalDel1.c"}

    @classmethod
    def get_C_def(clazz, obj_type, obj_id):
        return ["SignalDel1 sDel1_{0};".format(obj_id)]

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return ["sDel1_init(&sDel1_{0});".format(obj_id)]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_process(clazz, obj_type, process_dict, objects):
        return [
            "__hv_del1_f(&sDel1_{0}, VIf({1}), VOf({2}));".format(
                process_dict["id"],
                HeavyObject._c_buffer(process_dict["inputBuffers"][0]),
                HeavyObject._c_buffer(process_dict["outputBuffers"][0]))]
