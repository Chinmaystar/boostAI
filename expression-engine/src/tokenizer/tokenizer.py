from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from src.utilities.errors import TokenizerError


class TokenType(Enum):
    INTEGER = auto()
    VARIABLE = auto()
    PLUS = auto()
    MINUS = auto()
    ASTERISK = auto()
    SLASH = auto()
    LPAREN = auto()
    RPAREN = auto()
    EQUALS = auto()
    EOF = auto()


_TOKEN_CHARS: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.ASTERISK,
    "/": TokenType.SLASH,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "=": TokenType.EQUALS,
}

_IMPLICIT_RIGHT_TRIGGERS: set[TokenType] = {
    TokenType.INTEGER,
    TokenType.RPAREN,
    TokenType.VARIABLE,
}

_IMPLICIT_LEFT_TARGETS: set[TokenType] = {
    TokenType.LPAREN,
    TokenType.VARIABLE,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"


class Tokenizer:

    def __init__(self, text: str) -> None:
        if not isinstance(text, str):
            raise TokenizerError(f"Expected string, got {type(text).__name__}")
        self._text: str = text
        self._pos: int = 0

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self._pos < len(self._text):
            ch = self._text[self._pos]
            if ch.isspace():
                self._pos += 1
                continue

            if ch.isdigit():
                token = self._read_integer()
                tokens.append(token)
                self._maybe_insert_implicit_mult(tokens)
                continue

            if ch.isalpha():
                token = self._read_variable()
                tokens.append(token)
                self._maybe_insert_implicit_mult(tokens)
                continue

            if ch in _TOKEN_CHARS:
                tt = _TOKEN_CHARS[ch]
                tokens.append(Token(tt, ch, self._pos))
                self._pos += 1
                self._maybe_insert_implicit_mult(tokens)
                continue

            raise TokenizerError(
                f"Unexpected character {ch!r} at position {self._pos}"
            )

        tokens.append(Token(TokenType.EOF, "", self._pos))
        return tokens

    def _read_integer(self) -> Token:
        start = self._pos
        while self._pos < len(self._text) and self._text[self._pos].isdigit():
            self._pos += 1
        return Token(TokenType.INTEGER, self._text[start:self._pos], start)

    def _read_variable(self) -> Token:
        start = self._pos
        self._pos += 1
        return Token(TokenType.VARIABLE, self._text[start:self._pos], start)

    def _maybe_insert_implicit_mult(self, tokens: list[Token]) -> None:
        if len(tokens) < 2:
            return
        prev = tokens[-2]
        curr = tokens[-1]
        if prev.type in _IMPLICIT_RIGHT_TRIGGERS and curr.type in _IMPLICIT_LEFT_TARGETS:
            tokens.insert(
                len(tokens) - 1,
                Token(TokenType.ASTERISK, "*", prev.position),
            )
