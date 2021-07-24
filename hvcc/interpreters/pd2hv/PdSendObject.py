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
from .pdowl import parse_pd_owl_args, PdOwlException


class PdSendObject(PdObject):
    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        assert obj_type in ["s", "send", "s~", "send~", "throw~"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

        self.__send_name = ""
        self.__extern_type = None
        self.__attributes = {}

        try:
            # send objects don't necessarily need to have a name
            self.__send_name = self.obj_args[0]

            # only extern control rate sends
            if obj_type in ["s", "send"]:
                if self.obj_args[1] == "@hv_param":
                    self.__extern_type = "param"
                elif self.obj_args[1] == "@hv_event":
                    self.__extern_type = "event"
        except Exception:
            pass

        if '@owl' in self.obj_args or '@owl_param' in self.obj_args:
            try:
                pd_owl_args = parse_pd_owl_args(self.obj_args)
                self.__attributes.update(pd_owl_args)
                self.__extern_type = "param"  # make sure output code is generated
            except PdOwlException as e:
                self.add_error(e)

    def validate_configuration(self):
        if len(self.obj_args) == 0:
            self.add_warning(
                "No name was given to this {0} object. "
                "It should have a name to reduce the risk of errors.".format(self.obj_type),
                NotificationEnum.WARNING_USELESS_OBJECT)
        if len(self._inlet_connections.get("0", [])) == 0:
            self.add_warning(
                "This object has no inlet connections. "
                "It does nothing and will be removed.",
                NotificationEnum.WARNING_USELESS_OBJECT)
        if self.obj_type in ["s", "send"] and len(self._inlet_connections.get("1", [])) > 0:
            self.add_error(
                "Connections to the right inlet of a send object "
                "are not supported. A name should be given.",
                NotificationEnum.ERROR_MISSING_REQUIRED_ARGUMENT)

    def to_hv(self):
        # note: control rate send/receive objects should not modify their name argument
        names = {
            "s": "",
            "send": "",
            "s~": "sndrcv_sig_",
            "send~": "sndrcv_sig_",
            "throw~": "thrwctch_sig_"
        }

        return {
            "type": "send",
            "args": {
                "name": names[self.obj_type] + self.__send_name,
                "extern": self.__extern_type,
                "attributes": self.__attributes,
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            },
            "annotations": {
                "scope": "public"
            }
        }
