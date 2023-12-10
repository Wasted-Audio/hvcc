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


class ControlSend(HeavyObject):

    c_struct = "ControlSend"
    preamble = "cSend"

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [f"cSend_{obj_id}_sendMessage(_c, 0, m);"]

    @classmethod
    def get_C_impl(
        cls,
        obj_type: str,
        obj_id: int,
        on_message_list: List,
        get_obj_class: Callable,
        objects: Dict
    ) -> List[str]:
        # Note(joe): if no corresponding receivers exist and there's no extern indicator
        # then there is not much need to generate code stub
        send_message_list = [
            "{0}_{1}_sendMessage(HeavyContextInterface *_c, int letIn, const HvMessage *m) {{".format(
                cls.get_preamble(obj_type),
                obj_id)]

        if objects[obj_id]["args"].get("extern", False):
            # call the send hook
            send_name = objects[obj_id]["args"]["name"]
            send_message_list.append("if (_c->getSendHook() != nullptr) _c->getSendHook()(_c, \"{0}\", {1}, m);".format(
                send_name,
                cls.get_hash_string(send_name)))

        # a send has only one (implicit!) outlet
        send_message_list.extend(
            cls._get_on_message_list(on_message_list[0], get_obj_class, objects))

        send_message_list.append("}")  # end function

        return send_message_list
