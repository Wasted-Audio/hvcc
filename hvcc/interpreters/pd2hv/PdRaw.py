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

from typing import List, Dict


class PdRawException(Exception):
    pass


def replace_owl(args: List) -> List:
    new_args = []
    for arg in args:
        new_arg = arg.replace('owl', 'raw')
        new_args.append(new_arg)
    return new_args


def parse_pd_raw_args(args: List) -> Dict:
    """Parses a list of puredata send or receive objects looking for @raw and legacy @owl*
    annotations, parsing everything and throwing errors when syntax is not
    correct or values are of incorrect type"""

    attrdict = {}

    # define default values
    attrdict["min"] = 0.0
    attrdict["max"] = 1.0

    args = replace_owl(args)  # TODO(dromer): deprecate @owl on next stable release

    for raw_param in {'@raw', '@raw_min', '@raw_max', '@raw_default', '@raw_param'}:
        if raw_param not in args:
            continue

        i = args.index(raw_param)

        if raw_param in {'@raw', '@raw_param'}:
            try:
                attrdict["raw"] = args[i + 1]
            except IndexError:
                raise PdRawException(f"{raw_param} annotation missing assigned parameter")
            if raw_param == '@raw':
                try:
                    # expect the presence of up to 3 parameters which can be converted to float
                    attrdict["min"] = float(args[i + 2])
                    attrdict["max"] = float(args[i + 3])
                    attrdict["default"] = float(args[i + 4])
                except (IndexError, ValueError):
                    # otherwise keep default
                    pass
        elif raw_param in {'@raw_min', '@raw_max', '@raw_default'}:
            # make sure that it is a float value
            try:
                attrdict[raw_param.split('@raw_')[1]] = float(args[i + 1])
            except ValueError:
                raise PdRawException(f"{raw_param} annotation value '{args[i + 1]}' is not numeric")
            except IndexError:
                raise PdRawException(f"{raw_param} annotation is missing its value")

    if attrdict.get("default") is None:
        attrdict["default"] = (attrdict["max"] - attrdict["min"]) / 2.0

    return attrdict
