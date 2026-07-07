import pytest
from src.tokenizer import Tokenizer
from src.lexer import Lexer
from src.parser import Parser
from src.ast import (
    ConstantNode, VariableNode, BinaryOpNode, UnaryOpNode, EquationNode,
)
from src.utilities.errors import LexerError, ParserError


class TestParser:
    def parse(self, text: str):
        toks = Tokenizer(text).tokenize()
        Lexer().validate(toks)
        return Parser(toks).parse()

    def test_constant(self):
        ast = self.parse("5")
        assert isinstance(ast, ConstantNode)
        assert ast.value == 5

    def test_variable(self):
        ast = self.parse("x")
        assert isinstance(ast, VariableNode)
        assert ast.name == "x"

    def test_simple_addition(self):
        ast = self.parse("x+5")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "+"
        assert isinstance(ast.left, VariableNode)
        assert ast.left.name == "x"
        assert isinstance(ast.right, ConstantNode)
        assert ast.right.value == 5

    def test_implicit_multiplication(self):
        ast = self.parse("2x")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "*"
        assert isinstance(ast.left, ConstantNode)
        assert ast.left.value == 2
        assert isinstance(ast.right, VariableNode)
        assert ast.right.name == "x"

    def test_expression_with_implicit_mult(self):
        ast = self.parse("2x+5")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "+"
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "*"

    def test_simple_equation(self):
        ast = self.parse("2x+5=17")
        assert isinstance(ast, EquationNode)
        assert isinstance(ast.left, BinaryOpNode)
        assert isinstance(ast.right, ConstantNode)
        assert ast.right.value == 17

    def test_parentheses_grouping(self):
        ast = self.parse("2*(x+1)")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "*"
        assert isinstance(ast.left, ConstantNode)
        assert ast.left.value == 2
        assert isinstance(ast.right, BinaryOpNode)
        assert ast.right.operator == "+"

    def test_nested_parentheses(self):
        ast = self.parse("(x+2)*(y-3)")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "*"
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "+"
        assert isinstance(ast.right, BinaryOpNode)
        assert ast.right.operator == "-"

    def test_operator_precedence_mult_before_add(self):
        ast = self.parse("2x+5")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "+"
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "*"

    def test_operator_precedence_add_before_eq(self):
        ast = self.parse("x+5=10")
        assert isinstance(ast, EquationNode)
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "+"

    def test_unary_minus(self):
        ast = self.parse("-x")
        assert isinstance(ast, UnaryOpNode)
        assert ast.operator == "-"
        assert isinstance(ast.operand, VariableNode)

    def test_unary_minus_parentheses(self):
        ast = self.parse("-(x+1)")
        assert isinstance(ast, UnaryOpNode)
        assert ast.operator == "-"
        assert isinstance(ast.operand, BinaryOpNode)
        assert ast.operand.operator == "+"

    def test_double_negation(self):
        ast = self.parse("--x")
        assert isinstance(ast, UnaryOpNode)
        assert ast.operator == "-"
        assert isinstance(ast.operand, UnaryOpNode)
        assert ast.operand.operator == "-"

    def test_division(self):
        ast = self.parse("x/3")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "/"
        assert isinstance(ast.left, VariableNode)
        assert isinstance(ast.right, ConstantNode)
        assert ast.right.value == 3

    def test_chained_operations(self):
        ast = self.parse("x+y+z")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "+"
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "+"

    def test_missing_closing_paren(self):
        with pytest.raises((ParserError, LexerError)):
            self.parse("2*(x+1")

    def test_unexpected_token(self):
        with pytest.raises((ParserError, LexerError)):
            self.parse("2x+5=)17")

    def test_invalid_start(self):
        with pytest.raises((ParserError, LexerError)):
            self.parse(")x")

    def test_empty_parentheses(self):
        with pytest.raises((ParserError,)):
            self.parse("2*()")

    def test_lone_operator_at_end(self):
        with pytest.raises((ParserError,)):
            self.parse("2x+")

    def test_lone_operator(self):
        with pytest.raises((ParserError,)):
            self.parse("x+")

    def test_expression_only(self):
        ast = self.parse("2x+5")
        assert not isinstance(ast, EquationNode)

    def test_subtraction(self):
        ast = self.parse("5x-2")
        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "-"
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "*"

    def test_equals_expression_expression(self):
        ast = self.parse("x+1=y+2")
        assert isinstance(ast, EquationNode)
        assert isinstance(ast.left, BinaryOpNode)
        assert isinstance(ast.right, BinaryOpNode)
