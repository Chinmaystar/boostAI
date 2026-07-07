from __future__ import annotations

from typing import Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr
from .visitor import ToStringVisitor


class ExpressionEngine:
    """High-level operations on symbolic expressions.

    Handles representation, comparison, normalization, simplification,
    serialization, and reconstruction of expressions.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend
        self._stringifier = ToStringVisitor()

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    def simplify(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Simplify an expression to its most compact form."""
        return self._backend.simplify(expr)

    def normalize(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Normalize an expression (simplify + canonical ordering)."""
        simplified = self._backend.simplify(expr)
        return self._canonical_order(simplified)

    def _canonical_order(self, expr: SymbolicExpr) -> SymbolicExpr:
        if not expr.children:
            return expr
        ordered_children = tuple(
            sorted((self._canonical_order(c) for c in expr.children),
                   key=self._sort_key))
        return SymbolicExpr(expr.type, expr.value, ordered_children)

    @staticmethod
    def _sort_key(expr: SymbolicExpr) -> tuple:
        if expr.is_number():
            return (0, expr.value, "")
        if expr.is_symbol():
            return (1, 0, expr.value)
        return (2, expr.size(), "")

    def compare(self, a: SymbolicExpr, b: SymbolicExpr) -> bool:
        """Structural comparison — returns True when trees are identical."""
        return a == b

    def serialize(self, expr: SymbolicExpr) -> str:
        """Convert expression to string."""
        return self._backend.serialize(expr)

    def deserialize(self, text: str) -> SymbolicExpr:
        """Parse string into expression."""
        return self._backend.parse(text)

    def reconstruct(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Reconstruct expression (simplify + evaluate constants)."""
        return self._backend.evaluate(self._backend.simplify(expr))

    def symbols(self, expr: SymbolicExpr) -> set[str]:
        """Return all symbol names in the expression."""
        return expr.symbols()

    def depth(self, expr: SymbolicExpr) -> int:
        """Return the depth of the expression tree."""
        return expr.depth()

    def size(self, expr: SymbolicExpr) -> int:
        """Return the number of nodes in the expression tree."""
        return expr.size()

    def substitute(self, expr: SymbolicExpr, var: str,
                   val: SymbolicExpr) -> SymbolicExpr:
        """Substitute a variable with a value."""
        return self._backend.substitute(expr, var, val)

    def evaluate(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Evaluate constant sub-expressions."""
        return self._backend.evaluate(expr)
