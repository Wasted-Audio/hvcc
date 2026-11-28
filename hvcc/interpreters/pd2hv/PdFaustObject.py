# Copyright (C) 2026 Wasted Audio
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



from hvcc.types.Heavy import Heavy, HvPos

from .PdObject import PdObject


class PdFaustObject(PdObject):
    """
    Limitations (compared to faustgen2~):
    - requires patch name as argument
    """

    def __init__(
        self,
        obj_type: str,
        obj_args: list | None = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        assert obj_type == "faustgen2~"
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        if len(self.obj_args) == 0:
            self.add_error("No patch arguments")
        elif len(self.obj_args) > 1:
            self.add_error("Only a single patch argument is allowed")

        self.faustpatch = self.obj_args[0] if len(self.obj_args) > 0 else ""

    @staticmethod
    def _num_iolets(connections: dict) -> int:
        """ Returns the number of inlets/outlets needed to hold all connections.
        """
        if len(connections) == 0:
            return 0
        return max(int(index) for index in connections) + 1

    def get_inlet_connection_type(self, inlet_index: int) -> str | None:
        """ In faustgen2~ the first inlet is always for control messages.
            The rest are signal.
        """
        return "-->" if inlet_index == 0 else "~f>"

    def get_outlet_connection_type(self, outlet_index: int) -> str | None:
        """ In faustgen2~ the first outlet is always for control messages.
            The rest are signal.
        """
        return "-->" if outlet_index == 0 else "~f>"

    def validate_configuration(self) -> None:
        pass

    def to_hv(self) -> Heavy:
        return Heavy(
            type=f"__{self.obj_type}",
            args={
                "faustpatch": self.faustpatch,
                "num_inlets": self._num_iolets(self._inlet_connections),
                "num_outlets": self._num_iolets(self._outlet_connections)
            },
            properties=HvPos(x=self.pos_x, y=self.pos_y)
        )
