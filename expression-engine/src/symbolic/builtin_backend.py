from __future__ import annotations

import math
import re
import fractions
from typing import Any, Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr, ExprType
from .exceptions import (
    DivisionByZero, UnsupportedOperation, NoSolution,
    InfiniteSolutions, InvalidGeometry, DomainError,
    ExpressionNotPolynomial, InvalidExpression,
)


_EXPR_CACHE: dict[str, SymbolicExpr] = {}

_ADD_EVAL = frozenset({ExprType.NUMBER, ExprType.SYMBOL, ExprType.NEG})
_MUL_EVAL = frozenset({ExprType.NUMBER, ExprType.SYMBOL, ExprType.NEG,
                       ExprType.POW})


def _gcd(a: int, b: int) -> int:
    return math.gcd(a, b)


def _reduce_fraction(n: int, d: int) -> tuple[int, int]:
    if d == 0:
        raise DivisionByZero("Fraction denominator is zero")
    if d < 0:
        n, d = -n, -d
    g = _gcd(abs(n), abs(d))
    return n // g, d // g


class BuiltinBackend(SymbolicBackend):
    """Pure-Python implementation of SymbolicBackend.

    This backend performs all symbolic operations using only the Python
    standard library.  It is the default backend for BoostAI.
    """

    # ── expression operations ──────────────────────────────────────

    def simplify(self, expr: SymbolicExpr) -> SymbolicExpr:
        return self._simplify(expr)

    def _simplify(self, expr: SymbolicExpr, _neg: bool = False) -> SymbolicExpr:
        """Recursive simplification with sign tracking."""
        tp = expr.type

        if tp is ExprType.NUMBER:
            return SymbolicExpr.number(-expr.value if _neg else expr.value)

        if tp is ExprType.SYMBOL:
            return SymbolicExpr.symbol("-" + expr.value if _neg else expr.value)

        if tp is ExprType.NEG:
            return self._simplify(expr.operand(), not _neg)

        if tp is ExprType.ADD:
            left = self._simplify(expr.left(), _neg)
            right = self._simplify(expr.right(), _neg)
            if left.is_number() and right.is_number():
                return SymbolicExpr.number(left.value + right.value)
            if left.is_number() and left.value == 0:
                return right
            if right.is_number() and right.value == 0:
                return left
            if left == right:
                return SymbolicExpr.mul(SymbolicExpr.number(2), left)
            return SymbolicExpr.add(left, right)

        if tp is ExprType.SUB:
            left = self._simplify(expr.left(), _neg)
            right = self._simplify(expr.right(), _neg)
            if left.is_number() and right.is_number():
                return SymbolicExpr.number(left.value - right.value)
            if right.is_number() and right.value == 0:
                return left
            return SymbolicExpr.sub(left, right)

        if tp is ExprType.MUL:
            children = [self._simplify(c, _neg) for c in expr.children]
            const_val = 1.0
            var_parts: list[SymbolicExpr] = []
            for c in children:
                if c.is_number():
                    const_val *= c.value
                else:
                    var_parts.append(c)
            if const_val == 0:
                return SymbolicExpr.number(-0.0 if _neg else 0.0)
            parts: list[SymbolicExpr] = []
            if const_val != 1 or (not var_parts):
                parts.append(SymbolicExpr.number(-const_val if _neg else const_val))
            parts.extend(var_parts)
            if not parts:
                return SymbolicExpr.number(1)
            result = parts[0]
            for p in parts[1:]:
                result = SymbolicExpr.mul(result, p)
            return result

        if tp is ExprType.DIV:
            left = self._simplify(expr.left(), _neg)
            right = self._simplify(expr.right(), _neg)
            if right.is_number() and right.value == 0:
                raise DivisionByZero("Division by zero")
            if left.is_number() and right.is_number():
                return SymbolicExpr.number(left.value / right.value)
            if right.is_number() and right.value == 1:
                return left
            return SymbolicExpr.div(left, right)

        if tp is ExprType.POW:
            base = self._simplify(expr.left(), _neg)
            exp = self._simplify(expr.right())
            if base.is_number() and exp.is_number():
                try:
                    return SymbolicExpr.number(base.value ** exp.value)
                except OverflowError:
                    return SymbolicExpr.pow(base, exp)
            if exp.is_number() and exp.value == 0:
                return SymbolicExpr.number(1)
            if exp.is_number() and exp.value == 1:
                return base
            return SymbolicExpr.pow(base, exp)

        if tp is ExprType.SQRT:
            arg = self._simplify(expr.operand())
            if arg.is_number():
                if arg.value < 0:
                    raise DomainError("sqrt", arg.value,
                                      "Square root of negative number")
                return SymbolicExpr.number(math.sqrt(arg.value))
            return SymbolicExpr.sqrt(arg)

        if tp is ExprType.ABS:
            arg = self._simplify(expr.operand())
            if arg.is_number():
                return SymbolicExpr.number(abs(arg.value))
            return SymbolicExpr.abs(arg)

        if tp in (ExprType.SIN, ExprType.COS, ExprType.TAN,
                  ExprType.ARCSIN, ExprType.ARCCOS, ExprType.ARCTAN):
            arg = self._simplify(expr.operand())
            if arg.is_number():
                fn_name = tp.name.lower()
                fn = getattr(math, fn_name, None)
                if fn:
                    return SymbolicExpr.number(fn(arg.value))
            return SymbolicExpr(tp, children=(arg,))

        if tp is ExprType.EQUAL:
            return SymbolicExpr.equal(
                self._simplify(expr.left(), _neg),
                self._simplify(expr.right(), _neg),
            )

        if tp is ExprType.FRACTION:
            n, d = expr.value
            if d == 0:
                raise DivisionByZero("Fraction denominator is zero")
            rn, rd = _reduce_fraction(int(n), int(d))
            return SymbolicExpr.fraction(rn, rd)

        return expr

    def expand(self, expr: SymbolicExpr) -> SymbolicExpr:
        return self._expand(self._simplify(expr))

    def _expand(self, expr: SymbolicExpr) -> SymbolicExpr:
        tp = expr.type

        if tp is ExprType.NUMBER or tp is ExprType.SYMBOL:
            return expr

        if tp is ExprType.NEG:
            return SymbolicExpr.neg(self._expand(expr.operand()))

        if tp is ExprType.ADD:
            return SymbolicExpr.add(
                self._expand(expr.left()),
                self._expand(expr.right()),
            )

        if tp is ExprType.SUB:
            return SymbolicExpr.sub(
                self._expand(expr.left()),
                self._expand(expr.right()),
            )

        if tp is ExprType.MUL:
            left = self._expand(expr.left())
            right = self._expand(expr.right())
            if left.is_add():
                a, b = left.left(), left.right()
                return self._expand(SymbolicExpr.add(
                    SymbolicExpr.mul(a, right),
                    SymbolicExpr.mul(b, right),
                ))
            if right.is_add():
                a, b = right.left(), right.right()
                return self._expand(SymbolicExpr.add(
                    SymbolicExpr.mul(left, a),
                    SymbolicExpr.mul(left, b),
                ))
            return SymbolicExpr.mul(left, right)

        if tp is ExprType.DIV:
            return SymbolicExpr.div(
                self._expand(expr.left()),
                self._expand(expr.right()),
            )

        if tp is ExprType.POW:
            base = self._expand(expr.left())
            exp = self._simplify(expr.right())
            if exp.is_number() and exp.value == 2 and base.is_add():
                a, b = base.left(), base.right()
                return self._expand(SymbolicExpr.add(
                    self._expand(SymbolicExpr.pow(a, SymbolicExpr.number(2))),
                    self._expand(SymbolicExpr.add(
                        SymbolicExpr.mul(SymbolicExpr.number(2),
                                         SymbolicExpr.mul(a, b)),
                        SymbolicExpr.pow(b, SymbolicExpr.number(2)),
                    )),
                ))
            return SymbolicExpr.pow(base, exp)

        return expr

    def factor(self, expr: SymbolicExpr) -> SymbolicExpr:
        return self._factor(self._simplify(expr))

    def _factor(self, expr: SymbolicExpr) -> SymbolicExpr:
        tp = expr.type

        if tp is ExprType.NUMBER or tp is ExprType.SYMBOL:
            return expr

        if tp is ExprType.ADD:
            left = self._factor(expr.left())
            right = self._factor(expr.right())
            return SymbolicExpr.add(left, right)

        if tp is ExprType.MUL:
            return SymbolicExpr.mul(
                self._factor(expr.left()),
                self._factor(expr.right()),
            )

        return expr

    def substitute(self, expr: SymbolicExpr, var: str,
                   val: SymbolicExpr) -> SymbolicExpr:
        return self._substitute(expr, var, val)

    def _substitute(self, expr: SymbolicExpr, var: str,
                    val: SymbolicExpr) -> SymbolicExpr:
        if expr.is_symbol() and expr.value == var:
            return val
        if not expr.children:
            return expr
        return SymbolicExpr(expr.type, expr.value,
                            tuple(self._substitute(c, var, val)
                                  for c in expr.children))

    def collect_like_terms(self, expr: SymbolicExpr) -> SymbolicExpr:
        return self._collect(self._simplify(expr))

    def _collect(self, expr: SymbolicExpr) -> SymbolicExpr:
        tp = expr.type

        if tp in (ExprType.NUMBER, ExprType.SYMBOL):
            return expr

        if tp is ExprType.ADD:
            left = self._collect(expr.left())
            right = self._collect(expr.right())
            terms: dict[str, list[float]] = {"_const": []}
            for term in self._flatten_add(SymbolicExpr.add(left, right)):
                coeff, var_part = self._split_term(term)
                key = var_part or "_const"
                terms.setdefault(key, []).append(coeff)
            collected_parts: list[SymbolicExpr] = []
            for key, coeffs in terms.items():
                total = sum(coeffs)
                if total == 0:
                    continue
                if key == "_const":
                    collected_parts.append(SymbolicExpr.number(total))
                elif total == 1:
                    collected_parts.append(self._parse_var_part(key))
                elif total == -1:
                    collected_parts.append(
                        SymbolicExpr.neg(self._parse_var_part(key)))
                else:
                    collected_parts.append(
                        SymbolicExpr.mul(SymbolicExpr.number(total),
                                         self._parse_var_part(key)))
            if not collected_parts:
                return SymbolicExpr.number(0)
            result = collected_parts[0]
            for p in collected_parts[1:]:
                result = SymbolicExpr.add(result, p)
            return self._simplify(result)

        if tp is ExprType.SUB:
            return self._collect(SymbolicExpr.add(expr.left(),
                                                  SymbolicExpr.neg(expr.right())))

        return expr

    def _flatten_add(self, expr: SymbolicExpr) -> list[SymbolicExpr]:
        """Flatten nested ADD into a list of terms."""
        if expr.type is ExprType.ADD:
            return (self._flatten_add(expr.left())
                    + self._flatten_add(expr.right()))
        if expr.type is ExprType.SUB:
            return (self._flatten_add(expr.left())
                    + [SymbolicExpr.neg(expr.right())])
        return [expr]

    def _split_term(self, term: SymbolicExpr) -> tuple[float, str]:
        """Split a term into (coefficient, variable_part_string)."""
        if term.is_neg():
            coeff, var_part = self._split_term(term.operand())
            return -coeff, var_part
        term = self._simplify(term)
        if term.is_number():
            return term.value, ""
        if term.is_symbol():
            return 1.0, term.value
        if term.type is ExprType.MUL:
            left, right = term.left(), term.right()
            if left.is_number():
                return left.value, self._var_part_str(right)
            if right.is_number():
                return right.value, self._var_part_str(left)
            return 1.0, self._var_part_str(term)
        return 1.0, self._var_part_str(term)

    def _var_part_str(self, expr: SymbolicExpr) -> str:
        if expr.is_symbol():
            return expr.value
        if expr.type is ExprType.MUL:
            return f"({self._var_part_str(expr.left())}*{self._var_part_str(expr.right())})"
        if expr.type is ExprType.POW:
            return f"({self._var_part_str(expr.left())}^{self._var_part_str(expr.right())})"
        return str(expr)

    def _parse_var_part(self, s: str) -> SymbolicExpr:
        return SymbolicExpr.symbol(s)

    def evaluate(self, expr: SymbolicExpr) -> SymbolicExpr:
        return self._simplify(expr)

    def equals(self, a: SymbolicExpr, b: SymbolicExpr) -> bool:
        sa = self._simplify(a)
        sb = self._simplify(b)
        return sa == sb

    # ── equation solving ───────────────────────────────────────────

    def solve(self, equation: SymbolicExpr,
              variable: str) -> list[SymbolicExpr]:
        if not equation.is_equal():
            raise InvalidExpression("solve() requires an EQUAL expression")
        lhs = self._simplify(equation.left())
        rhs = self._simplify(equation.right())

        expr = self._simplify(SymbolicExpr.sub(lhs, rhs))

        deg = self._degree(expr, variable)
        if deg == 0:
            if self._simplify(expr).is_number() and expr.value == 0:
                raise InfiniteSolutions(variable)
            return []
        if deg == 1:
            return self._solve_linear(expr, variable)
        if deg == 2:
            return self._solve_quadratic(expr, variable)
        raise UnsupportedOperation(
            f"Solving degree-{deg} polynomials is not supported")

    def _solve_linear(self, expr: SymbolicExpr,
                      variable: str) -> list[SymbolicExpr]:
        coeffs = self._coefficients(expr, variable)
        if len(coeffs) < 2:
            return []
        a = coeffs[1]
        b = coeffs[0] if len(coeffs) > 0 else SymbolicExpr.number(0)
        if a.is_number() and a.value == 0:
            if b.is_number() and b.value == 0:
                raise InfiniteSolutions(variable)
            return []
        if a.is_number() and b.is_number():
            return [SymbolicExpr.number(-b.value / a.value)]
        return [SymbolicExpr.div(SymbolicExpr.neg(b), a)]

    def _solve_quadratic(self, expr: SymbolicExpr,
                         variable: str) -> list[SymbolicExpr]:
        coeffs = self._coefficients(expr, variable)
        if len(coeffs) < 3:
            return self._solve_linear(expr, variable)
        a = coeffs[2]
        b = coeffs[1] if len(coeffs) > 1 else SymbolicExpr.number(0)
        c = coeffs[0] if len(coeffs) > 0 else SymbolicExpr.number(0)

        if not (a.is_number() and b.is_number() and c.is_number()):
            raise UnsupportedOperation(
                "Quadratic solving requires numeric coefficients")
        av, bv, cv = a.value, b.value, c.value
        discriminant = bv * bv - 4 * av * cv
        if discriminant < 0:
            return []
        if discriminant == 0:
            return [SymbolicExpr.number(-bv / (2 * av))]
        sd = math.sqrt(discriminant)
        return [
            SymbolicExpr.number((-bv + sd) / (2 * av)),
            SymbolicExpr.number((-bv - sd) / (2 * av)),
        ]

    def degree(self, expr: SymbolicExpr, var: str) -> int:
        return self._degree(self._simplify(expr), var)

    def _degree(self, expr: SymbolicExpr, var: str) -> int:
        tp = expr.type
        if tp is ExprType.NUMBER:
            return 0
        if tp is ExprType.SYMBOL:
            return 1 if expr.value == var else 0
        if tp is ExprType.NEG:
            return self._degree(expr.operand(), var)
        if tp is ExprType.ADD or tp is ExprType.SUB:
            return max(self._degree(c, var) for c in expr.children)
        if tp is ExprType.MUL:
            return sum(self._degree(c, var) for c in expr.children)
        if tp is ExprType.DIV:
            deg_num = self._degree(expr.left(), var)
            deg_den = self._degree(expr.right(), var)
            if deg_den > 0:
                return -1
            return deg_num
        if tp is ExprType.POW:
            base_deg = self._degree(expr.left(), var)
            exp = self._simplify(expr.right())
            if exp.is_number() and exp.value == int(exp.value):
                return base_deg * int(exp.value)
            return -1
        return -1

    def coefficients(self, expr: SymbolicExpr,
                     var: str) -> list[SymbolicExpr]:
        return self._coefficients(self._simplify(expr), var)

    def _coefficients(self, expr: SymbolicExpr,
                      var: str) -> list[SymbolicExpr]:
        deg = self._degree(expr, var)
        if deg < 0:
            raise ExpressionNotPolynomial(
                f"Expression is not a polynomial in '{var}'")
        if deg == 0:
            return [self._simplify(expr)]

        terms = self._flatten_add(expr)
        coeffs: dict[int, float] = {}
        for term in terms:
            term_deg = self._degree(term, var)
            coeff, _ = self._split_term(term)
            coeffs[term_deg] = coeffs.get(term_deg, 0) + coeff

        result: list[SymbolicExpr] = []
        for d in range(deg + 1):
            result.append(SymbolicExpr.number(coeffs.get(d, 0.0)))
        return result

    # ── fraction arithmetic ────────────────────────────────────────

    def fraction_add(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        an, ad = int(a[0]), int(a[1])
        bn, bd = int(b[0]), int(b[1])
        if ad == 0 or bd == 0:
            raise DivisionByZero("Fraction denominator is zero")
        n = an * bd + bn * ad
        d = ad * bd
        return _reduce_fraction(n, d)

    def fraction_sub(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        an, ad = int(a[0]), int(a[1])
        bn, bd = int(b[0]), int(b[1])
        if ad == 0 or bd == 0:
            raise DivisionByZero("Fraction denominator is zero")
        n = an * bd - bn * ad
        d = ad * bd
        return _reduce_fraction(n, d)

    def fraction_mul(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        an, ad = int(a[0]), int(a[1])
        bn, bd = int(b[0]), int(b[1])
        if ad == 0 or bd == 0:
            raise DivisionByZero("Fraction denominator is zero")
        n = an * bn
        d = ad * bd
        return _reduce_fraction(n, d)

    def fraction_div(self, a: tuple[int | float, int | float],
                     b: tuple[int | float, int | float]
                     ) -> tuple[int, int]:
        an, ad = int(a[0]), int(a[1])
        bn, bd = int(b[0]), int(b[1])
        if ad == 0 or bn == 0 or bd == 0:
            raise DivisionByZero("Fraction division by zero")
        n = an * bd
        d = ad * bn
        return _reduce_fraction(n, d)

    def fraction_simplify(self, a: tuple[int | float, int | float]
                          ) -> tuple[int, int]:
        return _reduce_fraction(int(a[0]), int(a[1]))

    # ── geometry ───────────────────────────────────────────────────

    def distance(self, p1: tuple[float, float],
                 p2: tuple[float, float]) -> float:
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def midpoint(self, p1: tuple[float, float],
                 p2: tuple[float, float]) -> tuple[float, float]:
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    def slope(self, p1: tuple[float, float],
              p2: tuple[float, float]) -> float:
        dx = p2[0] - p1[0]
        if dx == 0:
            raise InvalidGeometry("Slope is undefined (vertical line)")
        return (p2[1] - p1[1]) / dx

    def triangle_area(self, a: tuple[float, float],
                      b: tuple[float, float],
                      c: tuple[float, float]) -> float:
        return abs((a[0] * (b[1] - c[1])
                    + b[0] * (c[1] - a[1])
                    + c[0] * (a[1] - b[1])) / 2.0)

    def circle_area(self, radius: float) -> float:
        if radius < 0:
            raise InvalidGeometry("Radius cannot be negative")
        return math.pi * radius * radius

    def circle_circumference(self, radius: float) -> float:
        if radius < 0:
            raise InvalidGeometry("Radius cannot be negative")
        return 2 * math.pi * radius

    def pythagorean_hypotenuse(self, a: float, b: float) -> float:
        if a < 0 or b < 0:
            raise InvalidGeometry("Leg lengths cannot be negative")
        return math.sqrt(a * a + b * b)

    def pythagorean_leg(self, hypotenuse: float, leg: float) -> float:
        if hypotenuse <= 0 or leg <= 0:
            raise InvalidGeometry("Lengths must be positive")
        if leg >= hypotenuse:
            raise InvalidGeometry("Leg must be shorter than hypotenuse")
        return math.sqrt(hypotenuse * hypotenuse - leg * leg)

    # ── statistics ─────────────────────────────────────────────────

    def mean(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute mean of empty list")
        return sum(data) / len(data)

    def median(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute median of empty list")
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 1:
            return sorted_data[mid]
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0

    def mode(self, data: list[float]) -> list[float]:
        if not data:
            raise ValueError("Cannot compute mode of empty list")
        freq: dict[float, int] = {}
        for v in data:
            freq[v] = freq.get(v, 0) + 1
        max_freq = max(freq.values())
        return sorted([k for k, v in freq.items() if v == max_freq])

    def data_range(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute range of empty list")
        return max(data) - min(data)

    def frequency(self, data: list[float]) -> dict[float, int]:
        freq: dict[float, int] = {}
        for v in data:
            freq[v] = freq.get(v, 0) + 1
        return dict(sorted(freq.items()))

    def probability(self, favorable: int, total: int) -> float:
        if total <= 0:
            raise ValueError("Total must be positive")
        if favorable < 0 or favorable > total:
            raise ValueError(
                "Favorable count must be between 0 and total")
        return favorable / total

    def percentage(self, value: float, total: float) -> float:
        if total == 0:
            raise ValueError("Total cannot be zero")
        return (value / total) * 100.0

    # ── trigonometry ───────────────────────────────────────────────

    def sin(self, x: float, degrees: bool = False) -> float:
        return math.sin(math.radians(x) if degrees else x)

    def cos(self, x: float, degrees: bool = False) -> float:
        return math.cos(math.radians(x) if degrees else x)

    def tan(self, x: float, degrees: bool = False) -> float:
        rad = math.radians(x) if degrees else x
        return math.tan(rad)

    def arcsin(self, x: float) -> float:
        if x < -1 or x > 1:
            raise DomainError("arcsin", x,
                              "arcsin domain is [-1, 1]")
        return math.asin(x)

    def arccos(self, x: float) -> float:
        if x < -1 or x > 1:
            raise DomainError("arccos", x,
                              "arccos domain is [-1, 1]")
        return math.acos(x)

    def arctan(self, x: float) -> float:
        return math.atan(x)

    def to_degrees(self, radians: float) -> float:
        return math.degrees(radians)

    def to_radians(self, degrees: float) -> float:
        return math.radians(degrees)

    def normalize_angle(self, angle: float, degrees: bool = False) -> float:
        if degrees:
            return angle % 360.0
        return angle % (2 * math.pi)

    # ── expression parsing / serialization ─────────────────────────

    def parse(self, text: str) -> SymbolicExpr:
        cached = _EXPR_CACHE.get(text)
        if cached is not None:
            return cached
        result = self._parse(text)
        _EXPR_CACHE[text] = result
        return result

    _TOKEN_PAT = re.compile(r"""
        (\d+\.?\d*|[a-zA-Z_]\w*|
         \+ | \- | \* | / | \*\* | \^ |
         \( | \) | = |
         sin | cos | tan | sqrt | abs |
         , )
    """, re.VERBOSE)

    def _parse(self, text: str) -> SymbolicExpr:
        tokens = [t for t in self._TOKEN_PAT.findall(text) if t.strip()]
        self._pos = 0
        self._tokens = tokens
        result = self._parse_expression()
        if self._pos < len(self._tokens):
            raise InvalidExpression(
                f"Unexpected tokens after expression: "
                f"{' '.join(self._tokens[self._pos:])}")
        return result

    def _peek(self) -> str | None:
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    def _consume(self, expected: str | None = None) -> str:
        if self._pos >= len(self._tokens):
            raise InvalidExpression("Unexpected end of expression")
        token = self._tokens[self._pos]
        if expected is not None and token != expected:
            raise InvalidExpression(
                f"Expected '{expected}', got '{token}'")
        self._pos += 1
        return token

    def _parse_expression(self) -> SymbolicExpr:
        result = self._parse_term()
        while self._peek() in ("+", "-"):
            op = self._consume()
            right = self._parse_term()
            if op == "+":
                result = SymbolicExpr.add(result, right)
            else:
                result = SymbolicExpr.sub(result, right)
        if self._peek() == "=":
            self._consume("=")
            right = self._parse_expression()
            result = SymbolicExpr.equal(result, right)
        return result

    def _parse_term(self) -> SymbolicExpr:
        result = self._parse_factor()
        while self._peek() in ("*", "/"):
            op = self._consume()
            right = self._parse_factor()
            if op == "*":
                result = SymbolicExpr.mul(result, right)
            else:
                result = SymbolicExpr.div(result, right)
        return result

    def _parse_factor(self) -> SymbolicExpr:
        token = self._peek()
        if token is None:
            raise InvalidExpression("Unexpected end of expression")

        if token == "(":
            self._consume("(")
            result = self._parse_expression()
            self._consume(")")
            return result

        if token == "-":
            self._consume("-")
            return SymbolicExpr.neg(self._parse_factor())

        if token in ("sin", "cos", "tan", "sqrt", "abs"):
            return self._parse_function(token)

        if token.replace(".", "", 1).isdigit():
            self._consume()
            return SymbolicExpr.number(float(token))

        if re.match(r"[a-zA-Z_]\w*$", token):
            self._consume()
            if self._peek() == "(":
                return self._parse_function(token)
            return SymbolicExpr.symbol(token)

        raise InvalidExpression(f"Unexpected token: '{token}'")

    def _parse_function(self, name: str) -> SymbolicExpr:
        self._consume(name)
        self._consume("(")
        arg = self._parse_expression()
        self._consume(")")
        fn_map = {
            "sin": SymbolicExpr.sin,
            "cos": SymbolicExpr.cos,
            "tan": SymbolicExpr.tan,
            "sqrt": SymbolicExpr.sqrt,
            "abs": SymbolicExpr.abs,
        }
        maker = fn_map.get(name)
        if maker is None:
            raise InvalidExpression(f"Unknown function: '{name}'")
        return maker(arg)

    def serialize(self, expr: SymbolicExpr) -> str:
        from .visitor import ToStringVisitor
        return ToStringVisitor().visit(expr)
