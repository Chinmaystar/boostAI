from __future__ import annotations

import math
from typing import Optional

from .backend import SymbolicBackend
from .exceptions import InvalidGeometry


class Point:
    """A 2D point."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


class Line:
    """A line defined by two points."""

    def __init__(self, p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2

    def slope(self) -> float:
        dx = self.p2.x - self.p1.x
        if dx == 0:
            raise InvalidGeometry("Slope is undefined (vertical line)")
        return (self.p2.y - self.p1.y) / dx

    def length(self) -> float:
        return math.sqrt(
            (self.p2.x - self.p1.x) ** 2
            + (self.p2.y - self.p1.y) ** 2
        )

    def midpoint(self) -> Point:
        return Point(
            (self.p1.x + self.p2.x) / 2,
            (self.p1.y + self.p2.y) / 2,
        )

    def is_vertical(self) -> bool:
        return abs(self.p2.x - self.p1.x) < 1e-12

    def is_horizontal(self) -> bool:
        return abs(self.p2.y - self.p1.y) < 1e-12

    def __repr__(self) -> str:
        return f"Line({self.p1}, {self.p2})"


class Triangle:
    """A triangle defined by three points."""

    def __init__(self, a: Point, b: Point, c: Point) -> None:
        self.a = a
        self.b = b
        self.c = c

    def area(self) -> float:
        return abs(
            (self.a.x * (self.b.y - self.c.y)
             + self.b.x * (self.c.y - self.a.y)
             + self.c.x * (self.a.y - self.b.y))
            / 2.0
        )

    def side_lengths(self) -> tuple[float, float, float]:
        ab = Line(self.a, self.b).length()
        bc = Line(self.b, self.c).length()
        ca = Line(self.c, self.a).length()
        return (ab, bc, ca)

    def is_valid(self) -> bool:
        s1, s2, s3 = self.side_lengths()
        return (s1 + s2 > s3 and s2 + s3 > s1 and s3 + s1 > s2
                and self.area() > 0)

    def perimeter(self) -> float:
        return sum(self.side_lengths())

    def __repr__(self) -> str:
        return f"Triangle({self.a}, {self.b}, {self.c})"


class Circle:
    """A circle defined by a center point and radius."""

    def __init__(self, center: Point, radius: float) -> None:
        if radius < 0:
            raise InvalidGeometry("Radius cannot be negative")
        self.center = center
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius * self.radius

    def circumference(self) -> float:
        return 2 * math.pi * self.radius

    def diameter(self) -> float:
        return 2 * self.radius

    def contains_point(self, p: Point) -> bool:
        dist = math.sqrt(
            (p.x - self.center.x) ** 2
            + (p.y - self.center.y) ** 2
        )
        return dist <= self.radius + 1e-12

    def __repr__(self) -> str:
        return f"Circle(center={self.center}, radius={self.radius})"


class GeometryEngine:
    """Geometry calculations and validation.

    Provides distance, midpoint, slope, triangle area, circle area,
    circle circumference, angles, Pythagoras, coordinate geometry,
    and geometry validation.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    # ── coordinate geometry ─────────────────────────────────────

    def distance(self, p1: tuple[float, float],
                 p2: tuple[float, float]) -> float:
        return self._backend.distance(p1, p2)

    def midpoint(self, p1: tuple[float, float],
                 p2: tuple[float, float]) -> tuple[float, float]:
        return self._backend.midpoint(p1, p2)

    def slope(self, p1: tuple[float, float],
              p2: tuple[float, float]) -> float:
        return self._backend.slope(p1, p2)

    def distance_between_points(self, a: Point, b: Point) -> float:
        return self.distance(a.as_tuple(), b.as_tuple())

    # ── triangle geometry ───────────────────────────────────────

    def triangle_area(self, a: tuple[float, float],
                      b: tuple[float, float],
                      c: tuple[float, float]) -> float:
        return self._backend.triangle_area(a, b, c)

    def triangle_is_valid(self, a: tuple[float, float],
                          b: tuple[float, float],
                          c: tuple[float, float]) -> bool:
        tri = Triangle(Point(*a), Point(*b), Point(*c))
        return tri.is_valid()

    # ── circle geometry ─────────────────────────────────────────

    def circle_area(self, radius: float) -> float:
        return self._backend.circle_area(radius)

    def circle_circumference(self, radius: float) -> float:
        return self._backend.circle_circumference(radius)

    # ── Pythagoras ──────────────────────────────────────────────

    def pythagorean_hypotenuse(self, a: float, b: float) -> float:
        return self._backend.pythagorean_hypotenuse(a, b)

    def pythagorean_leg(self, hypotenuse: float, leg: float) -> float:
        return self._backend.pythagorean_leg(hypotenuse, leg)

    # ── angles ──────────────────────────────────────────────────

    def angle_between(self, p1: tuple[float, float],
                      p2: tuple[float, float],
                      p3: tuple[float, float]) -> float:
        """Angle at p2 formed by vectors p2→p1 and p2→p3 (radians)."""
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
        if mag1 == 0 or mag2 == 0:
            raise InvalidGeometry("Zero-length vector in angle calculation")
        cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return math.acos(cos_angle)

    # ── validation ──────────────────────────────────────────────

    def validate_triangle(self, sides: tuple[float, float, float]
                          ) -> bool:
        """Triangle inequality: each side < sum of other two."""
        a, b, c = sides
        return (a + b > c and b + c > a and c + a > b)

    def collinear(self, p1: tuple[float, float],
                  p2: tuple[float, float],
                  p3: tuple[float, float]) -> bool:
        """Check if three points are collinear."""
        area = self.triangle_area(p1, p2, p3)
        return area < 1e-12
