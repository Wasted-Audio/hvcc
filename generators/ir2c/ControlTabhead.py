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

class ControlTabhead(HeavyObject):
    """Handles __tabhead
    """

    c_struct = "ControlTabhead"
    preamble = "cTabhead"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvControlTabhead.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvControlTabhead.h", "HvControlTabhead.c"}

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            "cTabhead_init(&cTabhead_{0}, &hTable_{1});".format(
                obj_id,
                args["table_id"])]

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "cTabhead_onMessage(_c, &Context(_c)->cTabhead_{0}, 0, m, &cTabhead_{0}_sendMessage);".format(
                obj_id)]
