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

from typing import Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .HeavyObject import HeavyObject
    from .PdBinopObject import PdBinopObject
    from .PdLibSignalGraph import PdLibSignalGraph


class Connection:
    def __init__(
        self,
        from_obj: 'HeavyObject',
        outlet_index: int,
        to_obj: Union['PdBinopObject', 'PdLibSignalGraph', 'HeavyObject'],
        inlet_index: int,
        conn_type: str
    ) -> None:
        assert from_obj is not None
        assert to_obj is not None
        assert conn_type is not None

        self.__from_obj = from_obj
        self.__to_obj = to_obj
        self.__hv_json: Dict = {
            "from": {
                "id": from_obj.obj_id,
                "outlet": outlet_index
            },
            "to": {
                "id": to_obj.obj_id,
                "inlet": inlet_index
            },
            "type": conn_type
        }

    @property
    def from_obj(self) -> 'HeavyObject':
        return self.__from_obj

    @property
    def from_id(self) -> str:
        return self.__hv_json["from"]["id"]

    @property
    def outlet_index(self) -> int:
        return self.__hv_json["from"]["outlet"]

    @property
    def to_obj(self) -> Union['PdBinopObject', 'PdLibSignalGraph', 'HeavyObject']:
        return self.__to_obj

    @property
    def to_id(self) -> str:
        return self.__hv_json["to"]["id"]

    @property
    def inlet_index(self) -> int:
        return self.__hv_json["to"]["inlet"]

    @property
    def conn_type(self) -> str:
        return self.__hv_json["type"]

    def to_hv(self) -> Dict:
        return self.__hv_json

    def __repr__(self) -> str:
        return "{0}:{1} {4} {2}:{3}".format(
            self.from_id,
            self.outlet_index,
            self.to_id,
            self.inlet_index,
            self.conn_type)
