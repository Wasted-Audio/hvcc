# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023 Wasted Audio
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

from typing import Callable, Dict, List
from .HeavyObject import HeavyObject


class ControlSwitchcase(HeavyObject):

    c_struct = "ControlSwitchase"
    preamble = "cSwichcase"

    @classmethod
    def get_C_def(cls, obj_type: str, obj_id: int) -> List[str]:
        return []

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []

    @classmethod
    def get_C_decl(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            f"cSwitchcase_{obj_id}_onMessage(HeavyContextInterface *, void *, int letIn, "
            "const HvMessage *const, void *);"
        ]

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [f"cSwitchcase_{obj_id}_onMessage(_c, NULL, {inlet_index}, m, NULL);"]

    @classmethod
    def get_C_impl(
        cls,
        obj_type: str,
        obj_id: int,
        on_message_list: List,
        get_obj_class: Callable,
        objects: Dict
    ) -> List[str]:
        # generate the onMessage implementation
        out_list = [
            f"cSwitchcase_{obj_id}_onMessage(HeavyContextInterface *_c, void *o, int letIn, "
            f"const HvMessage *const m, void *sendMessage) {{"
        ]
        out_list.append("int msgIndex = 0;")
        out_list.append("switch (msg_getHash(m, msgIndex)) {")
        out_list.append(f"case {cls.get_hash_string('symbol')}: {{ // \"symbol\"")
        out_list.append("msgIndex = 1;")
        out_list.append("break;")
        out_list.append("}")  # end symbol case
        out_list.append("}")  # end type switch

        out_list.append("switch (msg_getHash(m, msgIndex)) {")
        cases = objects[obj_id]["args"]["cases"]
        for i, c in enumerate(cases):
            hv_hash = cls.get_hash_string(c)
            out_list.append(f"case {hv_hash}: {{ // \"{c}\"")
            out_list.extend(
                cls._get_on_message_list(on_message_list[i], get_obj_class, objects))
            out_list.append("break;")
            out_list.append("}")
        out_list.append("default: {")
        out_list.extend(
            cls._get_on_message_list(on_message_list[-1], get_obj_class, objects))
        out_list.append("break;")
        out_list.append("}")  # end default
        out_list.append("}")  # end switch
        out_list.append("}")  # end function

        return out_list
