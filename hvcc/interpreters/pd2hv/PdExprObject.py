# Copyright (C) 2022-2025 Daniel Billotte, Wasted Audio
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
import re

from .PdObject import PdObject

from typing import Optional, List


class PdExprObject(PdObject):
    """
    Limitations (compared to vanilla pd):
    - only supports a single expression
    - pd docs say expr support 9 variables, experiments show that
      it supports at least 20... This version currently supports up
      to 10 variables as defined in HvControlExpr.h
    - I don't know what pd-expr does with strings, haven't experimented
      and haven't given it any thought yet here

    Bugs:
    - skipped variables cause crash, like "$f1 + $f3"
    """

    def __init__(
        self,
        obj_type: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0
    ) -> None:
        """
            Validate the expr object and any heavy restrictions, then
            convert it directly into a HeavyIR object.
        """
        # self.obj_type = obj_type

        print("In Pd expr Obj")
        assert obj_type in ["expr", "expr~"]
        super().__init__(obj_type, obj_args, pos_x, pos_y)

        # turn the arguments into a list of expressions, but only one for now
        if len(self.obj_args) == 0:
            self.add_error("Empty expression")

        expressions = [e.strip() for e in " ".join(self.obj_args).split("\\;")]
        if len(expressions) > 1:
            self.add_error("Heavy expr does not support multiple expressions")
        else:
            self.expressions = expressions

        # count the number of inlets
        var_nums = {
            int(var[2:]) for var in
            # this should be checked separately for control vs. signal instances
            # fis for control, v for signal
            re.findall(r"\$[fisv]\d+", self.expressions[0])
        }
        self.num_inlets = max(var_nums) if len(var_nums) > 0 else 1
        if self.num_inlets > 10:
            self.add_error("Heavy expr supports upto 10 variables")

    def validate_configuration(self):
        # things that could be validated:
        # - inlet count/types match variables in the expression(s)
        pass

    def to_hv(self):
        return {
            "type": f"__{self.obj_type}",
            "args": {
                "expressions": self.expressions,
                "num_inlets": self.num_inlets
            },
            "properties": {
                "x": self.pos_x,
                "y": self.pos_y
            }
        }
