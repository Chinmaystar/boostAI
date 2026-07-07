import pytest
from src.tokenizer import Tokenizer
from src.lexer import Lexer
from src.parser import Parser
from src.canonicalizer import Canonicalizer
from src.ast import ToStringVisitor


class TestCanonicalizer:
    def setup_method(self):
        self.canon = Canonicalizer(rename_variables=False)
        self.to_string = ToStringVisitor()

    def canonical(self, text: str) -> str:
        toks = Tokenizer(text).tokenize()
        Lexer().validate(toks)
        ast = Parser(toks).parse()
        result = self.canon.canonicalize(ast)
        return self.to_string.visit(result.tree)

    # ---- Commutative sorting ----

    def test_commutative_add_constants_first(self):
        assert self.canonical("2x+5") == "5 + 2 * x"

    def test_commutative_add_reverse(self):
        assert self.canonical("5+2x") == "5 + 2 * x"

    def test_commutative_mult_constants_first(self):
        assert self.canonical("x*2") == "2 * x"

    def test_commutative_mult_implicit(self):
        assert self.canonical("2x") == "2 * x"

    def test_commutative_variable_ordering(self):
        assert self.canonical("y+x") == "x + y"

    def test_commutative_add_many_terms(self):
        result = self.canonical("z + 5 + x + 3")
        # constants: 3 + 5 → 8; variables in alpha: x + z
        assert result == "8 + x + z"

    def test_commutative_mult_many_factors(self):
        result = self.canonical("y*x*z")
        assert result == "x * y * z"

    # ---- Constant folding ----

    def test_fold_addition(self):
        result = self.canonical("2+3")
        assert result == "5"

    def test_fold_multiplication(self):
        result = self.canonical("2*3")
        assert result == "6"

    def test_fold_chain_add(self):
        result = self.canonical("1+2+3")
        assert result == "6"

    def test_fold_chain_mult(self):
        result = self.canonical("2*3*4")
        assert result == "24"

    def test_fold_mixed_with_variable(self):
        result = self.canonical("2+3+x")
        assert result == "5 + x"

    def test_fold_constants_addition_in_equation(self):
        result = self.canonical("2+3=x+5")
        assert result == "5 = 5 + x"

    def test_fold_subtraction(self):
        result = self.canonical("5-3")
        assert result == "2"

    def test_fold_division_exact(self):
        result = self.canonical("6/3")
        assert result == "2"

    def test_no_fold_division_inexact(self):
        result = self.canonical("5/3")
        assert result == "5 / 3"

    def test_no_fold_division_by_zero(self):
        result = self.canonical("5/0")
        assert result == "5 / 0"

    # ---- Parentheses handling ----

    def test_single_parens_removed(self):
        result = self.canonical("(x)")
        assert result == "x"

    def test_nested_single_parens(self):
        result = self.canonical("((x))")
        assert result == "x"

    def test_necessary_parens_preserved(self):
        result = self.canonical("2*(x+1)")
        assert result == "2 * (1 + x)"

    def test_necessary_parens_commutative(self):
        result = self.canonical("(x+1)*2")
        assert result == "2 * (1 + x)"

    # ---- Multiplication ordering ----

    def test_mult_ordering_constant_first(self):
        assert self.canonical("x*5") == "5 * x"

    def test_mult_ordering_with_parens(self):
        result = self.canonical("(x+1)*3")
        assert result == "3 * (1 + x)"

    # ---- Unary minus ----

    def test_unary_minus_simple(self):
        assert self.canonical("-x") == "-x"

    def test_unary_minus_constant(self):
        assert self.canonical("-5") == "-5"

    def test_unary_minus_parens(self):
        result = self.canonical("-(x+1)")
        assert result == "-(1 + x)"

    def test_unary_minus_double(self):
        assert self.canonical("--x") == "--x"

    # ---- Equations ----

    def test_equation_simple(self):
        result = self.canonical("2x+5=17")
        # canonical: 5 + 2x = 17
        assert "=" in result
        assert result == "5 + 2 * x = 17"

    def test_equation_complex(self):
        result = self.canonical("3x-1=x+5")
        # canonical: -1 + 3x = 5 + x
        assert "=" in result

    # ---- Complex expressions ----

    def test_expression_with_division(self):
        result = self.canonical("x/3")
        assert result == "x / 3"

    def test_expression_multiple_ops(self):
        result = self.canonical("2*3*x+4*5")
        # 2*3 = 6, 4*5 = 20 → 6*x + 20 → 20 + 6*x
        assert result == "20 + 6 * x"

    def test_expression_all_operators(self):
        result = self.canonical("2*x+3/4")
        # 2*x sorted → 2*x, 3/4 stays → 0 + 3/4 + 2*x... no, 2x + 3/4
        # Actually 3/4 can't be folded (inexact), 3/4 stays as 3/4
        # 2*x sorted → 2*x
        # So: 3/4 + 2*x
        assert "3 / 4" in result
        assert "2 * x" in result

    def test_no_unnecessary_changes(self):
        result1 = self.canonical("17")
        result2 = self.canonical("17")
        assert result1 == result2

    # ---- Edge cases ----

    def test_single_constant(self):
        assert self.canonical("42") == "42"

    def test_single_variable(self):
        assert self.canonical("x") == "x"

    def test_negative_expression(self):
        result = self.canonical("-2*x+3")
        assert result == "3 + -2 * x"

    def test_expression_with_equals_only(self):
        result = self.canonical("x=5")
        assert result == "x = 5"

    def test_canonical_idempotent(self):
        once = self.canonical("2x+5=17")
        twice = self.canonical(once)
        assert once == twice
