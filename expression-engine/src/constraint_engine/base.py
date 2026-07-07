from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RetryReason(Enum):
    NONE = "none"
    ZERO_DENOMINATOR = "zero_denominator"
    NEGATIVE_RADIUS = "negative_radius"
    NEGATIVE_LENGTH = "negative_length"
    NEGATIVE_AREA = "negative_area"
    INVALID_TRIANGLE = "invalid_triangle"
    NON_INTEGER_SOLUTION = "non_integer_solution"
    OUT_OF_RANGE = "out_of_range"
    DUPLICATE_POINT = "duplicate_point"
    INVALID_COORDINATE = "invalid_coordinate"
    INVALID_PROBABILITY = "invalid_probability"
    INVALID_PERCENTAGE = "invalid_percentage"
    NOT_PRIME = "not_prime"
    NOT_COMPOSITE = "not_composite"
    NOT_PERFECT_SQUARE = "not_perfect_square"
    NOT_PERFECT_CUBE = "not_perfect_cube"
    NOT_FACTORISABLE = "not_factorisable"
    NON_UNIQUE_ROOT = "non_unique_root"
    GRAPH_BOUNDS_EXCEEDED = "graph_bounds_exceeded"
    INVALID_AXIS_LIMITS = "invalid_axis_limits"
    NON_MONOTONIC = "non_monotonic"
    DOMAIN_VIOLATION = "domain_violation"
    RANGE_VIOLATION = "range_violation"
    DUPLICATE_VARIABLE = "duplicate_variable"
    INVALID_EXPRESSION = "invalid_expression"
    CONSTRAINT_VIOLATION = "constraint_violation"


@dataclass(frozen=True)
class ConstraintMetadata:
    id: str
    name: str
    description: str
    domain: str
    version: str = "1.0.0"
    priority: int = 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "version": self.version,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class ConstraintResult:
    constraint_id: str
    passed: bool
    severity: Severity = Severity.ERROR
    retry_reason: RetryReason = RetryReason.NONE
    variables_involved: tuple[str, ...] = ()
    expected_condition: str = ""
    actual_values: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "constraint_id": self.constraint_id,
            "passed": self.passed,
            "severity": self.severity.value,
            "retry_reason": self.retry_reason.value,
            "variables_involved": list(self.variables_involved),
            "expected_condition": self.expected_condition,
            "actual_values": self.actual_values,
            "message": self.message,
        }


class Constraint(ABC):
    @property
    @abstractmethod
    def metadata(self) -> ConstraintMetadata:
        ...

    @abstractmethod
    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        ...

    def describe(self) -> str:
        return self.metadata.description

    def severity(self) -> Severity:
        return Severity.ERROR

    def dependencies(self) -> list[str]:
        return []
