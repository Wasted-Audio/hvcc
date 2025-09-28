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


def expr():     return none  # EOF                                                                  # noqa
def none():     return lor, ZeroOrMore(" ", lor)  # needed for logical `or`: `||`                   # noqa
def lor():      return land, ZeroOrMore("||", land)                                                 # noqa
def land():     return bor, ZeroOrMore("&&", bor)                                                   # noqa
def bor():      return xor, ZeroOrMore("|", xor)                                                    # noqa
def xor():      return band, ZeroOrMore("^", band)                                                  # noqa
def band():     return eq, ZeroOrMore("&", eq)                                                      # noqa
def eq():       return gtlte, ZeroOrMore(["==","!="], gtlte)                                        # noqa
def gtlte():    return gtlt, ZeroOrMore(["<=",">="], gtlt)                                          # noqa
def gtlt():     return shift, ZeroOrMore(["<",">"], shift)                                          # noqa
def shift():    return term, ZeroOrMore(["<<",">>"], term)                                          # noqa
def term():     return factor, ZeroOrMore(["+","-"], factor)    # RtoL                              # noqa
def factor():   return unary, ZeroOrMore(["*","/","%"], unary)                                      # noqa
def unary():    return [(["-","~","!"], unary), primary]        # RtoL                              # noqa
def primary():  return [number, var, func, group]                                                   # noqa
def number():   return [num_f, num_i]                                                               # noqa
def var():      return regex(r"\$[fisv]\d+")                                                        # noqa
def func():     return [                                                                            # noqa
                    (f_name, hide("("), expr, hide(")")),                                           # noqa
                    (f_name, hide("("), expr, hide(r"\,"), expr, hide(")")),                        # noqa
                    (f_name, hide("("), expr, hide(r"\,"), expr, hide(r"\,"), expr, hide(")"))      # noqa
                ]                                                                                   # noqa
def group():    return hide("("), expr, hide(")")                                                   # noqa
def num_f():    return regex(r"\d+\.\d+")  # prob need to cover exponential syntax, others?         # noqa
def num_i():    return regex(r"\d+")       # need to cover bin/octal/hex?                           # noqa
def f_name():   return [                                                                            # noqa
                    regex(r"\babs(?=\()"),
                    regex(r"\bacos(?=\()"),
                    regex(r"\bacosh(?=\()"),
                    regex(r"\basin(?=\()"),
                    regex(r"\basinh(?=\()"),
                    regex(r"\batan(?=\()"),
                    regex(r"\batan2(?=\()"),
                    regex(r"\batanh(?=\()"),
                    regex(r"\bcbrt(?=\()"),
                    regex(r"\bceil(?=\()"),
                    regex(r"\bcopysign(?=\()"),
                    regex(r"\bcos(?=\()"),
                    regex(r"\bcosh(?=\()"),
                    regex(r"\bdrem(?=\()"),
                    regex(r"\berf(?=\()"),
                    regex(r"\berfc(?=\()"),
                    regex(r"\bexp(?=\()"),
                    regex(r"\bexpm1(?=\()"),
                    # regex(r"\bfact(?=\()"),
                    regex(r"\bfinite(?=\()"),
                    regex(r"\bfloat(?=\()"),
                    regex(r"\bfloor(?=\()"),
                    regex(r"\bfmod(?=\()"),
                    regex(r"\bif(?=\()"),
                    regex(r"\bimodf(?=\()"),
                    regex(r"\bint(?=\()"),
                    regex(r"\bisinf(?=\()"),
                    regex(r"\bisnan(?=\()"),
                    regex(r"\bldexp(?=\()"),
                    regex(r"\bln(?=\()"),
                    regex(r"\blog(?=\()"),
                    regex(r"\blog10(?=\()"),
                    regex(r"\blog1p(?=\()"),
                    regex(r"\bmax(?=\()"),
                    regex(r"\bmin(?=\()"),
                    regex(r"\bmodf(?=\()"),
                    regex(r"\bpow(?=\()"),
                    regex(r"\bremainder(?=\()"),
                    regex(r"\brint(?=\()"),
                    regex(r"\bround(?=\()"),
                    regex(r"\bnearbyint(?=\()"),
                    regex(r"\bsin(?=\()"),
                    regex(r"\bsinh(?=\()"),
                    # regex(r"\bsize(?=\()"),
                    regex(r"\bsqrt(?=\()"),
                    # regex(r"\bsum(?=\()"),
                    # regex(r"\bSum(?=\()"),
                    regex(r"\btan(?=\()"),
                    regex(r"\btanh(?=\()"),
                ]


expr_grammar = ParserPython(expr, reduce_tree=True)
