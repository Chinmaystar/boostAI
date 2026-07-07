from __future__ import annotations

from typing import Any, Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr, ExprType
from .exceptions import DivisionByZero, DomainError


class EvaluationEngine:
    """Evaluates symbolic expressions, equations, and constraints.

    Supports variable substitution, numeric evaluation, equation
    verification, and constraint evaluation.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    def substitute(self, expr: SymbolicExpr, var: str,
                   val: SymbolicExpr) -> SymbolicExpr:
        """Replace *var* with *val* in *expr*."""
        return self._backend.substitute(expr, var, val)

    def substitute_all(self, expr: SymbolicExpr,
                       substitutions: dict[str, SymbolicExpr]
                       ) -> SymbolicExpr:
        """Apply multiple substitutions."""
        result = expr
        for var, val in substitutions.items():
            result = self._backend.substitute(result, var, val)
        return result

    def evaluate(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Evaluate constant sub-expressions numerically."""
        return self._backend.evaluate(expr)

    def evaluate_numeric(self, expr: SymbolicExpr) -> float:
        """Evaluate to a single float.

        Raises TypeError if the expression is not fully numeric.
        """
        evaluated = self._backend.evaluate(expr)
        if evaluated.is_number():
            return evaluated.value
        raise TypeError(
            f"Cannot evaluate to a single numeric value: {evaluated}")

    def evaluate_with_values(self, expr: SymbolicExpr,
                             values: dict[str, float]
                             ) -> float:
        """Substitute numeric values and evaluate.

        Parameters
        ----------
        expr : SymbolicExpr
            Expression to evaluate.
        values : dict[str, float]
            Mapping of variable names to numeric values.

        Returns
        -------
        float result.
        """
        sub_expr = self.substitute_all(
            expr,
            {var: SymbolicExpr.number(val)
             for var, val in values.items()},
        )
        return self.evaluate_numeric(sub_expr)

    def check_equation(self, equation: SymbolicExpr,
                       values: dict[str, float]) -> bool:
        """Check if an equation holds for the given variable values.

        Parameters
        ----------
        equation : SymbolicExpr
            Must be an EQUAL expression.
        values : dict[str, float]
            Variable assignments.

        Returns
        -------
        True if left ≈ right within tolerance.
        """
        if not equation.is_equal():
            raise TypeError("Equation must be an EQUAL expression")
        left_val = self.evaluate_with_values(equation.left(), values)
        right_val = self.evaluate_with_values(equation.right(), values)
        return abs(left_val - right_val) < 1e-12

    def verify_solution(self, equation: SymbolicExpr,
                        variable: str,
                        solution: SymbolicExpr) -> bool:
        """Verify that *solution* satisfies *equation*.

        Parameters
        ----------
        equation : SymbolicExpr
            EQUAL expression.
        variable : str
            Variable name.
        solution : SymbolicExpr
            Proposed solution value.

        Returns
        -------
        True if the equation holds when *variable* is replaced by
        *solution*.
        """
        if not solution.is_number():
            return False
        return self.check_equation(
            equation, {variable: solution.value})

    def evaluate_constraint(self, condition: SymbolicExpr,
                            variables: dict[str, float],
                            expected: bool = True) -> bool:
        """Evaluate a boolean constraint expression.

        The constraint is an expression like ``x > 0`` or ``x == y``
        represented as a symbolic expression tree.

        Parameters
        ----------
        condition : SymbolicExpr
            Constraint expression.
        variables : dict[str, float]
            Variable values.
        expected : bool
            Expected truth value (default True).

        Returns
        -------
        True if result matches expected.
        """
        result = self.evaluate_with_values(condition, variables)
        return bool(result) == expected
