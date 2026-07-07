from __future__ import annotations

from typing import Optional, Sequence

from src.ast import (
    ASTNode, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
)
from src.tokenizer import Token, TokenType
from src.utilities.errors import ParserError


class Parser:
    """Recursive-descent parser for mathematical expressions.

    Grammar (Milestone 1)::

        equation    → expression ("=" expression)?
        expression  → term (("+" | "-") term)*
        term        → unary (("*" | "/") unary)*
        unary       → "-" unary | primary
        primary     → INTEGER | VARIABLE | "(" expression ")"
    """

    def __init__(self, tokens: Sequence[Token]) -> None:
        self._tokens: list[Token] = list(tokens)
        self._pos: int = 0

    def parse(self) -> ASTNode:
        if not self._tokens:
            raise ParserError("No tokens to parse")
        result = self._parse_equation()
        if self._peek().type != TokenType.EOF:
            raise ParserError(
                f"Unexpected token {self._peek().value!r} at position "
                f"{self._peek().position}"
            )
        return result

    def _parse_equation(self) -> ASTNode:
        left = self._parse_expression()
        if self._peek().type == TokenType.EQUALS:
            self._advance()
            right = self._parse_expression()
            return EquationNode(left, right)
        return left

    def _parse_expression(self) -> ASTNode:
        left = self._parse_term()
        while self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._advance().value
            right = self._parse_term()
            left = BinaryOpNode(op, left, right)
        return left

    def _parse_term(self) -> ASTNode:
        left = self._parse_unary()
        while self._peek().type in (TokenType.ASTERISK, TokenType.SLASH):
            op = self._advance().value
            right = self._parse_unary()
            left = BinaryOpNode(op, left, right)
        return left

    def _parse_unary(self) -> ASTNode:
        if self._peek().type == TokenType.MINUS:
            self._advance()
            operand = self._parse_unary()
            return UnaryOpNode("-", operand)
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.INTEGER:
            self._advance()
            return ConstantNode(int(tok.value))

        if tok.type == TokenType.VARIABLE:
            self._advance()
            return VariableNode(tok.value)

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            if self._peek().type != TokenType.RPAREN:
                raise ParserError(
                    f"Missing closing parenthesis at position "
                    f"{self._peek().position}"
                )
            self._advance()
            return expr

        raise ParserError(
            f"Unexpected token {tok.value!r} ({tok.type.name}) "
            f"at position {tok.position}"
        )

    def _peek(self) -> Token:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return self._tokens[-1] if self._tokens else None

    def _advance(self) -> Token:
        tok = self._peek()
        self._pos += 1
        return tok
