from __future__ import annotations

from typing import Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr, ExprType
from .exceptions import UnsupportedOperation


class EquivalenceResult:
    """Result of an equivalence comparison."""

    def __init__(self, equivalent: bool,
                 method: str,
                 similarity: float = 1.0,
                 details: str = "") -> None:
        self._equivalent = equivalent
        self._method = method
        self._similarity = similarity
        self._details = details

    @property
    def equivalent(self) -> bool:
        return self._equivalent

    @property
    def method(self) -> str:
        return self._method

    @property
    def similarity(self) -> float:
        return self._similarity

    @property
    def details(self) -> str:
        return self._details

    def __repr__(self) -> str:
        return (f"EquivalenceResult(equivalent={self._equivalent}, "
                f"method='{self._method}', similarity={self._similarity})")


class EquivalenceEngine:
    """Determines equivalence between symbolic expressions.

    Supports three comparison methods:
    - Canonical: compare simplified forms
    - Structural: compare tree structure
    - Mathematical: compare by evaluating differences
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    def canonical_compare(self, a: SymbolicExpr,
                          b: SymbolicExpr) -> EquivalenceResult:
        """Compare by simplifying both to canonical form."""
        sa = self._backend.simplify(a)
        sb = self._backend.simplify(b)
        eq = sa == sb
        return EquivalenceResult(
            eq, "canonical",
            similarity=1.0 if eq else 0.0,
        )

    def structural_compare(self, a: SymbolicExpr,
                           b: SymbolicExpr) -> EquivalenceResult:
        """Compare tree structure (identical type/value/children)."""
        eq = a == b
        sim = self._compute_similarity(a, b)
        return EquivalenceResult(eq, "structural", similarity=sim)

    def mathematical_compare(self, a: SymbolicExpr,
                             b: SymbolicExpr) -> EquivalenceResult:
        """Compare by subtracting b from a and simplifying.

        If the result is zero, the expressions are equivalent.
        """
        diff = SymbolicExpr.sub(a, b)
        simplified = self._backend.simplify(diff)
        if simplified.is_number():
            eq = abs(simplified.value) < 1e-12
        else:
            eq = False
        return EquivalenceResult(
            eq, "mathematical",
            similarity=1.0 if eq else 0.0,
            details=str(simplified),
        )

    def are_equivalent(self, a: SymbolicExpr, b: SymbolicExpr,
                       method: str = "canonical") -> bool:
        """Check equivalence using the specified method."""
        methods = {
            "canonical": self.canonical_compare,
            "structural": self.structural_compare,
            "mathematical": self.mathematical_compare,
        }
        comparator = methods.get(method)
        if comparator is None:
            raise ValueError(f"Unknown comparison method: '{method}'")
        return comparator(a, b).equivalent

    def similarity(self, a: SymbolicExpr, b: SymbolicExpr) -> float:
        """Compute structural similarity score between 0.0 and 1.0."""
        return self._compute_similarity(a, b)

    @staticmethod
    def _compute_similarity(a: SymbolicExpr, b: SymbolicExpr) -> float:
        if a == b:
            return 1.0
        if a.type != b.type or a.value != b.value:
            return 0.0
        if not a.children and not b.children:
            return 1.0 if a == b else 0.0
        if not a.children or not b.children:
            return 0.0
        total = 0.0
        for ca, cb in zip(a.children, b.children):
            total += EquivalenceEngine._compute_similarity(ca, cb)
        return total / max(len(a.children), len(b.children))
