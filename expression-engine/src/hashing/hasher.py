from __future__ import annotations

import hashlib

from src.ast import ASTNode, ToStringVisitor
from src.canonicalizer import Canonicalizer


class CanonicalHasher:
    """Generates a deterministic, content-addressed hash from the
    canonical form of an expression.

    Usage::

        hasher = CanonicalHasher()
        h1 = hasher.hash("2x + 5")
        h2 = hasher.hash("5 + 2x")
        assert h1 == h2   # equivalent after canonicalization
    """

    def __init__(self, rename_variables: bool = False) -> None:
        self._canonicalizer = Canonicalizer(
            rename_variables=rename_variables,
        )
        self._to_string = ToStringVisitor()

    def hash(self, expression: str) -> str:
        """Tokenize, parse, canonicalize, and hash the expression.

        Args:
            expression: A raw mathematical expression string.

        Returns:
            A hex-encoded SHA-256 digest of the canonical form.

        Raises:
            ExpressionError: If any stage of the pipeline fails.
        """
        canonical_str = self.canonical_string(expression)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def canonical_string(self, expression: str) -> str:
        """Tokenize, parse, and canonicalize, returning the canonical
        string form (without hashing).

        Useful for debugging and visual inspection.
        """
        from src.tokenizer import Tokenizer
        from src.lexer import Lexer
        from src.parser import Parser

        tokens = Tokenizer(expression).tokenize()
        Lexer().validate(tokens)
        ast = Parser(tokens).parse()
        result = self._canonicalizer.canonicalize(ast)
        return self._to_string.visit(result.tree)

    def hash_ast(self, node: ASTNode) -> str:
        """Hash an already-constructed AST directly."""
        result = self._canonicalizer.canonicalize(node)
        canonical_str = self._to_string.visit(result.tree)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
