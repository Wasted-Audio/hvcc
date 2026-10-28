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

from arpeggio import (  # type: ignore
    ParserPython,
    StrMatch,
    ZeroOrMore,  # type: ignore
)
from arpeggio import RegExMatch as regex  # type: ignore


class SuppressStrMatch(StrMatch):
    suppress = True


hide = SuppressStrMatch


def expr():     return none  # EOF
def none():     return lor, ZeroOrMore(" ", lor)  # needed for logical `or`: `||`
def lor():      return land, ZeroOrMore("||", land)
def land():     return bor, ZeroOrMore("&&", bor)
def bor():      return xor, ZeroOrMore("|", xor)
def xor():      return band, ZeroOrMore("^", band)
def band():     return eq, ZeroOrMore("&", eq)
def eq():       return gtlte, ZeroOrMore(["==","!="], gtlte)
def gtlte():    return gtlt, ZeroOrMore(["<=",">="], gtlt)
def gtlt():     return shift, ZeroOrMore(["<",">"], shift)
def shift():    return term, ZeroOrMore(["<<",">>"], term)
def term():     return factor, ZeroOrMore(["+","-"], factor)    # RtoL
def factor():   return unary, ZeroOrMore(["*","/","%"], unary)
def unary():    return [(["-","~","!"], unary), primary]        # RtoL
def primary():  return [number, var, func, group]
def number():   return [num_f, num_i]
def var():      return regex(r"\$[fisv]\d+")
def func():     return [
                    (f_name, hide("("), expr, hide(")")),
                    (f_name, hide("("), expr, hide(r"\,"), expr, hide(")")),
                    (f_name, hide("("), expr, hide(r"\,"), expr, hide(r"\,"), expr, hide(")"))
                ]
def group():    return hide("("), expr, hide(")")
def num_f():    return regex(r"\d+\.\d+")  # prob need to cover exponential syntax, others?
def num_i():    return regex(r"\d+")       # need to cover bin/octal/hex?
def f_name():   return [
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
                    regex(r"\bfact(?=\()"),
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
                    regex(r"\btrunc(?=\()"),
                ]


expr_grammar = ParserPython(expr, reduce_tree=True)
