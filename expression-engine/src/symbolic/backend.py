from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from .expression import SymbolicExpr


class SymbolicBackend(ABC):
    """Abstract interface for a symbolic computation backend.

    Every symbolic operation in BoostAI goes through this interface.
    Future backends (SymPy, SageMath, Wolfram) implement this ABC
    without changing the rest of the system.
    """

    # ── expression operations ──────────────────────────────────────

    @abstractmethod
    def simplify(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Simplify an expression to its most compact form."""

    @abstractmethod
    def expand(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Expand products of sums and powers."""

    @abstractmethod
    def factor(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Factor an expression into irreducible factors."""

    @abstractmethod
    def substitute(self, expr: SymbolicExpr, var: str,
                   val: SymbolicExpr) -> SymbolicExpr:
        """Replace all occurrences of *var* with *val*."""

    @abstractmethod
    def collect_like_terms(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Collect and combine like terms."""

    @abstractmethod
    def evaluate(self, expr: SymbolicExpr) -> SymbolicExpr:
        """Evaluate constant sub-expressions numerically."""

    @abstractmethod
    def equals(self, a: SymbolicExpr, b: SymbolicExpr) -> bool:
        """Return True when *a* and *b* are mathematically equivalent."""

    # ── equation solving ───────────────────────────────────────────

    @abstractmethod
    def solve(self, equation: SymbolicExpr,
              variable: str) -> list[SymbolicExpr]:
        """Solve *equation* for *variable*; return list of solutions."""

    def solve_linear(self, equation: SymbolicExpr,
                     variable: str) -> list[SymbolicExpr]:
        """Solve a linear equation."""
        return self.solve(equation, variable)

    def solve_quadratic(self, equation: SymbolicExpr,
                        variable: str) -> list[SymbolicExpr]:
        """Solve a quadratic equation."""
        return self.solve(equation, variable)

    # ── polynomial operations ──────────────────────────────────────

    @abstractmethod
    def degree(self, expr: SymbolicExpr, var: str) -> int:
        """Return the degree of *expr* in *var*."""

    @abstractmethod
    def coefficients(self, expr: SymbolicExpr,
                     var: str) -> list[SymbolicExpr]:
        """Return coefficients of *expr* as a polynomial in *var*."""

    # ── fraction arithmetic ────────────────────────────────────────

    @abstractmethod
    def fraction_add(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        """Add two fractions (numerator, denominator)."""

    @abstractmethod
    def fraction_sub(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        """Subtract two fractions."""

    @abstractmethod
    def fraction_mul(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        """Multiply two fractions."""

    @abstractmethod
    def fraction_div(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        """Divide two fractions."""

    @abstractmethod
    def fraction_simplify(self, a: tuple[int | float, int | float]
                          ) -> tuple[int, int]:
        """Simplify a fraction to lowest terms."""

    # ── geometry ───────────────────────────────────────────────────

    @abstractmethod
    def distance(self, p1: tuple[float, float],
                 p2: tuple[float, float]) -> float:
        """Euclidean distance between two points."""

    @abstractmethod
    def midpoint(self, p1: tuple[float, float],
                 p2: tuple[float, float]) -> tuple[float, float]:
        """Midpoint of two points."""

    @abstractmethod
    def slope(self, p1: tuple[float, float],
              p2: tuple[float, float]) -> float:
        """Slope of the line through two points."""

    @abstractmethod
    def triangle_area(self, a: tuple[float, float],
                      b: tuple[float, float],
                      c: tuple[float, float]) -> float:
        """Area of triangle defined by three points."""

    @abstractmethod
    def circle_area(self, radius: float) -> float:
        """Area of a circle."""

    @abstractmethod
    def circle_circumference(self, radius: float) -> float:
        """Circumference of a circle."""

    @abstractmethod
    def pythagorean_hypotenuse(self, a: float, b: float) -> float:
        """Hypotenuse of a right triangle: sqrt(a^2 + b^2)."""

    @abstractmethod
    def pythagorean_leg(self, hypotenuse: float, leg: float) -> float:
        """Find a leg given hypotenuse and other leg."""

    # ── statistics ─────────────────────────────────────────────────

    @abstractmethod
    def mean(self, data: list[float]) -> float:
        """Arithmetic mean."""

    @abstractmethod
    def median(self, data: list[float]) -> float:
        """Median value."""

    @abstractmethod
    def mode(self, data: list[float]) -> list[float]:
        """Mode(s) — returns all values that appear most frequently."""

    @abstractmethod
    def data_range(self, data: list[float]) -> float:
        """Range (max - min)."""

    @abstractmethod
    def frequency(self, data: list[float]
                  ) -> dict[float, int]:
        """Frequency count of each value."""

    @abstractmethod
    def probability(self, favorable: int, total: int) -> float:
        """Probability as a value in [0, 1]."""

    @abstractmethod
    def percentage(self, value: float, total: float) -> float:
        """Value as a percentage of total."""

    # ── trigonometry ───────────────────────────────────────────────

    @abstractmethod
    def sin(self, x: float, degrees: bool = False) -> float:
        """Sine of x (radians by default)."""

    @abstractmethod
    def cos(self, x: float, degrees: bool = False) -> float:
        """Cosine of x."""

    @abstractmethod
    def tan(self, x: float, degrees: bool = False) -> float:
        """Tangent of x."""

    @abstractmethod
    def arcsin(self, x: float) -> float:
        """Inverse sine, result in radians."""

    @abstractmethod
    def arccos(self, x: float) -> float:
        """Inverse cosine, result in radians."""

    @abstractmethod
    def arctan(self, x: float) -> float:
        """Inverse tangent, result in radians."""

    @abstractmethod
    def to_degrees(self, radians: float) -> float:
        """Convert radians to degrees."""

    @abstractmethod
    def to_radians(self, degrees: float) -> float:
        """Convert degrees to radians."""

    @abstractmethod
    def normalize_angle(self, angle: float, degrees: bool = False) -> float:
        """Normalize angle to [0, 2*pi) (radians) or [0, 360) (degrees)."""

    # ── expression parsing / serialization ─────────────────────────

    @abstractmethod
    def parse(self, text: str) -> SymbolicExpr:
        """Parse a string into a SymbolicExpr."""

    @abstractmethod
    def serialize(self, expr: SymbolicExpr) -> str:
        """Serialize an expression to a string."""
