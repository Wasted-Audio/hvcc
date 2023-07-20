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

from typing import Dict, List

from .HeavyObject import HeavyObject


class SignalLorenz(HeavyObject):

    c_struct = "SignalLorenz"
    preamble = "sLorenz"

    @classmethod
    def get_C_header_set(cls) -> set:
        return {"HvSignalLorenz.h"}

    @classmethod
    def get_C_file_set(cls) -> set:
        return {"HvSignalLorenz.h", "HvSignalLorenz.c", "HvMath.h"}

    @classmethod
    def get_C_init(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            "sLorenz_init(&sLorenz_{0}, {1}f, {2}f, {3}f);".format(
                obj_id,
                float(args["x"]),
                float(args["y"]),
                float(args["z"]))
        ]

    @classmethod
    def get_C_free(cls, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return []  # nothing to free

    @classmethod
    def get_C_onMessage(cls, obj_type: str, obj_id: int, inlet_index: int, args: Dict) -> List[str]:
        return [
            "sLorenz_onMessage(_c, &Context(_c)->sLorenz_{0}, {1}, m);".format(
                obj_id,
                inlet_index)
        ]

    @classmethod
    def get_C_process(cls, process_dict: Dict, obj_type: str, obj_id: int, args: Dict) -> List[str]:
        return [
            "__hv_lorenz_f(&sLorenz_{0}, {1}, {2});".format(
                process_dict["id"],
                ", ".join(["VIf({0})".format(cls._c_buffer(b)) for b in process_dict["inputBuffers"]]),
                ", ".join(["VOf({0})".format(cls._c_buffer(b)) for b in process_dict["outputBuffers"]])
            )
        ]
