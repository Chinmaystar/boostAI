from __future__ import annotations

from typing import Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr, ExprType
from .exceptions import (
    NoSolution, InfiniteSolutions, UnsupportedOperation,
    InvalidExpression,
)


class EquationResult:
    """Result of solving an equation."""

    def __init__(self, solutions: list[SymbolicExpr],
                 variable: str) -> None:
        self._solutions = solutions
        self._variable = variable

    @property
    def solutions(self) -> list[SymbolicExpr]:
        return list(self._solutions)

    @property
    def variable(self) -> str:
        return self._variable

    @property
    def has_solution(self) -> bool:
        return len(self._solutions) > 0

    @property
    def solution_count(self) -> int:
        return len(self._solutions)

    def solution_values(self) -> list[float]:
        return [s.value for s in self._solutions if s.is_number()]

    def __repr__(self) -> str:
        return (f"EquationResult(solutions={self._solutions}, "
                f"variable='{self._variable}')")


class EquationEngine:
    """Solves algebraic equations.

    Supports linear, quadratic, and basic polynomial equations.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    def solve(self, equation: SymbolicExpr,
              variable: str) -> EquationResult:
        """Solve an equation for the given variable.

        Parameters
        ----------
        equation : SymbolicExpr
            Must be an EQUAL expression (left = right).
        variable : str
            Name of the variable to solve for.

        Returns
        -------
        EquationResult containing solutions.
        """
        if not equation.is_equal():
            raise InvalidExpression("solve() requires an EQUAL expression")
        try:
            solutions = self._backend.solve(equation, variable)
        except NoSolution:
            return EquationResult([], variable)
        except InfiniteSolutions:
            return EquationResult([], variable)
        return EquationResult(solutions, variable)

    def solve_linear(self, a: float, b: float, variable: str = "x"
                     ) -> EquationResult:
        """Solve a*x + b = 0."""
        expr = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(a),
                                 SymbolicExpr.symbol(variable)),
                SymbolicExpr.number(b),
            ),
            SymbolicExpr.number(0),
        )
        return self.solve(expr, variable)

    def solve_quadratic(self, a: float, b: float, c: float,
                        variable: str = "x") -> EquationResult:
        """Solve a*x^2 + b*x + c = 0."""
        expr = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.add(
                    SymbolicExpr.mul(
                        SymbolicExpr.number(a),
                        SymbolicExpr.pow(
                            SymbolicExpr.symbol(variable),
                            SymbolicExpr.number(2),
                        ),
                    ),
                    SymbolicExpr.mul(SymbolicExpr.number(b),
                                     SymbolicExpr.symbol(variable)),
                ),
                SymbolicExpr.number(c),
            ),
            SymbolicExpr.number(0),
        )
        return self.solve(expr, variable)

    def is_identity(self, equation: SymbolicExpr) -> bool:
        """Check if equation is an identity (always true)."""
        if not equation.is_equal():
            return False
        diff = SymbolicExpr.sub(equation.left(), equation.right())
        simplified = self._backend.simplify(diff)
        return simplified.is_number() and simplified.value == 0

    def has_solution(self, equation: SymbolicExpr,
                     variable: str) -> bool:
        """Check if an equation has at least one solution."""
        try:
            result = self.solve(equation, variable)
            return result.has_solution
        except (UnsupportedOperation, InvalidExpression):
            return False
