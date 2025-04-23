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

from arpeggio import ParserPython, StrMatch     # type: ignore
from arpeggio import ZeroOrMore                 # type: ignore
from arpeggio import RegExMatch as regex        # type: ignore


class SuppressStrMatch(StrMatch):
    suppress = True


hide = SuppressStrMatch


def expr():     return lor  # EOF                                                                   # noqa
def lor():      return land, ZeroOrMore("||", land)                                                 # noqa
def land():     return bor, ZeroOrMore("&&", bor)                                                   # noqa
def bor():      return xor, ZeroOrMore("|", xor)                                                    # noqa
def xor():      return band, ZeroOrMore("^", band)                                                  # noqa
def band():     return eq, ZeroOrMore("&", eq)                                                      # noqa
def eq():       return gtlt, ZeroOrMore(["==","!="], gtlt)                                          # noqa
def gtlt():     return shift, ZeroOrMore(["<","<=",">",">="], shift)                                # noqa
def shift():    return term, ZeroOrMore(["<<",">>"], term)                                          # noqa
def term():     return factor, ZeroOrMore(["+","-"], factor)    # RtoL                              # noqa
def factor():   return unary, ZeroOrMore(["*","/","%"], unary)                                      # noqa
def unary():    return [(["-","~","!"], unary), primary]        # RtoL                              # noqa
def primary():  return [number, var, func, group]                                                   # noqa
def number():   return [num_f, num_i]                                                               # noqa
def var():      return regex(r"\$[fisv]\d+")                                                        # noqa
def func():     return [                                                                            # noqa
                    (f_name, hide("("), expr, hide(")")),                                           # noqa
                    (f_name, hide("("), expr, hide(","), expr, hide(")")),                          # noqa
                    (f_name, hide("("), expr, hide(","), expr, hide(","), expr, hide(")"))          # noqa
                ]                                                                                   # noqa
def group():    return hide("("), expr, hide(")")                                                   # noqa
def num_f():    return regex(r"\d+\.\d+")  # prob need to cover exponential syntax, others?         # noqa
def num_i():    return regex(r"\d+")       # need to cover bin/octal/hex?                           # noqa
def f_name():   return [                                                                            # noqa
                    "abs", "acos", "acosh", "asin", "asinh", "atan", "atan2",                       # noqa
                    "cbrt", "ceil", "copysign", "cos", "cosh", "drem", "erf",                       # noqa
                    "erfc", "exp", "expm1", "fact", "finite", "float", "floor",                     # noqa
                    "fmod", "ldexp", "if", "imodf", "int", "isinf", "isnan",                        # noqa
                    "ln", "log", "log10", "log1p", "max", "min", "modf", "pow",                     # noqa
                    "rint", "sin", "sinh", "size", "sqrt", "sum", "Sum",                            # noqa
                    "tan", "tanh",                                                                  # noqa
                ]                                                                                   # noqa


expr_grammar = ParserPython(expr, reduce_tree=True)
