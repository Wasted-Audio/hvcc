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
    """ A Connection describes a connection between two objects.
    """

    def __init__(self, from_object, outlet_index, to_object, inlet_index, conn_type):
        self.from_object = from_object
        self.outlet_index = outlet_index
        self.to_object = to_object
        self.inlet_index = inlet_index
        self.type = conn_type

        # cache the hash of this object
        self.__hash = hash((
            self.from_object, self.outlet_index,
            self.to_object, self.inlet_index,
            self.type))

    def copy(self, from_object=None, outlet_index=None, to_object=None, inlet_index=None, type=None):
        """ Create a new connection based on the existing one, changing the given values.
        """
        return Connection(from_object=self.from_object if from_object is None else from_object,
                          outlet_index=self.outlet_index if outlet_index is None else outlet_index,
                          to_object=self.to_object if to_object is None else to_object,
                          inlet_index=self.inlet_index if inlet_index is None else inlet_index,
                          conn_type=self.type if type is None else type)

    @property
    def is_signal(self):
        return Connection.is_signal_type(self.type)

    @property
    def is_control(self):
        return self.type == "-->"

    @property
    def is_float_signal(self):
        return self.type == "~f>"

    @property
    def is_integer_signal(self):
        return self.type == "~i>"

    @property
    def is_mixed(self):
        return self.type == "-~>"

    @classmethod
    def is_signal_type(clazz, type):
        return type in ["~i>", "~f>"]

    def __eq__(self, other):
        return self.__hash == other.__hash__() if isinstance(other, Connection) else False

    def __hash__(self):
        return self.__hash

    def __repr__(self):
        return "[{0}:{1}] {4} [{2}:{3}]".format(
            self.from_object, self.outlet_index,
            self.to_object, self.inlet_index,
            self.type)
