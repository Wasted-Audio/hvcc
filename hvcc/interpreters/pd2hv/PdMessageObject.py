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

import re
from typing import Optional, List, Dict

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class PdMessageObject(PdObject):

    # only allow dollar argumnets if they are alone
    __RE_DOLLAR = re.compile(r"\$(\d+)")

    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type == "msg"
        super().__init__("msg", obj_args, pos_x, pos_y)

        self.obj_dict: Dict = {}

        # parse messages
        # remove prepended slash from $. Heavy does not use that.
        if obj_args is not None:
            semi_split = obj_args[0].replace(r"\$", "$").split(r"\;")
            semi_split = [x for x in semi_split if x]  # remove empty strings

        # parse local messages
        # ensure that empty message are not passed on
        if len(semi_split) > 0:
            self.obj_dict["local"] = [li.strip().split() for li in semi_split[0].split(r"\,") if len(li.strip()) > 0]
        else:
            self.obj_dict["local"] = []
            self.add_warning(
                "Message object is empty. Can it be removed?",
                NotificationEnum.WARNING_EMPTY_MESSAGE)

        # heavy does not support messages such as "$1-$2"
        for li in self.obj_dict["local"]:
            for m in li:
                x = self.__RE_DOLLAR.search(m)
                if x and len(x.group(0)) < len(m):
                    self.add_error(
                        "Heavy does not yet support message concatenation. "
                        "Dollar arguments must be alone: " + m)

        # parse remote messages
        self.obj_dict["remote"] = []
        for li in semi_split[1:]:
            l_split = li.strip().split()
            self.obj_dict["remote"].append({
                "receiver": l_split[0],
                "message": l_split[1:]
            })

        if len(self.obj_dict["remote"]) > 0:
            self.add_warning(
                "Message boxes don't yet support remote messages. "
                "These messages will be ignored.")

    def to_hv(self) -> Dict:
        return {
            "type": "message",
            "args": self.obj_dict,
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
