from __future__ import annotations

import hashlib

from src.ast import (
    ASTNode, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
)


_ADDITIVE_OPS = frozenset({"+", "-"})
_MULTIPLICATIVE_OPS = frozenset({"*", "/"})


class StructuralHasher:
    """Generates a deterministic hash from the structural shape of an AST.

    The structural shape ignores concrete values (constants, variable names)
    and collapses operators into broad categories, keeping only the tree
    skeleton. This allows structurally equivalent expressions (e.g.
    ``2x+5=17`` and ``7x+3=38``) to produce identical hashes while still
    distinguishing additive vs multiplicative structure.

    Node encoding:
        - ``ConstantNode`` → ``C``
        - ``VariableNode`` → ``V``
        - ``BinaryOpNode`` (additive ``+`` / ``-``) → ``A(left,right)``
        - ``BinaryOpNode`` (multiplicative ``*`` / ``/``) → ``M(left,right)``
        - ``UnaryOpNode`` → ``U(operand)``
        - ``EquationNode`` → ``E(left,right)``
    """

    @staticmethod
    def fingerprint(node: ASTNode) -> str:
        """Produce a structural fingerprint string.

        Args:
            node: The root AST node.

        Returns:
            A string such as ``"E(A(M(C,V),C),C)"`` representing the
            abstract tree shape with operator categories preserved.
        """
        return _fingerprint(node)

    @staticmethod
    def hash(node: ASTNode) -> str:
        """Return a SHA-256 hex digest of the structural fingerprint.

        Args:
            node: The root AST node.

        Returns:
            A 64-character hex-encoded SHA-256 hash.
        """
        fp = _fingerprint(node)
        return hashlib.sha256(fp.encode("utf-8")).hexdigest()


def _fingerprint(node: ASTNode) -> str:
    if isinstance(node, ConstantNode):
        return "C"
    if isinstance(node, VariableNode):
        return "V"
    if isinstance(node, UnaryOpNode):
        return f"U({_fingerprint(node.operand)})"
    if isinstance(node, BinaryOpNode):
        left = _fingerprint(node.left)
        right = _fingerprint(node.right)
        code = _operator_code(node.operator)
        a, b = sorted([left, right])
        return f"{code}({a},{b})"
    if isinstance(node, EquationNode):
        return f"E({_fingerprint(node.left)},{_fingerprint(node.right)})"
    raise ValueError(f"Unknown node type: {type(node).__name__}")


def _operator_code(op: str) -> str:
    if op in _ADDITIVE_OPS:
        return "A"
    if op in _MULTIPLICATIVE_OPS:
        return "M"
    raise ValueError(f"Unknown operator: {op!r}")
