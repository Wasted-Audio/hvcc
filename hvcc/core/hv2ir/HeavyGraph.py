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

from collections import Counter
import os
import re

from .BufferPool import BufferPool
from .Connection import Connection
from .LocalVars import LocalVars
from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HIrReceive import HIrReceive
from .HeavyLangObject import HeavyLangObject


class HeavyGraph(HeavyIrObject):
    """ Represents a graph. Subclasses HeavyIrObject for functionality.
        "__graph" does exist as a HeavyIR object, though it has no functionality
        and should not appear in any IR output.
    """

    def __init__(self, graph=None, graph_args=None, file=None, xname=None):
        # zero inlets and outlets until inlet/outlet objects are declared
        HeavyIrObject.__init__(self, "__graph", graph_args, graph, 0, 0)

        # the heavy file which defines this graph
        self.file = file

        # a user-defined name of this graph
        self.xname = xname or "heavy"

        # the dictionary of all objects in the graph
        self.objs = {}

        # set the local arguments
        self.args = graph_args or {}

        # initialise the local variables
        self.local_vars = LocalVars()

        # the list of all constituent inlet and outlet objects
        # graphs always start with no inlet/outlets
        self.inlet_objs = []
        self.outlet_objs = []

        # the set of input/output channels that this graph writes to
        self.input_channel_set = set()
        self.output_channel_set = set()

        # an ordered list of signal objects to process
        self.signal_order = []

        # a pool of signal buffers for use during signal ordering and buffer assignment
        self.buffer_pool = None

    def resolve_arguments(self, obj_args):
        """ Resolves the object arguments based on values from the local graph.
        """
        args = dict(obj_args)  # make a copy of the input arguments
        for key, value in args.items():
            # do any of them reference a variable input?
            if isinstance(value, str):
                if value.find("$") > -1:
                    # is there a value provided for that key in the graph arguments?
                    for k in self.args:
                        # replace all instances of $k with the argument value
                        # do this for all keys in the graph's argument dictionary
                        dollar_key = "$" + k
                        if value.find(dollar_key) > -1:
                            if value == dollar_key:
                                value = self.args[k]  # maintain the original data type
                                break  # break because all dollar arguments have by definition been replaced
                            else:
                                # otherwise assume a string value
                                value = value.replace(dollar_key, str(self.args[k]))
                                # continue around the loop in case value has multiple dollar args

                    if isinstance(value, str) and value.find("$") > -1:
                        # if the variable cannot be resolved, leave it alone.
                        # When the arguments are passed to the object, they will be
                        # set to the default value. These unset variables are simply
                        # removed from the argument dictionary
                        args.pop(key, None)
                        self.add_warning("Variable \"{0}\":\"{1}\" could not be resolved.".format(key, value))
                    else:
                        args[key] = value
        return args

    def connect_objects(self, c, require_intra_graph_connection=True):
        """ Establish a connection from one object to another.
            Typically a connection must be made within a single graph, though
            this requirement may be subpressed.
        """
        if require_intra_graph_connection:
            assert c.from_object.graph is c.to_object.graph, \
                "Conection established between two objects not in the same graph: {0}".format(c)

        # add the connection from the parent to the child
        c.from_object.add_connection(c)

        # add the connection to the child from the parent
        c.to_object.add_connection(c)

    def disconnect_objects(self, c):
        """ Remove a connection from one object to another.
        """
        # remove the connection from the parent to the child
        c.from_object.remove_connection(c)

        # remove the connection to the child from the parent
        c.to_object.remove_connection(c)

    def update_connection(self, c, n_list):
        """ Update the old connection (c) with the new connections (n_list).
            Connection order is maintained. If c is None, this method acts
            as connect_objects(). If n is empty, this method acts as disconnect_objects().
        """
        if c is not None and len(n_list) > 0:
            if all([c.from_object is n.from_object for n in n_list]):
                # connections start at the same point
                c.from_object.replace_connection(c, n_list)
                c.to_object.remove_connection(c)
                for n in n_list:
                    n.to_object.add_connection(n)
            elif all([c.to_object is n.to_object for n in n_list]):
                # connections end at the same point
                c.to_object.replace_connection(c, n_list)
                c.from_object.remove_connection(c)
                for n in n_list:
                    n.from_object.add_connection(n)
            else:
                raise HeavyException("Connections must have a common endpoint: {0} / {1}".format(c, n))
        elif c is not None and len(n_list) == 0:
            self.disconnect_objects(c)  # remove connection c
        elif c is None and len(n_list) > 0:
            for n in n_list:
                self.connect_objects(n)  # add connection n

    def add_object(self, obj, obj_id=None):
        """ Add an object to the graph based on the given id.
            Per-object bookkeeping is performed.
        """

        obj_id = obj_id or obj.id
        if obj_id not in self.objs:
            obj.graph = self
            self.objs[obj_id] = obj

            # some object needs to be specially handled when added to the graph
            if obj.type in ["inlet", "__inlet"]:
                self.inlet_connections.append([])
                self.inlet_buffers.append(("zero", 0))
                self.inlet_objs.append(obj)
                # sort inlet objects according to their index, ascending
                self.inlet_objs.sort(key=lambda o: o.args["index"])
            elif obj.type in ["outlet", "__outlet"]:
                self.outlet_connections.append([])
                self.outlet_buffers.append(("zero", 0))
                self.outlet_objs.append(obj)
                self.outlet_objs.sort(key=lambda o: o.args["index"])
            elif obj.type in ["adc"]:
                self.input_channel_set.update(obj.args["channels"])
            elif obj.type in ["dac"]:
                # if the object is a dac, keep track of the output channels
                # that this graph is writing to
                self.output_channel_set.update(obj.args["channels"])
            elif obj.type in ["receive", "__receive", "send", "__send"]:
                self.__register_named_object(obj, obj.name)
            elif obj.type in ["table", "__table"]:
                self.__register_named_object(
                    obj,
                    obj.name,
                    static=obj.static,
                    unique=True)
            elif obj.type in ["var"] and obj.name is not None:
                self.__register_named_object(
                    obj,
                    obj.name,
                    static=obj.static,
                    unique=True)
        else:
            self.add_error("Duplicate object id {0} found in graph.".format(obj_id))

    def __register_named_object(self, obj, name=None, static=False, unique=False):
        """ Register a named object at the appropriate graph level.
        """

        name = name or obj.name
        if obj.scope == "private" and not static:
            # stay at this level
            self.local_vars.register_object(obj, name, static, unique)
        elif obj.scope == "protected":
            # go up one level
            g = self.graph if self.graph is not None else self
            g.local_vars.register_object(obj, name, static, unique)
        elif obj.scope == "public" or static:
            self.get_root_graph().local_vars.register_object(obj, name, static, unique)
        else:
            raise HeavyException("Unknown scope \"{0}\" for object {1}.".format(obj.scope, obj))

    def __unregister_named_object(self, obj, name=None, static=False, unique=False):
        """ Unregister a named object at the appropriate graph level.
        """

        name = name or obj.name
        if obj.scope == "private" and not static:
            self.local_vars.unregister_object(obj, name)
        elif obj.scope == "protected":
            # go up one level
            g = self.graph if self.graph is not None else self
            g.local_vars.unregister_object(obj, name)
        elif obj.scope == "public" or static:
            self.get_root_graph().local_vars.unregister_object(obj, name)
        else:
            raise HeavyException("Unknown scope \"{0}\" for object {1}.".format(obj.scope, obj))

    def resolve_objects_for_name(self, name, obj_types, local_graph=None):
        """ Returns all objects with the given name and type that are visible
            from this graph. Returns an empty list if no objects could be found.
            The results are otherwise ordered from most local/private first,
            and the most global last.
        """

        obj_types = obj_types if isinstance(obj_types, list) else [obj_types]
        local_graph = local_graph or self

        obj_list = [o for o in self.local_vars.get_objects_for_name(name, obj_types)
                    if not (o.scope == "private" and o.graph is not local_graph)]

        if self.graph is not None:
            obj_list_from_super_graph = self.graph.resolve_objects_for_name(name, obj_types, local_graph)
            obj_list.extend(obj_list_from_super_graph)

        return obj_list

    def resolve_object_for_name(self, name, obj_types, local_graph=None):
        """ Returns the first object with the given name and type that is visible
            from this graph. Returns None if no objects are available.
            This is a convenience method.
        """

        objs = self.resolve_objects_for_name(name, obj_types, local_graph)
        return objs[0] if len(objs) > 0 else None

    def is_root_graph(self):
        """ Returns true if this is the top-level (i.e. root) graph. False otherwise.
        """
        return self.graph is None

    def get_root_graph(self):
        """Returns the top-level graph.
        """
        return self if self.is_root_graph() else self.graph.get_root_graph()

    def find_path_for_abstraction(self, obj_type):
        """ Travels up the graph heirarchy looking for a file path to an abstraction.
            Returns None if no abstraction is found.
        """
        file_path = self.local_vars.find_path_for_abstraction(obj_type)
        if file_path is not None:
            return file_path
        else:
            return self.graph.find_path_for_abstraction(obj_type) if self.graph is not None else None

    def remove_object(self, o, obj_id=None):
        """ Removes an object and all of its connections from the graph.
            A custom id for the object to be removed can be given.
        """
        for connections in o.inlet_connections:
            for c in list(connections):  # make copy of connections as it will be mutated
                self.disconnect_objects(c)
        for connections in o.outlet_connections:
            for c in list(connections):  # make copy
                self.disconnect_objects(c)

        for k, v in self.objs.items():
            if o is v:
                del self.objs[k]
                break

        if o.type in ["receive", "__receive", "send", "__send"]:
            self.__unregister_named_object(o, o.name)

    def get_inlet_object(self, index):
        """ Returns the indexed inlet object of this graph.
        """
        return self.inlet_objs[index]

    def get_outlet_object(self, index):
        """ Returns the indexed outlet object of this graph.
        """
        return self.outlet_objs[index]

    def get_input_channel_set(self, recursive=False):
        """ Returns the set of input channels that this graph writes to.
            Optionally includes all subgraphs as well.
        """
        if recursive:
            channels = set(self.input_channel_set)  # copy the output channel set
            for o in [o for o in self.objs.values() if o.type == "__graph"]:
                channels.update(o.get_input_channel_set(recursive=True))
            return channels
        else:
            return self.input_channel_set

    def get_output_channel_set(self, recursive=False):
        """ Returns the set of output channels that this graph writes to.
            Optionally includes all subgraphs as well.
        """
        if recursive:
            channels = set(self.output_channel_set)  # copy the output channel set
            for o in [o for o in self.objs.values() if o.type == "__graph"]:
                channels.update(o.get_output_channel_set(recursive=True))
            return channels
        else:
            return self.output_channel_set

    def get_notices(self):
        notices = HeavyLangObject.get_notices(self)
        for o in self.objs.values():
            n = o.get_notices()
            notices["warnings"].extend(n["warnings"])
            notices["errors"].extend(n["errors"])
        return notices

    def get_objects_for_type(self, obj_type, recursive=False):
        """ Returns a list of all objects of a given type in this graph.
            The optional parameter "recursive" also includes all objects from subgraphs.
        """
        obj_list = []
        for o in self.objs.values():
            if o.type == "__graph" and recursive:
                obj_list.extend(o.get_objects_for_type(obj_type, recursive))
            elif o.type == obj_type:
                obj_list.append(o)
        return obj_list

    def get_object_counter(self, recursive=False):
        """ Returns a counter of all object types in this graph.
            Graph objects are explicitly removed. "__inlet" and "__outlet"
            objects are renamed to "inlet" and "outlet", for clarity.
            An optional recursive argument includes all subgraphs.
        """
        c = Counter()
        for o in self.objs.values():
            if o.type == "__graph" and recursive:
                c += o.get_object_counter(recursive=True)
            elif o.type in ["__inlet", "__outlet"]:
                c[o.type[2:]] += 1  # remove leading "__"
            else:
                c[o.type] += 1
        return c

    def prepare(self):
        """ Prepares a graph to be exported. Must be called from a root graph.
        """
        assert self.is_root_graph()

        try:
            # apply graph transformations when all graphs have been read
            # All transformations must be recursive.

            # resolve all connection types such that all HeavyLang objects can
            # be correctly reduced
            self._resolve_connection_types()

            # TODO(mhroth): prune unnecessary objects and connections
            # All unnecessary objects and connections should be removed before the
            # graph is reduced. Reduction generally takes into account the existence
            # of connections when deciding on what HeavyIR objects to used.
            self._remove_unused_inlet_connections()

            # reconnect all send~/receive~ objects and remove them from the graph
            self.remap_send_receive()

            # now that the basic graph has been constructed,
            # objects are reduced to their well-defined low-level types.
            # Some objects may be replaced by graphs containing only low-level objects.
            # The graph is changed in-place and consists of only low-level
            # objects and subgraphs. All invalid connections are pruned.
            self.reduce()

            # +~~ expansion
            # ensures that there is at most one signal connection at any inlet
            self.cascade_expansion()

            # fma replacement
            # convert [__mul~f ~f> __add~f] into [__fma~f]
            self.fma_replacement()

            # group all control receivers with the same name under one logical receiver
            self.group_control_receivers()

            # assign signal buffers to signal objects
            # Buffer assignment only takes place at the very end,
            # and does so recursively over all objects and subgraphs.
            # All objects are ordered before buffers are assigned.
            self.assign_signal_buffers()
        except HeavyException as e:
            e.notes = self.get_notices()
            e.notes["has_error"] = True
            e.notes["exception"] = e
            raise e

    def _remove_unused_inlet_connections(self):
        """ Remove connections from inlet object, if there are no incoming
            connections to it. This is a basic approach to pruning unused or
            unnecessary connections, which allow further optimisation later
            in the pipeline.
        """
        for i, cc in enumerate(self.inlet_connections):
            if len(cc) == 0:
                # make copy of outlet_connections list because it will be changed
                for c in list(self.inlet_objs[i].outlet_connections[0]):
                    self.disconnect_objects(c)

        # the recursive bit
        for o in [o for o in self.objs.values() if (o.type == "__graph")]:
            o._remove_unused_inlet_connections()

    def _resolved_outlet_type(self, outlet_index=0):
        # a graph's outlet type depends on the connections incident on the
        # corresponding outlet object
        connection_type_set = {c.type for c in self.outlet_objs[outlet_index].inlet_connections[0]}
        if len(connection_type_set) == 0:
            return "-->"  # object has no incident connections, default to -->
        elif len(connection_type_set) == 1:
            return list(connection_type_set)[0]
        else:
            raise HeavyException(f"{self} has multiple incident connections of differing type.\
                                  The outlet type cannot be explicitly resolved.")

    def _resolve_connection_types(self, obj_stack=None):
        """ Resolves the type of all connections before reduction to IR object types.
            If connections incident on an object are incompatible, they are either
            resolved, potentially by inserting conversion objects, or pruned.
            If a viable resolution cannot be found, an exception may be raised.
        """
        obj_stack = obj_stack or set()
        if self in obj_stack:
            return  # ensure that each object is only resolved once (no infinite loops)
        else:
            obj_stack.add(self)

        # start from all roots and resolve all connections downwards
        for o in [o for o in self.objs.values() if o.is_root()]:
            o._resolve_connection_types(obj_stack)

        # when all internal connections have been resolved,
        # continue the recursion and resolve all outgoing connections
        for c in [c for cc in self.outlet_connections for c in cc]:
            if c.is_mixed:
                # resolve connection type and update it
                connection_type = self._resolved_outlet_type(c.outlet_index)
                self.update_connection(c, [c.copy(type=connection_type)])
            c.to_object._resolve_connection_types(obj_stack)  # turtle on down

    def remap_send_receive(self):
        """ Recursively finds all signal send/receive objects and for each unique
            send name, get all of the sends, and all of the corresponding receives.
            Reconnect all incoming connections to a __add~f, and fan out the results
            to all of receivers' connections. At most one __add~f must
            be added, and a lot of connections remapped.
        """

        sends_dict = self.local_vars.get_registered_objects_for_type("send")
        receives_dict = self.local_vars.get_registered_objects_for_type("receive")

        for (name, send_objs) in sends_dict.items():

            # unconnected send/receives will be removed in the reduce step,
            # if necessary (depending on control or signal functionality).
            # All signal sends will also be removed, regardless of whether they
            # have corresponding receives or not. So here we really only need to
            # be concerned with connecting "normal" signal send/receives.

            # get all signal sends for a name
            s_list = [o for o in send_objs if o.has_inlet_connection_format("f")]
            # assume that all similarly named receives will also be signal format
            r_list = [o for o in receives_dict[name]]

            if len(s_list) == 0:
                continue  # there are no signals going into this send
            elif len(s_list) == 1:
                s = s_list[0]
                c = s.inlet_connections[0][0]  # the connection

                ir_var = HeavyIrObject("__var~f")
                ir_varset = HeavyIrObject("__varwrite~f", {"var_id": ir_var.id})
                s.graph.add_object(ir_var)
                s.graph.add_object(ir_varset)

                # move all connection to send object, to ir_varset
                for c in list(s.inlet_connections[0]):
                    s.graph.update_connection(c, [c.copy(to_object=ir_varset)])

                # move connections from receivers, to be from __var~f
                for o in r_list:
                    ir_varread = HeavyIrObject("__varread~f", {"var_id": ir_var.id})
                    o.graph.add_object(ir_varread)
                    for x in list(o.outlet_connections[0]):
                        o.graph.update_connection(x, [x.copy(from_object=ir_varread)])
            else:
                ir_vars = [HeavyIrObject("__var~f") for s in s_list]
                for i, o in enumerate(s_list):
                    ir_varset = HeavyIrObject("__varwrite~f", {"var_id": ir_vars[i].id})
                    o.graph.add_object(ir_vars[i])
                    o.graph.add_object(ir_varset)
                    for c in list(o.inlet_connections[0]):
                        o.graph.update_connection(c, [c.copy(to_object=ir_varset, inlet_index=0)])

                for r in r_list:
                    ir_add = HeavyIrObject("__add~f")
                    r.graph.add_object(ir_add)

                    for i, s in enumerate(s_list):
                        ir_varread = HeavyIrObject("__varread~f", {"var_id": ir_vars[i].id})
                        r.graph.add_object(ir_varread)
                        r.graph.connect_objects(Connection(
                            from_object=ir_varread,
                            outlet_index=0,
                            to_object=ir_add,
                            inlet_index=(0 if i == 0 else 1),
                            conn_type="~f>"
                        ))

                    for c in list(r.outlet_connections[0]):
                        r.graph.update_connection(c, [c.copy(from_object=ir_add)])

            # when all is said and done, remove the send and receive objects
            for o in s_list:
                o.graph.remove_object(o)
            for o in r_list:
                o.graph.remove_object(o)

    def reduce(self):
        """ Breaks this object into low-level objects. This method returns either
            the object that it is called on, or a graph. In case of a graph, it contains
            only low-level objects. Unnecessary connections are pruned. Because
            this method is called on graphs while they are being constructed, returned
            graphs contains no sub-graphs. Thus this method does not process subgraphs.
        """
        # refactor all constituent objects
        for (obj_id, o) in self.objs.copy().items():
            # use items and not iteritems so that object dictionary remains mutable

            # break the object into atomic (i.e. low-level) objects and
            # update connections. Replace the new representation with the old
            # one in the graph.
            objects, connections = o.reduce()

            # if x is the original object (the case with low-level objects),
            # then no change must be made
            if (len(objects) == 1) and (o in objects):
                continue

            # add the new objects
            for x in objects:
                self.add_object(x)

            # replace existing connections
            # control connection order is maintained
            for c in connections:
                # c is a tuple containing the old and new connections
                # the new connection is a possibly empty list of new connections,
                # indicating that there is no replacement
                self.update_connection(c[0], c[1])

            # remove the old object (and any remaining connections) from the graph
            self.remove_object(o, obj_id=obj_id)
            # o.id may not be the same as obj_id if the object comes from an abstraction

        # a graph is reduced in-place and does not change any connections
        return ({self}, [])

    def cascade_expansion(self):
        """ Turns implicit +~ into explicit cascading +~ trees.
            It is assumed that this simplification operation is run on a reduced graph.
        """
        for o in self.objs.copy().values():  # all items in the graph
            for i in range(len(o.inlet_connections)):  # for each inlet
                # if there is more than one signal connection
                # get all of the signal connections to an object at this inlet
                cc = [c for c in o.inlet_connections[i] if c.is_signal]
                if len(cc) > 1:
                    oL = HeavyIrObject("__add~f")
                    self.add_object(oL)

                    self.update_connection(
                        cc[0],
                        [Connection.copy(cc[0], to_object=oL, inlet_index=0)])
                    self.update_connection(
                        cc[1],
                        [Connection.copy(cc[1], to_object=oL, inlet_index=1)])

                    for j in range(2, len(cc)):
                        x = HeavyIrObject("__add~f")
                        self.add_object(x)

                        self.connect_objects(Connection(
                            from_object=oL,
                            outlet_index=0,
                            to_object=x,
                            inlet_index=0,
                            conn_type="~f>"))
                        self.update_connection(
                            cc[j],
                            [Connection.copy(cc[j], to_object=x, inlet_index=1)])

                        oL = x

                    # add a connection from the last +~ to this inlet
                    self.connect_objects(Connection(
                        from_object=oL,
                        outlet_index=0,
                        to_object=o,
                        inlet_index=i,
                        conn_type="~f>"))

            if o.type == "__graph":
                o.cascade_expansion()

    def fma_replacement(self):
        """ Replace:
            [__mul~f] ~f> [__add~f] with [__fma~f] or
            [__mul~f] ~f> [__sub~f] with [__fms~f]
        """
        # for all __mul~f objects
        for o in self.objs.copy().values():
            if o.type == "__mul~f" \
                    and len(o.inlet_connections[0]) == 1 \
                    and len(o.inlet_connections[1]) == 1 \
                    and len(o.outlet_connections[0]) == 1 \
                    and (o.outlet_connections[0][0].to_object.type == "__add~f"
                         or (o.outlet_connections[0][0].to_object.type == "__sub~f"
                             and o.outlet_connections[0][0].inlet_index == 0)) \
                    and len(o.outlet_connections[0][0].to_object.inlet_connections[0]) == 1 \
                    and len(o.outlet_connections[0][0].to_object.inlet_connections[1]) == 1 \
                    and len(o.outlet_connections[0][0].to_object.outlet_connections[0]) > 0:

                fma_type = "__fma~f" if o.outlet_connections[0][0].to_object.type == "__add~f" else "__fms~f"
                fma = HeavyIrObject(fma_type)
                self.add_object(fma)

                # move connection to left inlet of fma~
                c = o.inlet_connections[0][0]
                self.update_connection(c, [c.copy(to_object=fma)])

                # move connection to right inlet of fma~
                c = o.inlet_connections[1][0]
                self.update_connection(c, [c.copy(to_object=fma)])

                o_add = o.outlet_connections[0][0].to_object

                # move connection to third inlet of fma~ from +~ (not connected to *~)
                i = o.outlet_connections[0][0].inlet_index  # i is either 0 or 1
                # i ^ 1 # use the other inlet; 0 > 1, 1 > 0
                c = o_add.inlet_connections[i ^ 1][0]
                self.update_connection(c, [c.copy(to_object=fma, inlet_index=2)])

                # move all +~ outlet connections to fma~ outlet
                for c in o_add.outlet_connections[0]:
                    self.connect_objects(c.copy(from_object=fma))

                # remove old *~ and +~ objects from the graph
                # (along with any remaining connections)
                o.graph.remove_object(o)  # *~
                o_add.graph.remove_object(o_add)  # +~

            elif o.type == "__graph":
                o.fma_replacement()  # recurse through all subgraphs

    def group_control_receivers(self):
        """ Group all control receivers with the same name under one receiver
            with that name. This way only one message must be scheduled to hit
            all receivers.
        """

        for name, receivers in self.local_vars.get_registered_objects_for_type("__receive").items():

            # ensure that all receiver arguments are consistent
            extern = list(set([r.args["extern"] for r in receivers]) - set([None]))
            attributes = [r.args["attributes"] for r in receivers if len(r.args["attributes"]) > 0]
            scope = list(set([r.annotations["scope"] for r in receivers]))

            if len(extern) > 1:
                self.add_error("Parameter \"{0}\" has conflicting extern types: {1} != {2}".format(
                    name, extern[0], extern[1]))

            # NOTE(mhroth): not checking for conflicting scope types right now. Not sure what to do with it.

            if not all(attributes[0] == a for a in attributes):
                self.add_error("Conflicting min/max/default values for parameter \"{0}\"".format(name))

            # create a new receiver
            recv = HIrReceive("__receive",
                              args={
                                  "name": name,
                                  "extern": extern[0] if len(extern) > 0 else None,
                                  "attributes": attributes[0] if len(attributes) > 0 else {},
                              },
                              annotations={"scope": scope[0]})

            # add new receiver to the top level graph
            self.add_object(recv)

            # sort receivers by priority
            receivers.sort(key=lambda x: x.args["priority"], reverse=True)

            # move all connections to new receiver
            for r in receivers:
                for c in r.outlet_connections[0]:
                    self.connect_objects(c.copy(from_object=recv), require_intra_graph_connection=False)

            # remove old receivers
            for r in receivers:
                r.graph.remove_object(r)

    @property
    def does_process_signal(self):
        # this graph processes a signal if it contains any adc~ (__inlet
        # objects with index > 127)
        return any(o.does_process_signal for o in self.objs.values()) or \
            any(o.args["index"] > 127 for o in self.inlet_objs)

    def order_signal_objects(self):
        """ Places the signal objects in the correct order to be processed.
            Only the objects in this graph are ordered, stopping at the inlet objects.
        """
        # for all leaves of graph, get the parent objects and combine the lists
        self.signal_order = []  # ordered objects
        for o in [o for o in self.objs.values() if o.is_leaf()]:
            self.signal_order.extend(o.get_parent_order())

        # retain only objects that process a signal
        self.signal_order = [o for o in self.signal_order if o.does_process_signal]

    def assign_signal_buffers(self, buffer_pool=None):
        self.buffer_pool = buffer_pool or BufferPool()  # the top-level graph owns the buffer pool

        # before signal buffers can be assigned, the objects must be ordered
        self.order_signal_objects()

        for c_list in self.inlet_connections:
            c_list = [c for c in c_list if c.is_signal]  # only consider signal connections to inlet
            if len(c_list) == 0:
                continue  # no connections at this inlet, it already contains the zero buffer
            if len(c_list) == 1:
                c = c_list[0]  # get the connection

                # get the buffer at the outlet of the connected object
                buf = c.from_object.outlet_buffers[c.outlet_index]

                # assign the buffer to the outlet of the corresponding inlet object
                inlet_obj = self.inlet_objs[c.inlet_index]
                inlet_obj.outlet_buffers[0] = buf

                # ensure that the retain count is accurately reflected by the inlet's connections
                # some inlets are mixed with both signal and control connections, count only the signal connections
                self.buffer_pool.retain_buffer(buf,
                                               len([c for c in inlet_obj.outlet_connections[0] if c.is_signal]) - 1)
            else:
                raise HeavyException("Object {0} in graph {1} has {2} (> 1) signal inputs.".format(
                    inlet_obj,
                    inlet_obj.graph.file,
                    len(c_list)))

        # for all objects in the signal order
        for o in self.signal_order:
            o.assign_signal_buffers(self.buffer_pool)

        # assign the output buffers
        for i, outlet_obj in enumerate(self.outlet_objs):
            # only assign signal buffers to outlets that have incoming signal connections
            c_list = [c for c in outlet_obj.inlet_connections[0] if c.is_signal]
            if len(c_list) == 0:
                continue
            if len(c_list) == 1:
                c = c_list[0]  # get the connection
                buf = c.from_object.outlet_buffers[c.outlet_index]
                self.outlet_buffers[i] = buf
                self.buffer_pool.retain_buffer(buf, len(self.outlet_connections[i]) - 1)
            else:
                raise HeavyException("Object {0} in graph {1} has {2} (> 1) signal inputs.".format(
                    outlet_obj,
                    outlet_obj.graph.file,
                    len(c_list)))

    def __repr__(self):
        if self.xname is not None:
            # TODO(mhroth): does not handle nested subgraph
            return "__graph.{0}({1}/{2})".format(
                self.id,
                os.path.basename(self.file),
                self.xname)
        else:
            return "__graph.{0}({1})".format(self.id, os.path.basename(self.file))

    #
    # Intermediate Representation generators
    #

    def to_ir(self):
        """ Returns Heavy intermediate representation.
        """

        # the set of all input/output signal channels used by the graph
        input_channel_set = self.get_input_channel_set(recursive=True)
        output_channel_set = self.get_output_channel_set(recursive=True)

        return {
            "name": {
                "escaped": re.sub("\W", "_", self.xname),
                "display": self.xname
            },
            "objects": self.get_object_dict(),
            "init": {
                "order": self.get_ir_init_list()
            },
            "tables": self.get_ir_table_dict(),
            "control": {
                "receivers": self.get_ir_receiver_dict(),
                "sendMessage": self.get_ir_control_list()
            },
            "signal": {
                "numInputBuffers": max(input_channel_set) if len(input_channel_set) > 0 else 0,
                "numOutputBuffers": max(output_channel_set) if len(output_channel_set) > 0 else 0,
                "numTemporaryBuffers": {
                    "float": self.buffer_pool.num_buffers("~f>"),
                    "integer": self.buffer_pool.num_buffers("~i>")
                },
                "processOrder": self.get_ir_signal_list()
            }
        }

    def get_object_dict(self):
        # d = {o.id: o.get_object_dict() for o in self.objs.values() if o.type not in
        # ["inlet", "__inlet", "outlet", "__outlet"]}
        d = {}
        for o in self.objs.values():
            # NOTE(mhroth): a bit of a hack to remove unnecessary inlet and outlet ir objects
            if o.type not in ["inlet", "__inlet", "outlet", "__outlet"]:
                d.update(o.get_object_dict())
        return d

    def get_ir_init_list(self):
        """ Init list is returned with all signal objects at the front,
            in the order that they are processed. This is to reduce cache misses
            on the signal object state as the process function is executed.
        """
        init_list = [x for o in self.objs.values() for x in o.get_ir_init_list()]
        signal_list = self.get_ir_signal_list()
        s_init_list = [x["id"] for x in signal_list if x["id"] in init_list]
        i_init_list = [o_id for o_id in init_list if o_id not in s_init_list]
        ordered_init_list = s_init_list + i_init_list
        # ordered_init_list = list(OrderedDict.fromkeys(s_init_list + i_init_list))
        return ordered_init_list

    def get_ir_on_message(self, inlet_index):
        # pass the method through the inlet object, but only follow control connections
        x = []
        for c in self.inlet_objs[inlet_index].outlet_connections[0]:
            if c.is_control:
                x.extend(c.to_object.get_ir_on_message(c.inlet_index))
        return x

    def get_ir_table_dict(self):
        """ Returns a dictionary of all publicly visible tables at the root graph
            and their ids.
        """
        assert self.is_root_graph(), "This function should only be called from the root graph."
        d = self.local_vars.get_registered_objects_for_type("__table")
        # update(), because tables can be registered either as Heavy tables
        # or HeavyIr __tables. We need to be able to handle them both.
        d.update(self.local_vars.get_registered_objects_for_type("table"))

        e = {}
        for k, v in d.items():
            # escape table key to be used as the value for code stubs
            key = ("_" + k) if re.match("\d", k) else k
            if key not in e:
                e[key] = {
                    "id": v[0].id,
                    "display": k,
                    "hash": "0x{0:X}".format(HeavyLangObject.get_hash(k)),
                    "extern": v[0].args["extern"]
                }
        return e

    def get_ir_control_list(self):
        return [x for o in self.objs.values() for x in o.get_ir_control_list()]

    def get_ir_receiver_dict(self):
        # NOTE(mhroth): this code assumes that v is always an array of length 1,
        # as the grouping of control receivers should have grouped all same-named
        # receivers into one logical receiver.
        # NOTE(mhroth): a code-compatible name is only necessary for externed receivers
        return {(("_" + k) if re.match("\d", k) else k): {
            "display": k,
            "hash": "0x{0:X}".format(HeavyLangObject.get_hash(k)),
            "extern": v[0].args["extern"],
            "attributes": v[0].args["attributes"],
            "ids": [v[0].id]
        } for k, v in self.local_vars.get_registered_objects_for_type("__receive").items()}

    def get_ir_signal_list(self):
        return [x for o in self.signal_order for x in o.get_ir_signal_list()]
