# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023-2024 Wasted Audio
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

from collections import defaultdict
import random
import string

from typing import Optional, List, Dict, TYPE_CHECKING

from .Connection import Connection
from .NotificationEnum import NotificationEnum

from hvcc.types.compiler import CompilerMsg, CompilerNotif

if TYPE_CHECKING:
    from .PdGraph import PdGraph


class PdObject:

    __RANDOM = random.Random()
    __ID_CHARS = string.ascii_letters + string.digits

    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        self.obj_type = obj_type
        # all arguments should be resolved when passed to a PdObject
        self.obj_args = obj_args or []
        self.obj_id = "{0}_{1}".format(
            obj_type,
            "".join(self.__RANDOM.choice(self.__ID_CHARS) for _ in range(8)))
        self.pos_x = pos_x
        self.pos_y = pos_y

        # this is set when the object is added to a graph
        self.parent_graph: Optional['PdGraph'] = None

        self._inlet_connections: Dict = defaultdict(list)
        self._outlet_connections: Dict = defaultdict(list)

        self._warnings: List[CompilerMsg] = []
        self._errors: List[CompilerMsg] = []

    def add_warning(self, warning: str, enum: NotificationEnum = NotificationEnum.WARNING_GENERIC) -> None:
        """ Add a warning regarding this object.
        """
        self._warnings.append(CompilerMsg(enum=enum, message=warning))

    def add_error(self, error: str, enum: NotificationEnum = NotificationEnum.ERROR_GENERIC) -> None:
        """ Add an error regarding this object.
        """
        self._errors.append(CompilerMsg(enum=enum, message=error))

    def get_notices(self) -> CompilerNotif:
        """ Returns a dictionary of all warnings and errors at this object.
        """
        # TODO(mhroth): we might want to consider moving to a more expressive format.
        # {
        #     "objectType": "trigger",
        #     "objectString": "t l l",
        #     "graphs": ["_main", "hello"],
        #     "rawText": "Heavy only supports arguments 'a', 'f', 's', and 'b'.",
        #     "humanText": "[t l l] in "_main/osc~" @ (x:452, y:273): Heavy only supports
        # arguments 'a', 'f', 's', and 'b'.",
        #     "position": {
        #         "x": 452,
        #         "y": 273
        #     }
        # }
        """
        {
            "warnings": [{
                "enum": 1000,
                "message": "this is a warning"
            }],
            "errors": [{
                "enum": 2000,
                "message": "this is an error"
            }]
        }
        """

        return CompilerNotif(
            has_error=len(self._errors) > 0,
            warnings=[
                CompilerMsg(enum=n.enum, message="{0} in \"{1}\" @ (x:{2}, y:{3}): {4}".format(
                    self, "/".join(self.get_graph_heirarchy()), self.pos_x, self.pos_y, n.message
                )) for n in self._warnings
            ],
            errors=[
                CompilerMsg(enum=n.enum, message="{0} in \"{1}\" @ (x:{2}, y:{3}): {4}".format(
                    self, "/".join(self.get_graph_heirarchy()), self.pos_x, self.pos_y, n.message
                )) for n in self._errors
            ]
        )

    def get_inlet_connections(self) -> Dict:
        return self._inlet_connections

    def get_inlet_connection_type(self, inlet_index: int) -> Optional[str]:
        """ Returns the inlet connection type of this Pd object.
            For the sake of convenience, the connection type is reported in
            Heavy's format.
        """
        return "~f>" if self.obj_type.endswith("~") else "-->"

    def get_outlet_connection_type(self, outlet_index: int) -> Optional[str]:
        """ Returns the outlet connection type of this Pd object.
            For the sake of convenience, the connection type is reported in
            Heavy's format.
        """
        return "~f>" if self.obj_type.endswith("~") else "-->"

    def add_connection(self, c: Connection) -> None:
        """ Adds a connection, either inlet or outlet, to this object.
        """
        if c.from_id == self.obj_id:
            self._outlet_connections[str(c.outlet_index)].append(c)
        elif c.to_id == self.obj_id:
            self._inlet_connections[str(c.inlet_index)].append(c)
        else:
            raise Exception("Adding a connection to the wrong object!")

    def remove_connection(self, c: Connection) -> None:
        """ Remove a connection to this object.
        """
        if c.to_obj is self:
            self._inlet_connections[str(c.inlet_index)].remove(c)
        elif c.from_obj is self:
            self._outlet_connections[str(c.outlet_index)].remove(c)
        else:
            raise Exception(f"Connection {c} does not connect to this object {self}.")

    def get_graph_heirarchy(self) -> List:
        """ Returns an indication of the graph "path" of this object.
        It only includes unique graphs (not subpatches) E.g. _main/tabosc4~
        The check for None is in case the object is somehow not yet attached.
        """
        return self.parent_graph.get_graph_heirarchy() \
            if self.parent_graph is not None else ["unattached"]

    def validate_configuration(self) -> None:
        """ Called when all graphs are finished parsing, from the root.
            Gives each object the chance to validate it's configuration,
            including connections.
            In general this function does nothing, though it may add warnings and
            errors.
            Note that object validation occurs when the entire patch is finished
            parsing and before it is returned to the user. The program may assume
            that all parameters and variables have been set.
        """
        pass

    @classmethod
    def get_supported_objects(cls) -> set:
        """ Returns a list of Pd objects that this class can parse.
        """
        raise NotImplementedError()

    def to_hv(self) -> Dict:
        """ Returns the HeavyLang JSON representation of this object.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        if len(self.obj_args) == 0:
            return f"[{self.obj_type}]"
        else:
            return f"[{self.obj_type} {' '.join([str(o) for o in self.obj_args])}]"
