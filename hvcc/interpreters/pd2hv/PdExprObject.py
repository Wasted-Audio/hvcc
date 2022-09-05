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


class PdExprObject(PdObject):
    """
        Validate the expr object and any heavy restrictions, then
        convert it directly into a HeavyIR object.
    """

    def __init__(self, obj_type, obj_args=None, pos_x=0, pos_y=0):
        print("In Pd expr Obj")
        assert obj_type in ["expr", "expr~"]
        PdObject.__init__(self, obj_type, obj_args, pos_x, pos_y)

        # turn the arguments into a list of expressions, separated
        # by any semicolons encountered
        if len(self.obj_args) == 0:
            self.add_error("Empty expression")

        expressions = [
            e.strip() for e in
            " ".join(self.obj_args).split("\\;")
        ]
        if len(expressions) > 1:
            self.add_error("Heavy expr does NOT support multiple expressions")
        else:
            self.expressions = expressions

        # below is code to start sussing out the inlets, kicking to IR for now.
        # main reason to do it here is if there is an advantage to knowing the
        # number of inlets before we get to the IR level...
        # var_re = re.compile(r"\$[fis]\d+")
        # variables = set()
        # for e in self.expressions:
        #     variables |= set(re.findall(var_re, e))

        # var_nums = set([re.search(r"\d+", var)[0] for var in variables])
        # self.num_inlets = len(var_nums)

    def validate_configuration(self):
        # things that could be validated:
        # - inlet count/types match variables in the expression(s)
        pass

    def to_hv(self):
        return {
            "type": "__expr",
            "args": {
                "expressions": self.expressions
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
