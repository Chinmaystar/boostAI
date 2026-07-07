from .base import (
    Constraint,
    ConstraintResult,
    ConstraintMetadata,
    Severity,
    RetryReason,
)
from .result import (
    ConstraintValidationResult,
    Diagnostic,
    ValidationStats,
)
from .constraint_graph import ConstraintGraph, DependencyEdge
from .registry import ConstraintRegistry
from .validator import ConstraintValidator
from .constraints.builtins import register_builtins

# Re-export concrete constraint classes for direct use
from .constraints.arithmetic import (
    NonZeroDenominator,
    IntegerConstraint,
    PrimeNumber,
    CompositeNumber,
    PerfectSquare,
    PerfectCube,
    FactorisablePolynomial,
)
from .constraints.algebra import (
    UniqueRoots,
    IntegerSolution,
)
from .constraints.geometry import (
    PositiveRadius,
    PositiveLength,
    PositiveArea,
    TriangleInequality,
)
from .constraints.coordinate import (
    DistinctCoordinates,
    CoordinateUniqueness,
)
from .constraints.statistics import (
    ProbabilityRange,
    PercentageRange,
)
from .constraints.graph_ import (
    GraphBounds,
    AxisLimits,
    Monotonicity,
)
from .constraints.domain import (
    DomainRestrictions,
    RangeRestrictions,
    DuplicateVariablePrevention,
    ExpressionValidity,
)

__all__ = [
    "Constraint",
    "ConstraintResult",
    "ConstraintMetadata",
    "Severity",
    "RetryReason",
    "ConstraintValidationResult",
    "Diagnostic",
    "ValidationStats",
    "ConstraintGraph",
    "DependencyEdge",
    "ConstraintRegistry",
    "ConstraintValidator",
    "register_builtins",
    # Arithmetic
    "NonZeroDenominator",
    "IntegerConstraint",
    "PrimeNumber",
    "CompositeNumber",
    "PerfectSquare",
    "PerfectCube",
    "FactorisablePolynomial",
    # Algebra
    "UniqueRoots",
    "IntegerSolution",
    # Geometry
    "PositiveRadius",
    "PositiveLength",
    "PositiveArea",
    "TriangleInequality",
    # Coordinate
    "DistinctCoordinates",
    "CoordinateUniqueness",
    # Statistics
    "ProbabilityRange",
    "PercentageRange",
    # Graph
    "GraphBounds",
    "AxisLimits",
    "Monotonicity",
    # Domain
    "DomainRestrictions",
    "RangeRestrictions",
    "DuplicateVariablePrevention",
    "ExpressionValidity",
]
