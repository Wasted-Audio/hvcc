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

OWL_PARAMS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH',
              'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BH']

def parse_pd_owl_args(args):
    """Parses a list of puredata send or receive objects looking for @owl*
    annotations, parsing everything and throwing errors when syntax is not
    correct or values are of incorrect type"""

    attrdict = {}
    if '@owl' not in args:
        return attrdict

    # define default values
    attrdict["min"] = 0.0
    attrdict["max"] = 1.0
    attrdict["default"] = None

    for owl_param in ['@owl', '@owl_min', '@owl_max', '@owl_default']:
        if owl_param not in args:
            continue

        i = args.index(owl_param)

        if owl_param == '@owl':
            try:
                p = args[i+1]
            except IndexError:
                raise PdOwlException("%s annotation missing owl parameter value" % owl_param)

            if p not in OWL_PARAMS:
                raise PdOwlException("%s annotation parameter must be one of %s" % (owl_param, OWL_PARAMS))

            attrdict["owl"] = args[i+1]
            try:
                # require the presence of 3 parameters which can be converted to float
                _min, _max, _def = [float(x) for x in args[i+2:i+2+4]]
                attrdict["min"] = _min
                attrdict["max"] = _max
                attrdict["default"] = _def
            except (IndexError, ValueError) as e:
                # otherwise keep default
                pass

        elif owl_param in ['@owl_min', '@owl_max', '@owl_default']:
            # make sure that it is a float value
            try:
                attrdict[owl_param.split('@owl_')[1]] = float(args[i+1])
            except ValueError:
                raise PdOwlException("%s annotation value '%s' is not numeric" %
                                     (owl_param, args[i+1]))
            except IndexError:
                raise PdOwlException("%s annotation is missing its value")

    if attrdict["default"] is None:
        attrdict["default"] = (attrdict["max"] - attrdict["min"]) / 2.0

    return attrdict

