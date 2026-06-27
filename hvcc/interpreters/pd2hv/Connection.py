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

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .PdObject import PdObject

from hvcc.types.Heavy import HvConn, HvConnFrom, HvConnTo


class Connection:
    def __init__(
        self,
        from_obj: 'PdObject',
        outlet_index: int,
        to_obj: 'PdObject',
        inlet_index: int,
        conn_type: Optional[str]  # not actually Optional. This is due to the requirement in HeavyObject.
    ) -> None:
        assert from_obj is not None
        assert to_obj is not None
        assert conn_type is not None

        self.__from_obj = from_obj
        self.__to_obj = to_obj

        self.__hv_json = HvConn(
            type=conn_type,
            conn_from=HvConnFrom(id=from_obj.obj_id, outlet=outlet_index),
            conn_to=HvConnTo(id=to_obj.obj_id, inlet=inlet_index)
        )

    @property
    def from_obj(self) -> 'PdObject':
        return self.__from_obj

    @property
    def from_id(self) -> str:
        return self.__hv_json.conn_from.id

    @property
    def outlet_index(self) -> int:
        return self.__hv_json.conn_from.outlet

    @property
    def to_obj(self) -> 'PdObject':
        return self.__to_obj

    @property
    def to_id(self) -> str:
        return self.__hv_json.conn_to.id

    @property
    def inlet_index(self) -> int:
        return self.__hv_json.conn_to.inlet

    @property
    def conn_type(self) -> str:
        return self.__hv_json.type

    def to_hv(self) -> HvConn:
        return self.__hv_json

    def __repr__(self) -> str:
        return "{0}:{1} {4} {2}:{3}".format(
            self.from_id,
            self.outlet_index,
            self.to_id,
            self.inlet_index,
            self.conn_type)
