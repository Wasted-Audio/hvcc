# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject

import re


class PdMessageObject(PdObject):

    # only allow dollar argumnets if they are alone
    __RE_DOLLAR = re.compile("\$(\d+)")

    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type == "msg"
        PdObject.__init__(self, "msg", obj_args, pos_x, pos_y)

        self.obj_args = {}

        # parse messages
        # remove prepended slash from $. Heavy does not use that.
        semi_split = obj_args[0].replace("\$", "$").split("\;")
        semi_split = [x for x in semi_split if x]  # remove empty strings

        # parse local messages
        # ensure that empty message are not passed on
        if len(semi_split) > 0:
            self.obj_args["local"] = [li.strip().split() for li in semi_split[0].split("\,") if len(li.strip()) > 0]
        else:
            self.obj_args["local"] = []
            self.add_warning(
                "Message object is empty. Can it be removed?",
                NotificationEnum.WARNING_EMPTY_MESSAGE)

        # heavy does not support messages such as "$1-$2"
        for li in self.obj_args["local"]:
            for m in li:
                x = PdMessageObject.__RE_DOLLAR.search(m)
                if x and len(x.group(0)) < len(m):
                    self.add_error(
                        "Heavy does not yet support message concatenation. "
                        "Dollar arguments must be alone: " + m)

        # parse remote messages
        self.obj_args["remote"] = []
        for li in semi_split[1:]:
            l_split = li.strip().split()
            self.obj_args["remote"].append({
                "receiver": l_split[0],
                "message": l_split[1:]
            })

        if len(self.obj_args["remote"]) > 0:
            self.add_warning(
                "Message boxes don't yet support remote messages. "
                "These messages will be ignored.")

    def to_hv(self):
        return {
            "type": "message",
            "args": self.obj_args,
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
