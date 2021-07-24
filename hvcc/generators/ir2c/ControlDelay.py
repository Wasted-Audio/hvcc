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


class ControlDelay(HeavyObject):

    c_struct = "ControlDelay"
    preamble = "cDelay"

    @classmethod
    def get_C_header_set(clazz):
        return {"HvControlDelay.h"}

    @classmethod
    def get_C_file_set(clazz):
        return {"HvControlDelay.h", "HvControlDelay.c"}

    @classmethod
    def get_C_init(clazz, obj_type, obj_id, args):
        return [
            "{0}_init(this, &{0}_{1}, {2}f);".format(
                clazz.preamble,
                obj_id,
                float(args["delay"]))
        ]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []  # no need to free any control binop objects

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [
            "{0}_onMessage(_c, &Context(_c)->{0}_{1}, {2}, m, "
            "&{0}_{1}_sendMessage);".format(
                clazz.preamble,
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_impl(clazz, obj_type, obj_id, on_message_list, get_obj_class, objects):
        send_message_list = [
            f"cDelay_{obj_id}_sendMessage(HeavyContextInterface *_c, int letIn, const HvMessage *const m) {{"
        ]
        send_message_list.append("cDelay_clearExecutingMessage(&Context(_c)->cDelay_{0}, m);".format(
            obj_id
        ))
        send_message_list.extend(
            HeavyObject._get_on_message_list(on_message_list[0], get_obj_class, objects))
        send_message_list.append("}")  # end function
        return send_message_list
