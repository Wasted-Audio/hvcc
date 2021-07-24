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

import json
import os

from hvcc.core.hv2ir.Connection import Connection
from hvcc.core.hv2ir.HeavyException import HeavyException
from hvcc.core.hv2ir.HeavyLangObject import HeavyLangObject


class HeavyIrObject(HeavyLangObject):
    """ Intermediate Representation (IR) objects are atomic and have
        strictly defined interfaces and types. These are generally defined in
        the file heavy.ir.json.
    """

    # load the HeavyIR object definitions
    with open(os.path.join(os.path.dirname(__file__), "../json/heavy.ir.json"), "r") as f:
        __HEAVY_OBJS_IR_DICT = json.load(f)

    def __init__(self, obj_type, args=None, graph=None, num_inlets=-1, num_outlets=-1, annotations=None):
        # allow the number of inlets and outlets to be overridden
        num_inlets = len(HeavyIrObject.__HEAVY_OBJS_IR_DICT[obj_type]["inlets"]) if num_inlets < 0 else num_inlets

        num_outlets = len(HeavyIrObject.__HEAVY_OBJS_IR_DICT[obj_type]["outlets"]) if num_outlets < 0 else num_outlets

        HeavyLangObject.__init__(self, obj_type, args, graph, num_inlets, num_outlets, annotations)

        # resolve arguments and fill in missing defaults for HeavyIR objects
        self.__resolve_default_ir_args()

        # the list of signal buffers at the inlets and outlets
        # these are filled in by HeavyGraph.assign_signal_buffers()
        self.inlet_buffers = [("zero", 0)] * self.num_inlets
        self.outlet_buffers = [("zero", 0)] * self.num_outlets

        # True if this object has already been ordered in the signal chain
        self.__is_ordered = False

    def __resolve_default_ir_args(self):
        """ Resolves missing default arguments. Also checks to make sure that all
            required arguments are present.
        """
        if self.type in HeavyIrObject.__HEAVY_OBJS_IR_DICT:
            for arg in self.__obj_desc.get("args", []):
                if arg["name"] not in self.args:
                    # if a defined argument is not in the argument dictionary
                    if not arg["required"]:
                        # if the argument is not required, use the default
                        self.args[arg["name"]] = arg["default"]
                    else:
                        self.add_error("Required argument \"{0}\" not present for object {1}.".format(
                            arg["name"],
                            self))
                else:
                    # enforce argument types.
                    # if the default argument is null, don't worry about about the arg
                    if arg["default"] is not None:
                        self.args[arg["name"]] = HeavyLangObject.force_arg_type(
                            self.args[arg["name"]],
                            arg["value_type"],
                            self.graph)

    @classmethod
    def is_ir(clazz, obj_type):
        """Returns true if the type is an IR object. False otherwise.
        """
        return obj_type in HeavyIrObject.__HEAVY_OBJS_IR_DICT

    @property
    def does_process_signal(self):
        """Returns True if this object processes a signal. False otherwise.
        """
        return self.__obj_desc["ir"]["signal"]

    @property
    def __obj_desc(self):
        """ Returns the original HeavyIR object description.
        """
        return HeavyIrObject.__HEAVY_OBJS_IR_DICT[self.type]

    def inlet_requires_signal(self, inlet_index=0):
        """ Returns True if the indexed inlet requires a signal connection. False otherwise.
        """
        return self.__obj_desc["inlets"][inlet_index] in ["~i>", "~f>"]

    def outlet_requires_signal(self, inlet_index=0):
        """ Returns True if the indexed outlet requires a signal connection. False otherwise.
        """
        return self.__obj_desc["outlets"][inlet_index] in ["~i>", "~f>"]

    def reduce(self):
        # A Heavy IR object is already reduced. Returns itself and no connection changes.
        return ({self}, [])

    def get_parent_order(self):
        """ Returns a list of all objects in process order, with this object at the end.
        """
        if self.__is_ordered:
            return []
        else:
            self.__is_ordered = True
            if self.is_root():
                return [self]
            else:
                order_list = []
                for c in [c for inlet in self.inlet_connections for c in inlet]:
                    order_list.extend(c.from_object.get_parent_order())
                order_list.append(self)
                return order_list

    def assign_signal_buffers(self, buffer_pool):
        # assign the inlet buffers
        for cc in self.inlet_connections:
            cc = [c for c in cc if c.is_signal]  # only need to deal with signal connections
            if len(cc) == 0:
                continue
            if len(cc) == 1:
                c = cc[0]  # get the connection

                # get the buffer at the outlet of the connected object
                buf = c.from_object.outlet_buffers[c.outlet_index]

                # assign the buffer to the inlet of this object
                self.inlet_buffers[c.inlet_index] = buf

                # decrease the retain count of the buffer
                buffer_pool.release_buffer(buf)
            else:
                raise HeavyException("This object has {0} (> 1) signal inputs.".format(len(cc)))

        # assign the output buffers
        exclude_set = set()

        for i in range(self.num_outlets):
            # buffers are assigned even if the outlet has no connections.
            # The buffer will still be filled. However, if the buffer has already
            # been set (i.e. non-zero) (e.g. in the case of dac~),
            # then we skip this set

            connection_type = self._resolved_outlet_type(outlet_index=i)
            if Connection.is_signal_type(connection_type) and self.outlet_buffers[i][0] == "zero":
                b = buffer_pool.get_buffer(
                    connection_type,
                    len(self.outlet_connections[i]),
                    exclude_set)
                self.outlet_buffers[i] = b

                # if the buffer has no dependencies, make sure that it isn't reused
                # right away. All outlets should have independent buffers.
                if len(self.outlet_connections[i]) == 0:
                    exclude_set.add(b)

    def _resolved_outlet_type(self, outlet_index=0):
        """ Returns the connection type at the given outlet.
            This information is always well-defined for IR objects.
        """
        return self.__obj_desc["outlets"][outlet_index]

    #
    # Intermediate Representation generators
    #

    def get_object_dict(self):
        """ Returns a dictionary of all constituent low-level objects,
            indexed by id, including their arguments and type.
        """
        return {
            self.id: {
                "args": self.args,
                "type": self.type
            }
        }

    def get_ir_init_list(self):
        """ Returns a list of all object id for obejcts that need initialisation.
        """
        return [self.id] if self.__obj_desc["ir"]["init"] else []

    def get_ir_on_message(self, inlet_index=0):
        """ Returns an array of dictionaries containing the information for the
            corresponding on_message call.
        """
        return [{
            "id": self.id,
            "inletIndex": inlet_index
        }]

    def get_ir_control_list(self):
        """ Returns the intermediate representation for object control functions.
            Basically, does sendMessage() need to be written?
        """
        if self.__obj_desc["ir"]["control"]:
            on_message_list = []
            for connections in self.outlet_connections:
                on_messages_let = []
                # only look at control connections
                for c in [c for c in connections if c.is_control]:
                    on_messages_let.extend(c.to_object.get_ir_on_message(c.inlet_index))
                on_message_list.append(on_messages_let)
            return [{
                "id": self.id,
                "onMessage": on_message_list
            }]
        else:
            return []

    def get_ir_signal_list(self):
        """ Returns the intermediate representation for object process functions.
            Only outputs buffer information for lets that require a signal.
        """
        # we assume that this method will only be called on signal objects
        assert self.__obj_desc["ir"]["signal"]

        return [{
            "id": self.id,
            "inputBuffers": [
                {"type": b[0], "index": b[1]} for i, b in enumerate(self.inlet_buffers)
                if self.inlet_requires_signal(i)],
            "outputBuffers": [
                {"type": b[0], "index": b[1]} for i, b in enumerate(self.outlet_buffers)
                if self.outlet_requires_signal(i)]
        }]
