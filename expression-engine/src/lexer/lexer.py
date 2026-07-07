from __future__ import annotations

from typing import Sequence

from src.tokenizer import Token, TokenType
from src.utilities.errors import LexerError


class Lexer:
    """Validates a sequence of tokens produced by the Tokenizer.

    Checks performed:
    - Non-empty input
    - No invalid consecutive operators
    - No operator at start or end (except unary minus)
    - Balanced parentheses
    - Valid equation structure (at most one ``=``)
    """

    _BINARY_OPS: set[TokenType] = {
        TokenType.PLUS, TokenType.MINUS,
        TokenType.ASTERISK, TokenType.SLASH,
    }

    _BINARY_OPS_NO_MINUS: set[TokenType] = {
        TokenType.PLUS, TokenType.ASTERISK, TokenType.SLASH,
    }

    def validate(self, tokens: Sequence[Token]) -> Sequence[Token]:
        tokens_list = list(tokens)
        if not tokens_list:
            raise LexerError("Empty expression")

        if tokens_list[-1].type == TokenType.EOF:
            body = tokens_list[:-1]
        else:
            body = tokens_list

        if not body:
            raise LexerError("Empty expression")

        self._check_balanced_parens(body)
        self._check_token_sequence(body)
        self._check_equation_structure(body)

        return tokens_list

    def _check_balanced_parens(self, tokens: Sequence[Token]) -> None:
        depth = 0
        for tok in tokens:
            if tok.type == TokenType.LPAREN:
                depth += 1
            elif tok.type == TokenType.RPAREN:
                depth -= 1
                if depth < 0:
                    raise LexerError(
                        f"Unmatched closing parenthesis at position {tok.position}"
                    )
        if depth != 0:
            raise LexerError(
                f"Unmatched opening parenthesis (missing {depth} closing "
                f"parenthesis)"
            )

    def _check_token_sequence(self, tokens: Sequence[Token]) -> None:
        for i, tok in enumerate(tokens):
            if i == 0:
                if tok.type in self._BINARY_OPS_NO_MINUS:
                    raise LexerError(
                        f"Expression cannot start with {tok.value!r} "
                        f"at position {tok.position}"
                    )
                continue

            prev = tokens[i - 1]
            if tok.type in self._BINARY_OPS:
                if prev.type in self._BINARY_OPS:
                    if tok.type == TokenType.MINUS:
                        pass
                    elif prev.type == TokenType.MINUS and tok.type in self._BINARY_OPS_NO_MINUS:
                        raise LexerError(
                            f"Unexpected operator {tok.value!r} after '-' "
                            f"at position {tok.position}"
                        )
                    elif prev.type in self._BINARY_OPS:
                        raise LexerError(
                            f"Consecutive operators {prev.value!r} and {tok.value!r} "
                            f"at positions {prev.position}, {tok.position}"
                        )
                if prev.type == TokenType.EQUALS and tok.type in self._BINARY_OPS_NO_MINUS:
                    raise LexerError(
                        f"Operator {tok.value!r} cannot follow '=' "
                        f"at position {tok.position}"
                    )

            if tok.type == TokenType.EQUALS:
                if prev.type in (TokenType.EQUALS,):
                    raise LexerError(
                        f"Consecutive '=' at position {tok.position}"
                    )

    def _check_equation_structure(self, tokens: Sequence[Token]) -> None:
        eq_count = sum(1 for t in tokens if t.type == TokenType.EQUALS)
        if eq_count > 1:
            raise LexerError(
                f"Multiple '=' signs ({eq_count}) in expression"
            )

        if eq_count == 1:
            eq_idx = next(i for i, t in enumerate(tokens)
                          if t.type == TokenType.EQUALS)
            if eq_idx == 0:
                raise LexerError("Expression cannot start with '='")
            if eq_idx == len(tokens) - 1:
                raise LexerError("Expression cannot end with '='")
