from __future__ import annotations

from typing import Any, Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr, ExprType
from .exceptions import DivisionByZero, ExpressionNotPolynomial


class AlgebraEngine:
    """Algebraic operations on symbolic expressions.

    Supports expansion, factorisation, substitution, collection of
    like terms, constant evaluation, fraction arithmetic, and
    polynomial arithmetic.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    # ── core algebra ───────────────────────────────────────────

    def expand(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Expand products of sums and powers."""
        return self._backend.expand(expr)

    def factor(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Factor an expression."""
        return self._backend.factor(expr)

    def substitute(self, expr: SymbolicExpr, var: str,
                   val: SymbolicExpr) -> SymbolicExpr:
        """Replace all occurrences of *var* with *val*."""
        return self._backend.substitute(expr, var, val)

    def collect_like_terms(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Collect and combine like terms."""
        return self._backend.collect_like_terms(expr)

    def evaluate_constants(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Evaluate all constant sub-expressions."""
        return self._backend.evaluate(expr)

    # ── fraction arithmetic ─────────────────────────────────────

    def fraction_add(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        return self._backend.fraction_add(a, b)

    def fraction_sub(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        return self._backend.fraction_sub(a, b)

    def fraction_mul(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        return self._backend.fraction_mul(a, b)

    def fraction_div(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        return self._backend.fraction_div(a, b)

    def fraction_simplify(self, a: tuple[int | float, int | float]
                          ) -> tuple[int, int]:
        return self._backend.fraction_simplify(a)

    # ── polynomial arithmetic ───────────────────────────────────

    def degree(self, expr: SymbolicExpr, var: str) -> int:
        """Return the degree of *expr* as a polynomial in *var*."""
        return self._backend.degree(expr, var)

    def coefficients(self, expr: SymbolicExpr,
                     var: str) -> list[SymbolicExpr]:
        """Return coefficients as a polynomial in *var*."""
        return self._backend.coefficients(expr, var)

    def polynomial_add(self, a: SymbolicExpr, b: SymbolicExpr,
                       var: str) -> SymbolicExpr:
        """Add two polynomials in *var*."""
        return self._backend.simplify(SymbolicExpr.add(a, b))

    def polynomial_sub(self, a: SymbolicExpr, b: SymbolicExpr,
                       var: str) -> SymbolicExpr:
        """Subtract two polynomials in *var*."""
        return self._backend.simplify(SymbolicExpr.sub(a, b))

    def polynomial_mul(self, a: SymbolicExpr, b: SymbolicExpr,
                       var: str) -> SymbolicExpr:
        """Multiply two polynomials in *var*."""
        return self._backend.expand(SymbolicExpr.mul(a, b))

    def polynomial_pow(self, base: SymbolicExpr, exp: int,
                       var: str) -> SymbolicExpr:
        """Raise a polynomial to a non-negative integer power."""
        if exp < 0:
            raise ValueError("Negative exponents not supported")
        if exp == 0:
            return SymbolicExpr.number(1)
        if exp == 1:
            return base
        result = base
        for _ in range(exp - 1):
            result = self._backend.expand(SymbolicExpr.mul(result, base))
        return result

    # ── utility ─────────────────────────────────────────────────

    def is_linear(self, expr: SymbolicExpr, var: str) -> bool:
        """Check if *expr* is linear in *var*."""
        return self.degree(expr, var) == 1

    def is_quadratic(self, expr: SymbolicExpr, var: str) -> bool:
        """Check if *expr* is quadratic in *var*."""
        return self.degree(expr, var) == 2

    def is_polynomial(self, expr: SymbolicExpr, var: str) -> bool:
        """Check if *expr* is a polynomial in *var*."""
        try:
            deg = self.degree(expr, var)
            return deg >= 0
        except ExpressionNotPolynomial:
            return False
