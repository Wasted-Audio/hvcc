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

from .PdObject import PdObject


class HvSwitchcase(PdObject):
    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type == "__switchcase"
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

        # ensure that correct case hashes are generated
        for i, a in enumerate(self.obj_args):
            try:
                self.obj_args[i] = float(a)
            except Exception:
                pass

    def get_outlet_connection_type(self, outlet_index):
        return "-->"

    def to_hv(self):
        return {
            "type": "__switchcase",
            "args": {
                "cases": self.obj_args
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
