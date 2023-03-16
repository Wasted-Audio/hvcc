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

import decimal
import json
import os
import random
import string

from struct import unpack, pack
from typing import Optional, Union, List, Dict, Any, TYPE_CHECKING

from .Connection import Connection
from .HeavyException import HeavyException

if TYPE_CHECKING:
    from .HeavyGraph import HeavyGraph
    from .HeavyIrObject import HeavyIrObject


class HeavyLangObject:
    """ This is the base Heavy object class.
    """

    __RANDOM = random.Random()
    __ID_CHARS = string.ascii_letters + string.digits

    # load the Heavy object definitions
    with open(os.path.join(os.path.dirname(__file__), "../json/heavy.lang.json"), "r") as f:
        _HEAVY_LANG_DICT = json.load(f)

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional['HeavyGraph'] = None,
        num_inlets: int = -1,
        num_outlets: int = -1,
        annotations: Optional[Dict] = None
    ) -> None:
        # set the object type
        self.type = obj_type

        # generate a unique id for this object
        self.id = "".join(self.__RANDOM.choice(self.__ID_CHARS) for _ in range(8))

        # assign the parent graph
        self.graph = graph

        # set local arguments
        self.args: Dict = args or {}

        # set local annotations
        self.annotations: Dict = annotations or {}

        # a list of locally generated warnings and errors (notifications)
        self.warnings: List = []
        self.errors: List = []

        # resolve arguments and fill in missing defaults for HeavyLang objects
        self.__resolve_default_lang_args()

        # the list of connections at each inlet
        num_inlets = num_inlets if num_inlets >= 0 else len(self._obj_desc["inlets"])
        self.inlet_connections: List = [[] for _ in range(num_inlets)]

        # the list of connections at each outlet
        num_outlets = num_outlets if num_outlets >= 0 else len(self._obj_desc["outlets"])
        self.outlet_connections: List = [[] for _ in range(num_outlets)]

    @property
    def scope(self) -> str:
        """ Returns the scope of this object, private by default.
            Scope may be public, protected, private.
        """
        return self.annotations.get("scope", "private")

    @property
    def static(self) -> bool:
        """ Returns true of this object is marked as static. False by default.
        """
        return self.annotations.get("static", False)

    @property
    def const(self) -> bool:
        """ Returns true of this object is marked as constant. False by default.
        """
        return self.annotations.get("const", False)

    @property
    def name(self) -> Optional[str]:
        """ Returns the name of this object. Returns None if there is no name.
        """
        return self.args.get("name", None)

    @property
    def _obj_desc(self) -> Dict:
        """ Returns the HeavyLang object description.
        """
        return self._HEAVY_LANG_DICT[self.type]

    def inlet_connection_type(self, index: int) -> Dict:
        return self._obj_desc["inlets"][index]

    def outlet_connection_type(self, index: int) -> Dict:
        return self._obj_desc["outlets"][index]

    def name_for_arg(self, index: int = 0) -> str:
        """ Returns the name of the argument at the given index.
        """
        return self._obj_desc["args"][index]["name"]

    def add_warning(self, warning: str) -> None:
        """ Add a warning to this object.
        """
        self.warnings.append({"message": warning})

    def add_error(self, error: str) -> None:
        """ Add an error to this object and raise an exception.
        """
        self.errors.append({"message": error})
        raise HeavyException(error)

    def get_notices(self) -> Dict:
        """ Returns a dictionary of all warnings and errors at this object.
        """
        return {
            "warnings": [{"message": f"{self}: {n['message']}"} for n in self.warnings],
            "errors": [{"message": f"{self}: {n['message']}"} for n in self.errors],
        }

    @classmethod
    def force_arg_type(cls, value: Any, value_type: str, graph: Optional['HeavyGraph'] = None) -> Any:
        """ Attempts to convert a value to a given value type. Raises an Exception otherwise.
            If the value_type is unknown and a graph is provided, a warning will be registered.
        """
        if value_type == "float":
            try:
                return float(value)
            except Exception:
                raise Exception(f"Cannot convert argument \"{value}\" into float.")
        elif value_type == "int":
            return int(decimal.Decimal(value))
        elif value_type == "string":
            return str(value) if value is not None else None
        elif value_type == "boolean":
            if isinstance(value, str):
                return value.strip().lower() not in ["false", "f", "0"]
            else:
                return bool(value)
        elif value_type == "floatarray":
            if isinstance(value, list):
                return [float(v) for v in value]
            if isinstance(value, str):
                return [float(v) for v in value.split()]
            else:
                raise HeavyException(f"Cannot convert value to type floatarray: {value}")
        elif value_type == "intarray":
            if isinstance(value, list):
                return [int(v) for v in value]
            if isinstance(value, str):
                return [int(v) for v in value.split()]
            else:
                raise HeavyException(f"Cannot convert value to type intarray: {value}")
        elif value_type == "stringarray":
            if isinstance(value, list):
                return [str(v) for v in value]
            if isinstance(value, str):
                return [str(v) for v in value.split()]
            else:
                raise HeavyException(f"Cannot convert value to type stringarray: {value}")
        else:
            # NOTE(mhroth): if value_type is not a known type or None, that is
            # not necessarily an error. It may simply be that the value should
            # not be resolved to anything other than what it already is.
            # This happens most often with message objects.
            # if graph is not None:
            #     graph.add_warning(f"Unknown value type \"{value_type}\" for value: {value}")
            return value

    def __resolve_default_lang_args(self) -> None:
        """ Resolves missing default arguments. Also checks to make sure that all
            required arguments are present. Does nothing if the object is IR.
        """
        if self.type in HeavyLangObject._HEAVY_LANG_DICT:
            for arg in self._obj_desc["args"]:
                if arg["name"] not in self.args:
                    # if a defined argument is not in the argument dictionary
                    if not arg["required"]:
                        # if the argument is not required, use the default
                        self.args[arg["name"]] = arg["default"]
                    else:
                        self.add_error(f"Required argument \"{arg['name']}\" not present for object {self}.")
                else:
                    # enforce argument types
                    self.args[arg["name"]] = HeavyLangObject.force_arg_type(
                        self.args[arg["name"]],
                        arg["value_type"],
                        self.graph)

    @property
    def num_inlets(self) -> int:
        return len(self.inlet_connections)

    @property
    def num_outlets(self) -> int:
        return len(self.outlet_connections)

    def add_connection(self, c: Connection) -> None:
        """ Add a connection to this object.
        """
        try:
            if c.to_object is self:
                self.inlet_connections[c.inlet_index].append(c)
            elif c.from_object is self:
                self.outlet_connections[c.outlet_index].append(c)
            else:
                raise HeavyException(f"Connection {c} does not connect to this object {self}.")
        except Exception:
            raise HeavyException(f"Connection {c} connects to out-of-range let.")

    def remove_connection(self, c: Connection) -> None:
        """ Remove a connection to this object.
        """
        if c.to_object is self:
            self.inlet_connections[c.inlet_index].remove(c)
        elif c.from_object is self:
            self.outlet_connections[c.outlet_index].remove(c)
        else:
            raise HeavyException(f"Connection {c} does not connect to this object {self}.")

    def replace_connection(self, c: Connection, n_list: list) -> None:
        """ Replaces connection c with connection list n_list, maintaining connection order
        """
        if c.from_object is self:
            cc = self.outlet_connections[c.outlet_index]
            # NOTE(mhroth): this will throw an exception if c does not exist
            # if a heavy object connects to itself, such as through a [t a]
            # or directly, there may be an error here,
            i = cc.index(c)
            self.outlet_connections[c.outlet_index] = cc[0:i] + n_list + cc[i + 1:]
        elif c.to_object is self:
            # connection order doesn't matter at the inlet
            self.inlet_connections[c.inlet_index].remove(c)
            self.inlet_connections[c.inlet_index].extend(n_list)
        else:
            raise HeavyException(f"Connections must have a common endpoint: {c} / {n_list}")

    def get_connection_move_list(self, o: 'HeavyIrObject', connection_type_filter: str = "-~>") -> List:
        """ Create a list of commands to move all connections from this object
            to the given object o.
        """
        m = []
        for c in [c for cc in self.inlet_connections for c in cc]:
            m.append((c, [c.copy(to_object=o)]))
        for c in [c for cc in self.outlet_connections for c in cc]:
            m.append((c, [c.copy(from_object=o)]))
        return m

    def _get_connection_format(self, connections_list: List) -> str:
        fmt = []
        for cc in connections_list:
            s = {c.type for c in cc}
            if len(s) == 0:
                fmt.append("_")
            elif len(s) == 1:
                if "-->" in s:
                    fmt.append("c")
                elif "~f>" in s:
                    fmt.append("f")
                elif "~i>" in s:
                    fmt.append("i")
                else:
                    raise Exception(f"Unknown connection type in set {cc} in file {cc[0].from_object.graph.file}.")
            elif s in [{"~f>", "-->"}, {"~i>", "-->"}]:
                fmt.append("m")
            else:
                fmt.append("m")
        return "".join(fmt)

    def has_inlet_connection_format(self, fmts: Optional[Union[str, List]] = None) -> bool:
        """ Returns true if the object has given format at its inlets.
        """
        fmts = fmts if isinstance(fmts, list) else [fmts]
        return self._get_connection_format(self.inlet_connections) in fmts

    def has_outlet_connection_format(self, fmts: Optional[Union[str, List]] = None) -> bool:
        """ Returns true if the object has given format at its outlets.
            Take either litteral or list as input.
        """
        fmts = fmts if isinstance(fmts, list) else [fmts]
        return self._get_connection_format(self.outlet_connections) in fmts

    def is_leaf(self) -> bool:
        """ Returns True if this object is a leaf in the graph. False otherwise.
        """
        return all(len(c) == 0 for c in self.outlet_connections)

    def is_root(self) -> bool:
        """ Returns True if this object is a root in the graph. False otherwise.
        """
        return all(len(c) == 0 for c in self.inlet_connections)

    def _resolved_outlet_type(self, outlet_index: int = 0) -> Optional[str]:
        """ Returns the connection type expected at the given outlet.
            The result may be influenced by the state of the input connections.
        """
        # get the defined connection type
        connection_type = self._obj_desc["outlets"][outlet_index]["connectionType"]
        if connection_type == "-~>" and self.graph is not None:
            # if the connection type is defined as mixed,
            # use the default approach to resolve it
            connection_type_set = {c.type for c in self.inlet_connections[0]}
            if len(connection_type_set) == 0:
                return "-->"
            elif len(connection_type_set) == 1:
                return list(connection_type_set)[0]
            elif len(connection_type_set) == 2:
                if {"-->", "~f>"} == connection_type_set:
                    return "~f>"
                elif {"-->", "~i>"} == connection_type_set:
                    return "~i>"
            # if the connection type cannot be resolved to a well-defined type
            self.graph.add_error("Connection type cannot be resolved."
                                 f"Unknown inlet connection type configuration: {connection_type_set}")
        else:
            return connection_type

        return None

    def _resolve_connection_types(self, obj_stack: Optional[set] = None) -> Optional[None]:
        """ Resolves the type of all connections before reduction to IR object types.
            If connections incident on an object are incompatible, they are either
            resolved, potentially by inserting conversion objects, or pruned.
            If a viable resolution cannot be found, an exception may be raised.
        """
        obj_stack = obj_stack or set()
        if self in obj_stack:
            return
        else:
            obj_stack.add(self)

        # for all outgoing connections
        if self.graph is not None:
            for c in [c for cc in self.outlet_connections for c in cc]:
                if c.is_mixed:
                    connection_type = self._resolved_outlet_type(outlet_index=c.outlet_index)
                    if connection_type == "-~>":
                        self.graph.add_error("Cannot resolve connection type from -~>.")
                    else:
                        self.graph.update_connection(c, [c.copy(type=connection_type)])

                c.to_object._resolve_connection_types(obj_stack)  # turtle all the way down

    @classmethod
    def get_hash(cls, x: str) -> int:
        """ Compute the message element hash used by msg_getHash(). Returns a 32-bit integer.
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
                k = unpack("@I", bytes(x[i:i + 4], "utf-8"))[0]
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

    def __repr__(self) -> str:
        arg_str = " ".join([f"{k}:{o}" for (k, o) in self.args.items()])
        return f"{self.type} {{{arg_str}}}" if len(arg_str) > 0 else self.type
