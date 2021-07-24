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


class ControlSwitchcase(HeavyObject):

    c_struct = "ControlSwitchase"
    preamble = "cSwichcase"

    @classmethod
    def get_C_def(clazz, obj_type, obj_id):
        return []

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return []

    @classmethod
    def get_C_decl(clazz, obj_type, obj_id, args):
        return [
            f"cSwitchcase_{obj_id}_onMessage(HeavyContextInterface *, void *, int letIn, "
            "const HvMessage *const, void *);"
        ]

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return [f"cSwitchcase_{obj_id}_onMessage(_c, NULL, {inlet_index}, m, NULL);"]

    @classmethod
    def get_C_impl(clazz, obj_type, obj_id, on_message_list, obj_class_dict, objects):
        # generate the onMessage implementation
        out_list = [
            f"cSwitchcase_{obj_id}_onMessage(HeavyContextInterface *_c, void *o, int letIn, "
            f"const HvMessage *const m, void *sendMessage) {{"
        ]
        out_list.append("switch (msg_getHash(m, 0)) {")
        cases = objects[obj_id]["args"]["cases"]
        for i, c in enumerate(cases):
            out_list.append("case {0}: {{ // \"{1}\"".format(
                HeavyObject.get_hash_string(c),
                c))
            out_list.extend(
                HeavyObject._get_on_message_list(on_message_list[i], obj_class_dict, objects))
            out_list.append("break;")
            out_list.append("}")
        out_list.append("default: {")
        out_list.extend(
            HeavyObject._get_on_message_list(on_message_list[-1], obj_class_dict, objects))
        out_list.append("break;")
        out_list.append("}")  # end default
        out_list.append("}")  # end switch
        out_list.append("}")  # end function

        return out_list
