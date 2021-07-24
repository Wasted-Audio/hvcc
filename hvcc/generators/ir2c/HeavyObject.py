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

from struct import unpack, pack


class HeavyObject:

    c_struct = ""
    preamble = ""

    __C_BUFFER_DICT = {
        "~f>": "Bf",
        "~i>": "Bi",
        "input": "I",
        "output": "O",
        "zero": "ZERO"
    }

    @classmethod
    def get_c_struct(clazz, obj_type=""):
        return clazz.c_struct

    @classmethod
    def get_preamble(clazz, obj_type):
        return clazz.preamble

    @classmethod
    def get_C_header_set(self):
        return set()

    @classmethod
    def get_C_file_set(self):
        return set()

    @classmethod
    def get_C_def(clazz, obj_type, obj_id):
        return ["{0} {1}_{2};".format(clazz.get_c_struct(obj_type), clazz.get_preamble(obj_type), obj_id)]

    @classmethod
    def get_C_free(clazz, obj_type, obj_id, args):
        return ["{0}_free(&{0}_{1});".format(clazz.get_preamble(obj_type), obj_id)]

    @classmethod
    def get_C_decl(clazz, obj_type, obj_id, args):
        return ["{0}_{1}_sendMessage(HeavyContextInterface *, int, const HvMessage *);".format(
                clazz.get_preamble(obj_type),
                obj_id)]

    @classmethod
    def get_C_impl(clazz, obj_type, obj_id, on_message_list, get_obj_class, objects):
        send_message_list = [
            "{0}_{1}_sendMessage(HeavyContextInterface *_c, int letIn, const HvMessage *m) {{".format(
                clazz.get_preamble(obj_type),
                obj_id)]
        if len(on_message_list) == 1:
            # if there is only one outlet, skip the switch-case template
            send_message_list.extend(
                HeavyObject._get_on_message_list(on_message_list[0], get_obj_class, objects))
        else:
            send_message_list.append("switch (letIn) {")
            for i in range(len(on_message_list)):
                send_message_list.append("case {0}: {{".format(i))
                send_message_list.extend(
                    HeavyObject._get_on_message_list(on_message_list[i], get_obj_class, objects))
                send_message_list.append("break;")
                send_message_list.append("}")  # end case
            send_message_list.append("default: return;")
            send_message_list.append("}")  # end switch
        send_message_list.append("}")  # end function
        return send_message_list

    @classmethod
    def _get_on_message_list(clazz, on_message_list, get_obj_class, objects):
        out_list = []
        for om in on_message_list:
            out_list.extend(
                get_obj_class(objects[om["id"]]["type"]).get_C_onMessage(
                    objects[om["id"]]["type"],
                    om["id"],
                    om["inletIndex"],
                    objects[om["id"]]["args"]))
        return out_list

    @classmethod
    def _c_buffer(clazz, buffer_dict):
        """ Returns the C represenation of the given buffer.
        """
        if buffer_dict["type"] == "zero":
            return HeavyObject.__C_BUFFER_DICT[buffer_dict["type"]]
        else:
            return "{0}{1}".format(
                HeavyObject.__C_BUFFER_DICT[buffer_dict["type"]],
                buffer_dict["index"])

    @classmethod
    def get_hash(clazz, x):
        """ Compute the message element hash used by msg_getHash().
        Returns a 32-bit integer.
        """
        if isinstance(x, float) or isinstance(x, int):
            # interpret the float bytes as an unsigned integer
            return unpack("@I", pack("@f", float(x)))[0]
        elif x == "bang":
            return 0xFFFFFFFF
        elif isinstance(x, str):
            # this hash is based MurmurHash2
            # http://en.wikipedia.org/wiki/MurmurHash
            # https://sites.google.com/site/murmurhash/
            x = str(x)
            m = 0x5bd1e995
            r = 24
            h = len(x)
            i = 0
            while i < len(x) & ~0x3:
                k = unpack("@I", bytes(x[i:i + 4], encoding='utf-8'))[0]
                k = (k * m) & 0xFFFFFFFF
                k ^= k >> r
                k = (k * m) & 0xFFFFFFFF
                h = (h * m) & 0xFFFFFFFF
                h ^= k
                i += 4

            n = len(x) & 0x3
            x = x[i:i + n]
            if n >= 3:
                h ^= (ord(x[2]) << 16) & 0xFFFFFFFF
            if n >= 2:
                h ^= (ord(x[1]) << 8) & 0xFFFFFFFF
            if n >= 1:
                h ^= ord(x[0])
                h = (h * m) & 0xFFFFFFFF

            h ^= h >> 13
            h = (h * m) & 0xFFFFFFFF
            h ^= h >> 15
            return h
        else:
            raise Exception("Message element hashes can only be computed for float and string types.")

    @classmethod
    def get_hash_string(clazz, x):
        """ Returns the hash as a hex string.
        """
        return "0x{0:X}".format(HeavyObject.get_hash(x))
