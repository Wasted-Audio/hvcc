from arpeggio import ParserPython, StrMatch
from arpeggio import ZeroOrMore
from arpeggio import RegExMatch as regex


class SuppressStrMatch(StrMatch):
    suppress = True

hide = SuppressStrMatch


def expr():     return lor  # EOF
def lor():      return land, ZeroOrMore("||", land)
def land():     return bor, ZeroOrMore("&&", bor)
def bor():      return xor, ZeroOrMore("|", xor)
def xor():      return band, ZeroOrMore("^", band)
def band():     return eq, ZeroOrMore("&", eq)
def eq():       return gtlt, ZeroOrMore(["==", "!="], gtlt)
def gtlt():     return shift, ZeroOrMore(["<", "<=", ">", ">="], shift)
def shift():    return term, ZeroOrMore(["<<", ">>"], term)
def term():     return factor, ZeroOrMore(["+", "-"], factor)    # RtoL
def factor():   return unary, ZeroOrMore(["*", "/", "%"], unary)
def unary():    return [(["-", "~", "!"], unary), primary]        # RtoL
def primary():  return [number, var, func, group]
def number():   return [num_f, num_i]
def var():      return regex(r"\$[fisv]\d+")
def func():     return [
                    (f_name, hide("("), expr, hide(")")),
                    (f_name, hide("("), expr, hide(","), expr, hide(")")),
                    (f_name, hide("("), expr, hide(","), expr, hide(","), expr, hide(")"))
                ]
def group():    return hide("("), expr, hide(")")
def num_f():    return regex(r"\d+\.\d+")  # prob need to cover exponential syntax, others?
def num_i():    return regex(r"\d+")       # need to cover bin/octal/hex?
def f_name():   return [
                    "abs", "acos", "acosh", "asin", "asinh", "atan", "atan2",
                    "cbrt", "ceil", "copysign", "cos", "cosh", "drem", "erf",
                    "erfc", "exp", "expm1", "fact", "finite", "float", "floor",
                    "fmod", "ldexp", "if", "imodf", "int", "isinf", "isnan",
                    "ln", "log", "log10", "log1p", "max", "min", "modf", "pow",
                    "rint", "sin", "sinh", "size", "sqrt", "sum", "Sum",
                    "tan", "tanh",
                ]

expr_grammar = ParserPython(expr, reduce_tree=True)
