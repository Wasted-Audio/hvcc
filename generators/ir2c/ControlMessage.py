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

import re

from .HeavyObject import HeavyObject

class ControlMessage(HeavyObject):

    preamble = "cMsg"

    @classmethod
    def get_C_onMessage(clazz, obj_type, obj_id, inlet_index, args):
        return ["cMsg_{0}_sendMessage(_c, 0, m);".format(obj_id)]

    @classmethod
    def get_C_impl(clazz, obj_type, obj_id, on_message_list, get_obj_class, objects):
        send_message_list = [
            "cMsg_{0}_sendMessage(HeavyContextInterface *_c, int letIn, const HvMessage *const n) {{".format(obj_id)
        ]

        if len(objects[obj_id]["args"]["local"]) > 0:
            # declare the outgoing messages (if there are any)
            send_message_list.append("HvMessage *m = nullptr;")

        # for each message
        for m in objects[obj_id]["args"]["local"]:
            # construct the message
            send_message_list.append("m = HV_MESSAGE_ON_STACK({0});".format(len(m)))
            send_message_list.append("msg_init(m, {0}, msg_getTimestamp(n));".format(len(m)))
            for i in range(len(m)):
                e = m[i] # get the message element
                try:
                    # is the message a float?
                    send_message_list.append("msg_setFloat(m, {0}, {1}f);".format(i, float(e)))
                except:
                    if e in ["bang"]:
                        # is the message a bang?
                        send_message_list.append("msg_setBang(m, {0});".format(i))
                    elif re.match("\$[\d]+", e):
                        send_message_list.append("msg_setElementToFrom(m, {0}, n, {1});".format(i, int(e[1:])-1))
                    elif e == "@HV_N_SIMD":
                        # NOTE(mhroth): messages can contain special arguments
                        # which are interpreted differently than other strings
                        send_message_list.append("msg_setFloat(m, {0},  static_cast<float>(HV_N_SIMD));".format(i))
                    else:
                        send_message_list.append("msg_setSymbol(m, {0}, \"{1}\");".format(i, e))

            # send the message to all receiving objects
            for om in on_message_list[0]:
                send_message_list.extend(
                    get_obj_class(objects[om["id"]]["type"]).get_C_onMessage(
                        objects[om["id"]]["type"],
                        om["id"],
                        om["inletIndex"],
                        objects[om["id"]]["args"]))

        send_message_list.append("}") # end function
        return send_message_list
