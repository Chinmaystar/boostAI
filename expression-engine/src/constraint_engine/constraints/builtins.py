from __future__ import annotations

from ..base import Constraint
from ..registry import ConstraintRegistry
from .arithmetic import (
    NonZeroDenominator,
    IntegerConstraint,
    PrimeNumber,
    CompositeNumber,
    PerfectSquare,
    PerfectCube,
    FactorisablePolynomial,
)
from .algebra import (
    UniqueRoots,
    IntegerSolution,
)
from .geometry import (
    PositiveRadius,
    PositiveLength,
    PositiveArea,
    TriangleInequality,
)
from .coordinate import (
    DistinctCoordinates,
    CoordinateUniqueness,
)
from .statistics import (
    ProbabilityRange,
    PercentageRange,
)
from .graph_ import (
    GraphBounds,
    AxisLimits,
    Monotonicity,
)
from .domain import (
    DomainRestrictions,
    RangeRestrictions,
    DuplicateVariablePrevention,
    ExpressionValidity,
)


def register_builtins(registry: ConstraintRegistry) -> int:
    """Register all built-in constraints into the given registry.

    Args:
        registry: A ``ConstraintRegistry`` instance.

    Returns:
        The number of constraints registered.
    """
    constraints: list[Constraint] = [
        # Arithmetic
        NonZeroDenominator(),
        IntegerConstraint(),
        PrimeNumber(),
        CompositeNumber(),
        PerfectSquare(),
        PerfectCube(),
        FactorisablePolynomial(),
        # Algebra
        UniqueRoots(),
        IntegerSolution(),
        # Geometry
        PositiveRadius(),
        PositiveLength(),
        PositiveArea(),
        TriangleInequality(),
        # Coordinate
        DistinctCoordinates(),
        CoordinateUniqueness(),
        # Statistics
        ProbabilityRange(),
        PercentageRange(),
        # Graph
        GraphBounds(),
        AxisLimits(),
        Monotonicity(),
        # Domain
        DomainRestrictions(),
        RangeRestrictions(),
        DuplicateVariablePrevention(),
        ExpressionValidity(),
    ]
    return registry.register_many(constraints)
