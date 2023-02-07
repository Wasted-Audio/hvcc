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

from typing import Optional, Dict

from .HeavyLangObject import HeavyLangObject
from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph


class HLangUnop(HeavyLangObject):

    __HEAVY_DICT = {
        "log": ["__log"],
        "log10": ["__log10"],
        "log2": ["__log2", "__log2~f"],
        "cos": ["__cos", "__cos~f"],
        "acos": ["__acos", "__acos~f"],
        "cosh": ["__cosh", "__cosh~f"],
        "acosh": ["__acosh", "__acosh~f"],
        "sin": ["__sin", "__sin~f"],
        "asin": ["__asin", "__asin~f"],
        "sinh": ["__sinh", "__sinh~f"],
        "asinh": ["__asinh", "__asin~f"],
        "tan": ["__tan", "__tan~f"],
        "atan": ["__atan", "__atan~f"],
        "tanh": ["__tanh", "__tanh~f"],
        "atanh": ["__atanh", "__atanh~f"],
        "exp": ["__exp", "__exp~f"],
        "sqrt": ["__sqrt", "__sqrt~f"],
        "abs": ["__abs", "__abs~f", "__abs~i"],
        "floor": ["__floor", "__floor~f"],
        "ceil": ["__ceil", "__ceil~f"],
        "cast_fi": ["__cast~fi"],
        "cast_if": ["__cast~if"]
    }

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: 'HeavyGraph',
        annotations: Optional[Dict] = None
    ) -> None:
        assert self.handles_type(obj_type)
        super().__init__(obj_type, args, graph,
                         num_inlets=1,
                         num_outlets=1,
                         annotations=annotations)

    @classmethod
    def handles_type(cls, obj_type: str) -> bool:
        """ Returns True if this class handles the given object type. False otherwise.
        """
        return obj_type in HLangUnop.__HEAVY_DICT

    def reduce(self) -> Optional[tuple]:
        if len(self.inlet_connections[0]) == 0:
            self.add_error("Unary operator objects must have an input.")

        # TODO(mhroth): there is no general consensus on how to handle incoming
        # and outgoing connections of different types, given the local let-type
        # definitions.

        if self.type == "cast_fi":
            x = HeavyIrObject(self.type)  # is this correct? no idea what x is otherwise
            return ({HeavyIrObject("__cast~fi", {})}, self.get_connection_move_list(x))
        elif self.type == "cast_if":
            x = HeavyIrObject(self.type)  # is this correct? no idea what x is otherwise
            return ({HeavyIrObject("__cast~if", {})}, self.get_connection_move_list(x))
        elif self.has_inlet_connection_format("f"):
            ir_type = f"__{self.type}~f"
            assert ir_type in HLangUnop.__HEAVY_DICT[self.type]
            x = HeavyIrObject(ir_type)
            return ({x}, self.get_connection_move_list(x, "~f>"))
        elif self.has_inlet_connection_format("i"):
            ir_type = f"__{self.type}~i"
            assert ir_type in HLangUnop.__HEAVY_DICT[self.type]
            x = HeavyIrObject(ir_type)
            return ({x}, self.get_connection_move_list(x, "~i>"))
        elif self.has_inlet_connection_format("c"):
            ir_type = f"__{self.type}"
            assert ir_type in HLangUnop.__HEAVY_DICT[self.type]
            x = HeavyIrObject(ir_type)
            return ({x}, self.get_connection_move_list(x, "-->"))
        else:
            self.add_error("Unknown inlet configuration.")
            return None
