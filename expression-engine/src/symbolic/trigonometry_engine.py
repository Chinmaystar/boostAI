from __future__ import annotations

import math
from typing import Optional

from .backend import SymbolicBackend
from .exceptions import DomainError


class TrigonometryEngine:
    """Trigonometric function calculations.

    Provides sin, cos, tan, inverse functions, angle normalization,
    and degree/radian conversion.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    def sin(self, x: float, degrees: bool = False) -> float:
        return self._backend.sin(x, degrees)

    def cos(self, x: float, degrees: bool = False) -> float:
        return self._backend.cos(x, degrees)

    def tan(self, x: float, degrees: bool = False) -> float:
        return self._backend.tan(x, degrees)

    def arcsin(self, x: float) -> float:
        return self._backend.arcsin(x)

    def arccos(self, x: float) -> float:
        return self._backend.arccos(x)

    def arctan(self, x: float) -> float:
        return self._backend.arctan(x)

    def to_degrees(self, radians: float) -> float:
        return self._backend.to_degrees(radians)

    def to_radians(self, degrees: float) -> float:
        return self._backend.to_radians(degrees)

    def normalize_angle(self, angle: float, degrees: bool = False
                        ) -> float:
        return self._backend.normalize_angle(angle, degrees)

    def sin_degrees(self, x: float) -> float:
        return self.sin(x, degrees=True)

    def cos_degrees(self, x: float) -> float:
        return self.cos(x, degrees=True)

    def tan_degrees(self, x: float) -> float:
        return self.tan(x, degrees=True)

    def csc(self, x: float, degrees: bool = False) -> float:
        s = self.sin(x, degrees)
        if abs(s) < 1e-15:
            raise DomainError("csc", x, "Cosecant undefined (sin=0)")
        return 1.0 / s

    def sec(self, x: float, degrees: bool = False) -> float:
        c = self.cos(x, degrees)
        if abs(c) < 1e-15:
            raise DomainError("sec", x, "Secant undefined (cos=0)")
        return 1.0 / c

    def cot(self, x: float, degrees: bool = False) -> float:
        t = self.tan(x, degrees)
        if abs(t) < 1e-15:
            raise DomainError("cot", x, "Cotangent undefined (tan=0)")
        return 1.0 / t

    def evaluate_trig_expr(self, expr_str: str,
                           degrees: bool = False) -> float:
        """Evaluate a simple trigonometric expression string.

        Supports: sin, cos, tan, arcsin, arccos, arctan with
        numeric arguments.
        """
        import re
        expr_str = expr_str.strip().lower()
        m = re.match(r"(sin|cos|tan|arcsin|arccos|arctan)\(([^)]+)\)$",
                     expr_str)
        if not m:
            raise ValueError(f"Cannot evaluate: '{expr_str}'")
        fn_name = m.group(1)
        arg = float(m.group(2))
        fn_map = {
            "sin": lambda x: self.sin(x, degrees),
            "cos": lambda x: self.cos(x, degrees),
            "tan": lambda x: self.tan(x, degrees),
            "arcsin": self.arcsin,
            "arccos": self.arccos,
            "arctan": self.arctan,
        }
        fn = fn_map.get(fn_name)
        if fn is None:
            raise ValueError(f"Unknown function: '{fn_name}'")
        return fn(arg)
