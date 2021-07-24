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


class PdAudioIoObject(PdObject):
    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type in ["adc~", "dac~"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

    def validate_configuration(self):
        # ensure that only signal connections are made to the dac
        for i, connections in self._inlet_connections.items():
            if any(c.conn_type == "-->" for c in connections):
                self.add_error(
                    "{0} does not support control connections (inlet {1}). They should be removed.".format(
                        self.obj_type,
                        i),
                    NotificationEnum.ERROR_UNSUPPORTED_CONNECTION)

    def to_hv(self):
        return {
            "type": self.obj_type.strip("~"),
            "args": {
                "channels": [1, 2] if len(self.obj_args) == 0 else [int(a) for a in self.obj_args]
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
