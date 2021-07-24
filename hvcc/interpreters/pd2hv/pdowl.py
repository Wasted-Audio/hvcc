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

class PdOwlException(Exception):
    pass


def parse_pd_owl_args(args):
    """Parses a list of puredata send or receive objects looking for @owl*
    annotations, parsing everything and throwing errors when syntax is not
    correct or values are of incorrect type"""

    attrdict = {}

    # define default values
    attrdict["min"] = 0.0
    attrdict["max"] = 1.0
    attrdict["default"] = None

    for owl_param in ['@owl', '@owl_min', '@owl_max', '@owl_default', '@owl_param']:
        if owl_param not in args:
            continue

        i = args.index(owl_param)

        if owl_param in ['@owl', '@owl_param']:
            try:
                attrdict["owl"] = args[i + 1]
            except IndexError:
                raise PdOwlException(f"{owl_param} annotation missing assigned parameter")
            if owl_param == '@owl':
                try:
                    # expect the presence of up to 3 parameters which can be converted to float
                    attrdict["min"] = float(args[i + 2])
                    attrdict["max"] = float(args[i + 3])
                    attrdict["default"] = float(args[i + 4])
                except (IndexError, ValueError):
                    # otherwise keep default
                    pass
        elif owl_param in ['@owl_min', '@owl_max', '@owl_default']:
            # make sure that it is a float value
            try:
                attrdict[owl_param.split('@owl_')[1]] = float(args[i + 1])
            except ValueError:
                raise PdOwlException(f"{owl_param} annotation value '{args[i + 1]}' is not numeric")
            except IndexError:
                raise PdOwlException(f"{owl_param} annotation is missing its value")

    if attrdict["default"] is None:
        attrdict["default"] = (attrdict["max"] - attrdict["min"]) / 2.0

    return attrdict
