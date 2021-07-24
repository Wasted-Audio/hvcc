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

from .NotificationEnum import NotificationEnum
from .PdObject import PdObject


class PdTableObject(PdObject):

    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type in ["table"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

        self.__table_name = ""
        self.__size = 0
        self.__extern = False

        try:
            self.__table_name = self.obj_args[0]
        except Exception:
            self.add_error(
                "Missing \"name\" argument for table",
                NotificationEnum.ERROR_MISSING_REQUIRED_ARGUMENT)

        try:
            # optional arguments
            try:
                self.__size = int(self.obj_args[1])
                self.__extern = (self.obj_args[2] == "@hv_table")
            except Exception:
                pass
        except Exception:
            pass

    def to_hv(self):
        return {
            "type": "table",
            "args": {
                "name": self.__table_name,
                "size": self.__size,
                "values": [],
                "extern": self.__extern
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            },
            "annotations": {
                "scope": "public"
            }
        }
