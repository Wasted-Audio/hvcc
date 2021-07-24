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

class Connection:
    def __init__(self, from_obj, outlet_index, to_obj, inlet_index, conn_type):
        assert from_obj is not None
        assert to_obj is not None
        assert conn_type is not None

        self.__from_obj = from_obj
        self.__to_obj = to_obj
        self.__hv_json = {
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
    def from_obj(self):
        return self.__from_obj

    @property
    def from_id(self):
        return self.__hv_json["from"]["id"]

    @property
    def outlet_index(self):
        return self.__hv_json["from"]["outlet"]

    @property
    def to_obj(self):
        return self.__to_obj

    @property
    def to_id(self):
        return self.__hv_json["to"]["id"]

    @property
    def inlet_index(self):
        return self.__hv_json["to"]["inlet"]

    @property
    def conn_type(self):
        return self.__hv_json["type"]

    def to_hv(self):
        return self.__hv_json

    def __repr__(self):
        return "{0}:{1} {4} {2}:{3}".format(
            self.__hv_json["from"]["id"],
            self.__hv_json["from"]["outlet"],
            self.__hv_json["to"]["id"],
            self.__hv_json["to"]["inlet"],
            self.__hv_json["type"])
