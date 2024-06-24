from .expr_arpeggio_grammar import expr_grammar


class ExprArpeggioParser():
    """
    These two methods are the "public" API
    """
    @classmethod
    def parse(cls, expr):
        """Parse the input expression and return a parse tree"""
        return expr_grammar.parse(expr)

    @classmethod
    def parse_to_ast(cls, expr):
        """Parse the input expression and return an AST"""
        return cls.to_expr_tree(cls.parse(expr))

    """
    Helper methods below
    """
    @classmethod
    def to_expr_tree(cls, expr):
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
                    if not subtree:
                        subtree = foo
                    else:
                        tmp.nodes.append(foo)
                    tmp = foo
            tmp.nodes.append(val)
            return subtree

        elif expr.rule_name in (
            "lor", "land", "bor", "xor", "band", "eq", "gtlt", "shift", "factor"
        ):
            # this is LtoR associativity
            subtree = None
            for i in range(len(expr)):
                if i % 2 == 0:
                    if not subtree:
                        subtree = cls.to_expr_tree(expr[i])
                    else:
                        subtree.nodes.append(cls.to_expr_tree(expr[i]))
                else:
                    subtree = ExprNode("binary", str(expr[i]), [subtree])
            return subtree


class ExprNode:
    def __init__(self, node_type, value, nodes=[]):
        self.type = node_type
        self.value = value
        self.nodes = nodes

    def __str__(self, depth=0):
        this = f"{'  '*depth}{self.type}:{self.value}\n"
        for node in self.nodes:
            this += node.__str__(depth + 1)
        return this
