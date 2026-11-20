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

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from .Connection import Connection
from .HeavyGraph import HeavyGraph
from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject


class HLangBinop(HeavyLangObject):

    __HEAVY_DICT: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType({
        "+": ("__add", "__add_k", "__add~f", "__add~i"),
        "-": ("__sub", "__sub_k", "__sub~f", "__sub~i"),
        "*": ("__mul", "__mul_k", "__mul~f", "__mul~i"),
        "/": ("__div", "__div_k", "__div~f", "__div~i"),
        "max": ("__max", "__max_k", "__max~f", "__max~i"),
        "min": ("__min", "__min_k", "__min~f", "__min~i"),
        ">": ("__gt", "__gt_k", "__gt~f", "__gt~i"),
        ">=": ("__gte", "__gte_k", "__gte~f", "__gte~i"),
        "==": ("__eq", "__eq_k", "__eq~f", "__eq~i"),
        "!=": ("__neq", "__neq_k", "__neq~f", "__neq~i"),
        "<": ("__lt", "__lt_k", "__lt~f", "__lt~i"),
        "<=": ("__lte", "__lte_k", "__lte~f", "__lte~i"),
        "&": ("__and", "__and_k", "__and~f", "__and~i"),    # binary and
        "&&": ("__logand", "__logand_k"),                   # logical or
        "&!": ("__andnot", "__andnot~f", "__andnot~i"),
        "|": ("__or", "__or_k", "__or~f", "__or~i"),        # binary or
        "||": ("__logor", "__logor_k"),                     # logical or
        "pow": ("__pow", "__pow_k", "__pow~f", "__pow~i"),
        "atan2": ("__atan2", "__atan2_k", "__atan2~f"),
        "mod": ("__unimod", "__unimod_k"),
        "%": ("__bimod", "__bimod_k"),
        ">>": ("__shiftright", "__shiftright_k"),           # binary right shift
        "<<": ("__shiftleft", "__shiftleft_k")              # binary left shift
    })

    # Comparison IR objects used for Pd/Cyclone's <~, <=~, >~, >=~, ==~ and !=~.
    __SIGNAL_COMPARISONS: Final[frozenset[str]] = frozenset({
        "__gt~f", "__gte~f", "__eq~f", "__neq~f", "__lt~f", "__lte~f"})

    def __init__(
        self,
        obj_type: str,
        args: dict | None = None,
        graph: HeavyGraph | None = None,
        annotations: dict | None = None
    ) -> None:
        super().__init__(obj_type, args, graph,
                         num_inlets=2,
                         num_outlets=1,
                         annotations=annotations)

    @classmethod
    def handles_type(cls, obj_type: str) -> bool:
        """Returns True if this class handles the given object type. False otherwise.
        """
        return obj_type in cls.__HEAVY_DICT

    def reduce(self) -> tuple | None:
        result = self._reduce()
        if result is None:
            return None
        return self._mask_comparison_result(*result)

    def _mask_comparison_result(self, obj_set: set, connections: list) -> tuple:
        """Turn the bit mask of a float signal comparison into Pd's 1.0 or 0.0.

        The IR comparisons return a SIMD mask: all bits set for true, all clear
        for false. Read as a float, the all-set mask is NaN. AND-ing with the
        bit pattern of 1.0 (0x3F800000) gives 1.0 or 0.0:

            0xFFFFFFFF & 0x3F800000 == 0x3F800000  # 1.0
            0x00000000 & 0x3F800000 == 0x00000000  # 0.0

        A no-op on HV_SIMD_NONE, where comparisons already yield 1.0 or 0.0.
        """
        cmp = next((x for x in obj_set if x.type in self.__SIGNAL_COMPARISONS), None)
        if cmp is None:
            return (obj_set, connections)

        mask = HeavyIrObject("__and~f")
        one = HeavyIrObject("__var_k~f", args={"k": 1.0})

        rewired = [
            (source, [c.copy(from_object=mask) if c.from_object is cmp else c for c in new_connections])
            for source, new_connections in connections
        ]

        rewired.append((None, [
            Connection(cmp, 0, mask, 0, "~f>"),
            Connection(one, 0, mask, 1, "~f>")
        ]))
        return (obj_set | {mask, one}, rewired)

    def _reduce(self) -> tuple | None:
        if self.has_inlet_connection_format("__") or \
                self.has_inlet_connection_format("_c") or \
                self.has_inlet_connection_format("_f") or \
                self.has_outlet_connection_format("_"):
            # binary operator objects must have a left inlet or outlet connection.
            return (set(), [])  # remove this object

        if self.has_inlet_connection_format("ff"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~f"))
            x = HeavyIrObject(ir_type)
            return ({x}, self.get_connection_move_list(x))

        elif self.has_inlet_connection_format("fc"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~f"))
            x = HeavyIrObject(ir_type)
            y = HeavyIrObject("__var~f", {"k": self.args[self.name_for_arg()]})
            z = HeavyIrObject("__varread~f", {"var_id": y.id})
            connections = [(None, [Connection(z, 0, x, 1, "~f>")])]
            for c in self.inlet_connections[0]:  # left inlet to ir_type
                connections.append((c, [c.copy(to_object=x)]))
            for c in self.inlet_connections[1]:  # right inlet to __var~f
                connections.append((c, [c.copy(to_object=y, inlet_index=0)]))
            for c in self.outlet_connections[0]:  # ir_type outlet
                connections.append((c, [c.copy(from_object=x)]))
            return ({x, y, z}, connections)

        elif self.has_inlet_connection_format("f_"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~f"))

            # handle identity-operations
            if (self.type == "+" and self.args["k"] == 0.0) or \
                    (self.type == "-" and self.args["k"] == 0.0) or \
                    (self.type == "*" and self.args["k"] == 1.0) or \
                    (self.type == "/" and self.args["k"] == 1.0):
                if len(self.inlet_connections[0]) == 0:
                    return (set(), [])  # remove this object
                elif len(self.inlet_connections[0]) == 1:
                    # there is only one connection, pass through the connection
                    # and remove this object
                    c = self.inlet_connections[0][0]
                    connections = [(c, [c.copy(to_object=v.to_object, inlet_index=v.inlet_index) for
                                        v in self.outlet_connections[0]])]
                    return (set(), connections)
                else:  # len(self.inlet_connections[0]) > 1
                    # there are multiple connections to the left inlet
                    # create a __add~f, move one connection to the left inlet
                    # and the remainder to the right inlet
                    x = HeavyIrObject("__add~f")
                    c = self.inlet_connections[0][0]
                    connections = [(c, [c.copy(to_object=x, inlet_index=0)])]
                    for c in self.inlet_connections[0][1:]:
                        connections.append((c, [c.copy(to_object=x, inlet_index=1)]))
                    for c in self.outlet_connections[0]:
                        connections.append((c, [c.copy(from_object=x, outlet_index=0)]))
                    return ({x}, connections)

            if self.type == "*":
                # self.args["k"] == 1.0 case handled above

                if self.args["k"] == 0.0:
                    # this object does nothing at all. Remove it.
                    return (set(), [])

                if self.args["k"] == -1.0:
                    x = HeavyIrObject("__neg~f")
                    return ({x}, self.get_connection_move_list(x))

            x = HeavyIrObject(ir_type)
            # add constant generator
            y = HeavyIrObject(
                "__var_k~f",
                args={"k": self.args[self.name_for_arg()]})
            connections = self.get_connection_move_list(x)
            connections.append((None, [Connection(y, 0, x, 1, "~f>")]))
            return ({x, y}, connections)

        elif self.has_inlet_connection_format("ii"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~i"))
            x = HeavyIrObject(ir_type)
            return ({x}, self.get_connection_move_list(x))

        elif self.has_inlet_connection_format("ic"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~i"))
            x = HeavyIrObject(ir_type)
            y = HeavyIrObject("__var~i", {"k": self.args[self.name_for_arg()]})
            z = HeavyIrObject("__varread~i", {"var_id": y.id})
            connections = [(None, [Connection(z, 0, x, 1, "~f>")])]
            for c in self.inlet_connections[0]:
                connections.append((c, [c.copy(to_object=x)]))
            for c in self.inlet_connections[1]:
                connections.append((c, [c.copy(to_object=y, inlet_index=0)]))
            for c in self.outlet_connections[0]:
                connections.append((c, [c.copy(from_object=x)]))
            return ({x, y, z}, connections)

        elif self.has_inlet_connection_format("i_"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~i"))
            x = HeavyIrObject(ir_type)
            # add constant generator
            y = HeavyIrObject(
                "__var_k~i",
                args={"k": self.args[self.name_for_arg()]})
            connections = [(None, [Connection(y, 0, x, 1, "~i>")])]
            for c in self.inlet_connections[0]:
                connections.append((c, [c.copy(to_object=x)]))
            for c in self.inlet_connections[1]:
                connections.append((c, [c.copy(to_object=y, inlet_index=0)]))
            for c in self.outlet_connections[0]:
                connections.append((c, [c.copy(from_object=x)]))
            return ({x, y}, connections)

        elif self.has_inlet_connection_format("cc"):
            ir_type = self.__HEAVY_DICT[self.type][0]
            # standardise the operation's constant argument name to "k"
            args = {"k": self.args[self.name_for_arg()]}
            x = HeavyIrObject(ir_type, args)
            return ({x}, self.get_connection_move_list(x))

        elif self.has_inlet_connection_format("c_"):
            # if the right inlet is empty, generate a constant variation of the object
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("_k"))
            # standardise the operation's constant argument name to "k"
            args = {"k": self.args[self.name_for_arg()]}
            x = HeavyIrObject(ir_type, args)
            return ({x}, self.get_connection_move_list(x))

        elif self.has_inlet_connection_format("cf"):
            ir_type = next(x for x in self.__HEAVY_DICT[self.type] if x.endswith("~f"))
            x = HeavyIrObject(ir_type)
            v = HeavyIrObject("__var~f")
            vr = HeavyIrObject("__varread~f", args={"var_id": v.id})

            obj_set = {x, v, vr}
            connections = [(None, [Connection(vr, 0, x, 0, "~f>")])]
            for c in self.inlet_connections[0]:
                connections.append((c, [c.copy(to_object=v, inlet_index=0)]))
            for c in self.inlet_connections[1]:
                connections.append((c, [c.copy(to_object=x, inlet_index=1)]))
            for c in self.outlet_connections[0]:
                connections.append((c, [c.copy(from_object=x, outlet_index=0)]))

            return (obj_set, connections)

        else:
            fmt = self._get_connection_format(self.inlet_connections)
            if "m" in fmt:
                self.add_error(
                    "A binary operator cannot have both a signal and control "
                    f"connection to the same inlet: {fmt}")
            else:
                self.add_error(f"Unknown inlet configuration: {fmt}")

        return None
