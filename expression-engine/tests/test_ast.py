from src.ast import (
    ConstantNode, VariableNode, BinaryOpNode, UnaryOpNode, EquationNode,
    ToStringVisitor,
)


class TestToStringVisitor:
    def setup_method(self):
        self.visitor = ToStringVisitor()

    def test_constant(self):
        assert self.visitor.visit(ConstantNode(5)) == "5"

    def test_variable(self):
        assert self.visitor.visit(VariableNode("x")) == "x"

    def test_addition(self):
        ast = BinaryOpNode("+", ConstantNode(2), VariableNode("x"))
        assert self.visitor.visit(ast) == "2 + x"

    def test_multiplication(self):
        ast = BinaryOpNode("*", ConstantNode(2), VariableNode("x"))
        assert self.visitor.visit(ast) == "2 * x"

    def test_equation(self):
        left = BinaryOpNode("+", BinaryOpNode("*", ConstantNode(2), VariableNode("x")), ConstantNode(5))
        ast = EquationNode(left, ConstantNode(17))
        result = self.visitor.visit(ast)
        assert "=" in result
        assert "2 * x + 5" in result or "5 + 2 * x" in result

    def test_parentheses_needed(self):
        # 2 * (x + 1)
        inner = BinaryOpNode("+", VariableNode("x"), ConstantNode(1))
        ast = BinaryOpNode("*", ConstantNode(2), inner)
        result = self.visitor.visit(ast)
        assert result == "2 * (x + 1)"

    def test_parentheses_not_needed(self):
        # 2 + x (no parens needed)
        ast = BinaryOpNode("+", ConstantNode(2), VariableNode("x"))
        result = self.visitor.visit(ast)
        assert result == "2 + x"

    def test_division(self):
        ast = BinaryOpNode("/", VariableNode("x"), ConstantNode(3))
        assert self.visitor.visit(ast) == "x / 3"

    def test_unary_minus_variable(self):
        ast = UnaryOpNode("-", VariableNode("x"))
        assert self.visitor.visit(ast) == "-x"

    def test_unary_minus_constant(self):
        ast = UnaryOpNode("-", ConstantNode(5))
        assert self.visitor.visit(ast) == "-5"

    def test_unary_minus_parens(self):
        inner = BinaryOpNode("+", VariableNode("x"), ConstantNode(1))
        ast = UnaryOpNode("-", inner)
        result = self.visitor.visit(ast)
        assert result == "-(x + 1)"

    def test_double_negation(self):
        ast = UnaryOpNode("-", UnaryOpNode("-", VariableNode("x")))
        result = self.visitor.visit(ast)
        assert result == "--x"

    def test_complex_expression(self):
        # (x + 1) * (y - 2)
        left = BinaryOpNode("+", VariableNode("x"), ConstantNode(1))
        right = BinaryOpNode("-", VariableNode("y"), ConstantNode(2))
        ast = BinaryOpNode("*", left, right)
        result = self.visitor.visit(ast)
        assert result == "(x + 1) * (y - 2)"

    def test_non_associative_right_side(self):
        # a - b - c should stay as (a - b) - c, but a - (b - c) needs parens
        # (a - b) - c
        inner = BinaryOpNode("-", VariableNode("a"), VariableNode("b"))
        ast = BinaryOpNode("-", inner, VariableNode("c"))
        result = self.visitor.visit(ast)
        assert result == "a - b - c"

        # a - (b - c)
        inner = BinaryOpNode("-", VariableNode("b"), VariableNode("c"))
        ast = BinaryOpNode("-", VariableNode("a"), inner)
        result = self.visitor.visit(ast)
        assert result == "a - (b - c)"
