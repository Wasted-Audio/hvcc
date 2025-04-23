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

from typing import Union

from arpeggio import ParsingExpression as ParseTreeNode, Terminal  # type: ignore
from .expr_arpeggio_grammar import expr_grammar

ParseExpr = Union[ParseTreeNode, Terminal]


class ExprNode:
    def __init__(
        self,
        node_type: str,
        value: str,
        nodes: list = []
    ) -> None:
        self.type = node_type
        self.value = value
        self.nodes: list[ExprNode] = nodes

    def __str__(self, depth: int = 0) -> str:
        this = f"{'  '*depth}{self.type}:{self.value}\n"
        for node in self.nodes:
            this += node.__str__(depth + 1)
        return this


class ExprArpeggioParser():
    """
    These two methods are the "public" API
    """
    @classmethod
    def parse(cls, expr) -> ParseExpr:
        """Parse the input expression and return a parse tree"""
        return expr_grammar.parse(expr)

    @classmethod
    def parse_to_ast(cls, expr: str) -> ExprNode:
        """Parse the input expression and return an AST"""
        return cls.to_expr_tree(cls.parse(expr))

    """
    Helper methods below
    """
    @classmethod
    def to_expr_tree(cls, expr: ParseExpr) -> ExprNode:
        if expr.rule_name == "num_i":
            return ExprNode("num_i", expr.value)
        elif expr.rule_name == "num_f":
            return ExprNode("num_f", expr.value)
        elif expr.rule_name == "var":
            return ExprNode("var", expr.value)
        elif expr.rule_name == "func":
            return ExprNode("func", expr[0].value, [cls.to_expr_tree(p) for p in expr[1:]])
        elif expr.rule_name == "unary":
            return ExprNode("unary", expr[0].value, [cls.to_expr_tree(expr[1])])
        elif expr.rule_name == "term":
            # this is RtoL associativity
            val = None
            tmp = None
            subtree = None
            for i in range(len(expr)):
                if i % 2 == 0:
                    val = cls.to_expr_tree(expr[i])
                else:
                    foo = ExprNode("binary", str(expr[i]), [val])
                    if subtree is None:
                        subtree = foo
                    else:
                        assert tmp
                        tmp.nodes.append(foo)
                    tmp = foo
            assert val and tmp and subtree
            tmp.nodes.append(val)
            return subtree

        elif expr.rule_name in (
            "lor", "land", "bor", "xor", "band", "eq", "gtlt", "shift", "factor"
        ):
            # this is LtoR associativity
            subtree = None
            for i in range(len(expr)):
                if i % 2 == 0:
                    if subtree is None:
                        subtree = cls.to_expr_tree(expr[i])
                    else:
                        subtree.nodes.append(cls.to_expr_tree(expr[i]))
                else:
                    subtree = ExprNode("binary", str(expr[i]), [subtree])
            assert subtree
            return subtree

        else:
            raise ValueError(f"Unknown rule {expr.rule_name}")
