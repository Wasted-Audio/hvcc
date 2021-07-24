# Copyright 2018 Enzien Audio, Ltd. All Rights Reserved.

import os

from .Connection import Connection
from .PdGraph import PdGraph
from .HeavyObject import HeavyObject


class PdLibSignalGraph(PdGraph):

    def __init__(self, obj_args, pd_path, pos_x=0, pos_y=0):
        PdGraph.__init__(self, obj_args, pd_path, pos_x, pos_y)

    def validate_configuration(self):
        """ Auto-detect control only connections to expected signal inlets and
            insert a sig~ (var) object inbetween to ensure it doesn't break.
        """
        # Note(joe): only checking first inlet, should we check all inlets by
        # default? i.e. samphold~ has a 2nd inlet that requires checking
        conns = self._inlet_connections.get("0", [])

        # only do this if no signal connections are present
        if (len([c for c in conns if c.conn_type == "~f>"]) == 0) and len(conns) > 0:

            # add sig~ object to parent graph
            sig_obj = HeavyObject(
                obj_type="var",
                obj_args=[0],
                pos_x=int(self.pos_x),
                pos_y=int(self.pos_y - 5))  # shift upwards a few points
            self.parent_graph.add_object(sig_obj)

            # add connection from sig~ to this abstraction
            c = Connection(sig_obj, 0, self, 0, "~f>")
            self.parent_graph._PdGraph__connections.append(c)  # update the local connections list
            sig_obj.add_connection(c)
            self.add_connection(c)

            # retrieve all control connections
            control_conns = [c for c in conns if c.conn_type == "-->"]

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

        # make sure to call parent validate_configuration()
        PdGraph.validate_configuration(self)

    def __repr__(self):
        return "[{0} {1}]".format(
            os.path.splitext(os.path.basename(self._PdGraph__pd_path))[0],
            " ".join(self.obj_args[1:]))
