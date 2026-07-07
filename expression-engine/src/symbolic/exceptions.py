from __future__ import annotations


class SymbolicError(Exception):
    """Base exception for all symbolic mathematics errors."""


class DivisionByZero(SymbolicError):
    """Raised when an expression involves division by zero."""


class UnsimplifiableExpression(SymbolicError):
    """Raised when an expression cannot be simplified further."""


class UnsupportedOperation(SymbolicError):
    """Raised when a symbolic operation is not supported by the backend."""


class NoSolution(SymbolicError):
    """Raised when an equation has no solution."""

    def __init__(self, variable: str = "", message: str = "") -> None:
        self.variable = variable
        super().__init__(message or f"No solution found for variable '{variable}'")


class InfiniteSolutions(SymbolicError):
    """Raised when an equation has infinitely many solutions."""

    def __init__(self, variable: str = "", message: str = "") -> None:
        self.variable = variable
        super().__init__(message or f"Infinite solutions for variable '{variable}'")


class InvalidGeometry(SymbolicError):
    """Raised when a geometry operation receives invalid inputs."""


class DomainError(SymbolicError):
    """Raised when a value falls outside the valid domain of a function."""

    def __init__(self, function: str = "", value: object = None,
                 message: str = "") -> None:
        self.function = function
        self.value = value
        super().__init__(message or f"Domain error in '{function}'")


class RangeError(SymbolicError):
    """Raised when a result falls outside expected range."""


class InvalidExpression(SymbolicError):
    """Raised when an expression is structurally invalid."""


class ExpressionNotPolynomial(SymbolicError):
    """Raised when a polynomial operation receives a non-polynomial expression."""


class BackendNotFound(SymbolicError):
    """Raised when a requested backend is not registered."""


class PluginRegistrationError(SymbolicError):
    """Raised when plugin registration fails."""
