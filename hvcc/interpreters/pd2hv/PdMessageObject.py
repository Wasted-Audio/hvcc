# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

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
    ):
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
                x = PdMessageObject.__RE_DOLLAR.search(m)
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
