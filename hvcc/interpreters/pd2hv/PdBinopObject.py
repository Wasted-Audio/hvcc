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

from .Connection import Connection
from .PdObject import PdObject
from .HeavyObject import HeavyObject


class PdBinopObject(PdObject):
    # a translation dictionary from a Pd object to corresponding heavy object
    __PD_HEAVY_DICT = {
        "+": "+",
        "+~": "+",
        "-": "-",
        "-~": "-",
        "*": "*",
        "*~": "*",
        "/": "/",
        "/~": "/",
        "mod": "mod",
        "%": "%",
        "max": "max",
        "max~": "max",
        "min": "min",
        "min~": "min",
        "&": "&",
        "&&": "&&",
        "|": "|",
        "||": "||",
        "==": "==",
        "!=": "!=",
        "<": "<",
        "<=": "<=",
        ">": ">",
        ">=": ">=",
        "pow": "pow",
        "pow~": "pow",
        ">>": ">>",
        "<<": "<<"
    }

    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert PdBinopObject.is_binop(obj_type)
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

    @classmethod
    def is_binop(clazz, obj_type):
        return obj_type in PdBinopObject.__PD_HEAVY_DICT

    @classmethod
    def get_supported_objects(clazz):
        return list(PdBinopObject.__PD_HEAVY_DICT.keys())

    def validate_configuration(self):
        # check signal objects for control connections and auto insert
        # heavy var objects where necessary
        if self.obj_type.endswith("~"):

            # left inlet check
            conns_left = self._inlet_connections.get("0", [])

            if len(conns_left) == 0:
                # no left inlet connections
                self.convert_ctrl_to_sig_connections_at_inlet([], 0)
            elif (len([c for c in conns_left if c.conn_type == "~f>"]) == 0) and len(conns_left) > 0:
                # control connection and no sig connection
                self.convert_ctrl_to_sig_connections_at_inlet(conns_left, 0)

            # right inlet check
            conns_right = self._inlet_connections.get("1", [])
            num_signal_conns = len([c for c in conns_right if c.conn_type == "~f>"])

            if len(self.obj_args) > 0 and num_signal_conns > 0:
                # TODO(joe): removing this connection instead of throwing an error
                # would be compatible with Pd's behaviour
                self.add_error("signal outlet connected to nonsignal inlet")

            if len(self.obj_args) == 0 and num_signal_conns == 0 and len(conns_right) > 0:
                # any arguments present will create a control type right inlet
                self.convert_ctrl_to_sig_connections_at_inlet(conns_right, 1)

        if len(self.obj_args) > 0:
            try:
                self.__k = float(self.obj_args[0])
            except Exception:
                self.add_warning(f"\"{self.obj_args[0]}\" cannot be resolved to a number. Defaulting to zero.")
                self.__k = 0.0
        else:
            self.__k = 0.0

    def convert_ctrl_to_sig_connections_at_inlet(self, connection_list, inlet_index):
        """ Auto insert heavy var object inbetween control connections.
        """
        sig_obj = HeavyObject(obj_type="var",
                              obj_args=[0],
                              pos_x=int(self.pos_x),
                              pos_y=int(self.pos_y - 5))  # shift upwards a few points

        # add sig~ object to parent graph
        self.parent_graph.add_object(sig_obj)

        # add connection from sig~ to this object
        c = Connection(sig_obj, 0, self, inlet_index, "~f>")
        self.parent_graph._PdGraph__connections.append(c)  # update the local connections list
        sig_obj.add_connection(c)
        self.add_connection(c)

        # retrieve all control connections
        control_conns = [c for c in connection_list if c.conn_type == "-->"]

        for old_conn in control_conns:
            # get from obj
            from_obj = old_conn.from_obj

            # add connection from fromobj to new sig
            new_conn = Connection(from_obj, old_conn.outlet_index, sig_obj, 0, "-->")
            self.parent_graph._PdGraph__connections.append(new_conn)
            sig_obj.add_connection(new_conn)
            from_obj.add_connection(new_conn)

            # remove connection from fromobj
            self.parent_graph._PdGraph__connections.remove(old_conn)
            from_obj.remove_connection(old_conn)
            self.remove_connection(old_conn)

    def to_hv(self):
        return {
            "type": PdBinopObject.__PD_HEAVY_DICT[self.obj_type],
            "args": {
                "k": self.__k
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
