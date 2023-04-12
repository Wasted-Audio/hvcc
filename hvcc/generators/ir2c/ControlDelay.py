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


class ControlDelay(HeavyObject):

    c_struct = "ControlDelay"
    preamble = "cDelay"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvControlDelay.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvControlDelay.h", "HvControlDelay.c"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            "{0}_init(this, &{0}_{1}, {2}f);".format(
                cls.preamble,
                obj_id,
                float(args["delay"]))
        ]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []  # no need to free any control binop objects

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [
            "{0}_onMessage(_c, &Context(_c)->{0}_{1}, {2}, m, "
            "&{0}_{1}_sendMessage);".format(
                cls.preamble,
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_impl(
        cls,
        obj_type: str,
        obj_id: int,
        on_message_list: List,
        get_obj_class: Callable,
        objects: Dict
    ) -> List[str]:
        send_message_list = [
            f"cDelay_{obj_id}_sendMessage(HeavyContextInterface *_c, int letIn, const HvMessage *const m) {{"
        ]
        send_message_list.append(f"cDelay_clearExecutingMessage(&Context(_c)->cDelay_{obj_id}, m);")
        send_message_list.extend(
            cls._get_on_message_list(on_message_list[0], get_obj_class, objects))
        send_message_list.append("}")  # end function
        return send_message_list
