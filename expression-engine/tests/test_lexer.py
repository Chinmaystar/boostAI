import pytest
from src.tokenizer import Tokenizer, TokenType
from src.lexer import Lexer
from src.utilities.errors import LexerError


class TestLexer:
    def make_lexer(self) -> Lexer:
        return Lexer()

    def tokenize(self, text: str):
        return Tokenizer(text).tokenize()

    def test_valid_expression(self):
        toks = self.tokenize("2x+5")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_valid_equation(self):
        toks = self.tokenize("2x+5=17")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_valid_parentheses(self):
        toks = self.tokenize("(x+2)")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_empty_expression(self):
        toks = self.tokenize("")
        with pytest.raises(LexerError, match="Empty expression"):
            self.make_lexer().validate(toks)

    def test_whitespace_only(self):
        toks = self.tokenize("   ")
        with pytest.raises(LexerError, match="Empty expression"):
            self.make_lexer().validate(toks)

    def test_consecutive_plus_minus(self):
        toks = self.tokenize("2++x")
        with pytest.raises(LexerError, match="Consecutive operators"):
            self.make_lexer().validate(toks)

    def test_consecutive_operators(self):
        toks = self.tokenize("2*+x")
        with pytest.raises(LexerError, match="Consecutive operators"):
            self.make_lexer().validate(toks)

    def test_starts_with_operator(self):
        toks = self.tokenize("*x")
        with pytest.raises(LexerError, match="cannot start"):
            self.make_lexer().validate(toks)

    def test_starts_with_plus(self):
        toks = self.tokenize("+x")
        with pytest.raises(LexerError, match="cannot start"):
            self.make_lexer().validate(toks)

    def test_starts_with_minus_allowed(self):
        toks = self.tokenize("-x")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_starts_with_minus_constant(self):
        toks = self.tokenize("-5")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_unmatched_lparen(self):
        toks = self.tokenize("(x+2")
        with pytest.raises(LexerError, match="Unmatched opening parenthesis"):
            self.make_lexer().validate(toks)

    def test_unmatched_rparen(self):
        toks = self.tokenize("x+2)")
        with pytest.raises(LexerError, match="Unmatched closing parenthesis"):
            self.make_lexer().validate(toks)

    def test_empty_parens(self):
        toks = self.tokenize("()")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_multiple_equals(self):
        toks = self.tokenize("x=y=z")
        with pytest.raises(LexerError, match="Multiple"):
            self.make_lexer().validate(toks)

    def test_equals_at_start(self):
        toks = self.tokenize("=x")
        with pytest.raises(LexerError, match="cannot start with '='"):
            self.make_lexer().validate(toks)

    def test_equals_at_end(self):
        toks = self.tokenize("x=")
        with pytest.raises(LexerError, match="cannot end with '='"):
            self.make_lexer().validate(toks)

    def test_operator_after_equals(self):
        # "x = +5" is questionable
        toks = self.tokenize("x=+5")
        with pytest.raises(LexerError, match="cannot follow"):
            self.make_lexer().validate(toks)

    def test_double_equals(self):
        toks = self.tokenize("x==5")
        with pytest.raises(LexerError, match="Consecutive"):
            self.make_lexer().validate(toks)

    def test_complex_valid(self):
        text = "2x + 3*(x-5) = 12"
        toks = self.tokenize(text)
        result = self.make_lexer().validate(toks)
        assert len(result) > 0

    def test_leading_minus_paren(self):
        toks = self.tokenize("-(x+1)")
        result = self.make_lexer().validate(toks)
        assert len(result) > 0
