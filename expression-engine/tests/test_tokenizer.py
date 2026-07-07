import pytest
from src.tokenizer import Tokenizer, Token, TokenType
from src.utilities.errors import TokenizerError


class TestTokenizer:
    def test_simple_expression(self):
        toks = Tokenizer("2x+5").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.INTEGER, TokenType.ASTERISK, TokenType.VARIABLE,
            TokenType.PLUS, TokenType.INTEGER,
            TokenType.EOF,
        ]

    def test_simple_equation(self):
        toks = Tokenizer("2x+5=17").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.INTEGER, TokenType.ASTERISK, TokenType.VARIABLE,
            TokenType.PLUS, TokenType.INTEGER,
            TokenType.EQUALS,
            TokenType.INTEGER,
            TokenType.EOF,
        ]

    def test_explicit_multiplication(self):
        toks = Tokenizer("2*x").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.INTEGER, TokenType.ASTERISK, TokenType.VARIABLE,
            TokenType.EOF,
        ]

    def test_parentheses(self):
        toks = Tokenizer("2*(x+1)").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.INTEGER, TokenType.ASTERISK,
            TokenType.LPAREN, TokenType.VARIABLE, TokenType.PLUS,
            TokenType.INTEGER, TokenType.RPAREN,
            TokenType.EOF,
        ]

    def test_implicit_constant_variable(self):
        toks = Tokenizer("2x").tokenize()
        assert toks[0].type == TokenType.INTEGER
        assert toks[0].value == "2"
        assert toks[1].type == TokenType.ASTERISK
        assert toks[2].type == TokenType.VARIABLE
        assert toks[2].value == "x"

    def test_implicit_constant_paren(self):
        toks = Tokenizer("2(x+1)").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.INTEGER, TokenType.ASTERISK,
            TokenType.LPAREN, TokenType.VARIABLE, TokenType.PLUS,
            TokenType.INTEGER, TokenType.RPAREN,
            TokenType.EOF,
        ]

    def test_implicit_paren_paren(self):
        toks = Tokenizer("(x+1)(x+2)").tokenize()
        types = [t.type for t in toks]
        expected = [
            TokenType.LPAREN, TokenType.VARIABLE, TokenType.PLUS,
            TokenType.INTEGER, TokenType.RPAREN,
            TokenType.ASTERISK,
            TokenType.LPAREN, TokenType.VARIABLE, TokenType.PLUS,
            TokenType.INTEGER, TokenType.RPAREN,
            TokenType.EOF,
        ]
        assert types == expected

    def test_implicit_paren_variable(self):
        toks = Tokenizer("(x+1)x").tokenize()
        types = [t.type for t in toks]
        assert TokenType.ASTERISK in types

    def test_implicit_variable_paren(self):
        toks = Tokenizer("x(2)").tokenize()
        types = [t.type for t in toks]
        assert TokenType.ASTERISK in types

    def test_implicit_variable_variable(self):
        toks = Tokenizer("xy").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.VARIABLE, TokenType.ASTERISK, TokenType.VARIABLE,
            TokenType.EOF,
        ]

    def test_whitespace_handling(self):
        toks = Tokenizer("  2x  +  5  =  17  ").tokenize()
        values = [t.value for t in toks if t.type != TokenType.EOF]
        assert values == ["2", "*", "x", "+", "5", "=", "17"]

    def test_integer_values(self):
        toks = Tokenizer("42x+100").tokenize()
        int_tokens = [t for t in toks if t.type == TokenType.INTEGER]
        assert int_tokens[0].value == "42"
        assert int_tokens[1].value == "100"

    def test_single_token(self):
        toks = Tokenizer("x").tokenize()
        assert toks[0].type == TokenType.VARIABLE
        assert toks[1].type == TokenType.EOF

    def test_single_constant(self):
        toks = Tokenizer("5").tokenize()
        assert toks[0].type == TokenType.INTEGER
        assert toks[0].value == "5"

    def test_negative_constant(self):
        toks = Tokenizer("-5").tokenize()
        types = [t.type for t in toks]
        assert types == [TokenType.MINUS, TokenType.INTEGER, TokenType.EOF]

    def test_trailing_operator(self):
        toks = Tokenizer("5+").tokenize()
        types = [t.type for t in toks]
        assert types == [TokenType.INTEGER, TokenType.PLUS, TokenType.EOF]

    def test_invalid_character(self):
        with pytest.raises(TokenizerError):
            Tokenizer("2x@5").tokenize()

    def test_non_string_input(self):
        with pytest.raises(TokenizerError):
            Tokenizer(123)

    def test_empty_input(self):
        toks = Tokenizer("").tokenize()
        assert toks == [Token(TokenType.EOF, "", 0)]

    def test_implicit_multiple_after_variable(self):
        toks = Tokenizer("x(2)").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.VARIABLE, TokenType.ASTERISK,
            TokenType.LPAREN, TokenType.INTEGER, TokenType.RPAREN,
            TokenType.EOF,
        ]

    def test_no_implicit_mult_for_plus(self):
        toks = Tokenizer("x+2").tokenize()
        types = [t.type for t in toks]
        assert types == [
            TokenType.VARIABLE, TokenType.PLUS, TokenType.INTEGER,
            TokenType.EOF,
        ]
