from __future__ import annotations

from typing import Any

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class DistinctCoordinates(Constraint):
    _metadata = ConstraintMetadata(
        id="distinct_coordinates",
        name="Distinct Coordinates",
        description="All coordinates must be distinct",
        domain="coordinate",
    )

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        from src.variable_engine import VariableType
        graph = variable_graph
        points: list[tuple[str, Any]] = []

        for v in graph.all_nodes():
            if v.type in (VariableType.POINT, VariableType.COORDINATE):
                val = variable_values.get(v.id)
                if val is not None:
                    points.append((v.id, val))

        seen = set()
        for vid, val in points:
            key = tuple(val) if isinstance(val, (list, tuple)) else val
            if key in seen:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.DUPLICATE_POINT,
                    variables_involved=(vid,),
                    expected_condition="all coordinates must be distinct",
                    actual_values={vid: val},
                    message=f"Duplicate coordinate {val}",
                )
            seen.add(key)

        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All coordinates are distinct",
        )


class CoordinateUniqueness(Constraint):
    _metadata = ConstraintMetadata(
        id="coordinate_uniqueness",
        name="Coordinate Uniqueness",
        description="Coordinate values must be unique within axis",
        domain="coordinate",
    )

    def __init__(self, axis: str = "x") -> None:
        self._axis = axis

    def dependencies(self) -> list[str]:
        return ["distinct_coordinates"]

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        from src.variable_engine import VariableType
        graph = variable_graph
        axis_idx = 0 if self._axis == "x" else 1
        seen: set[Any] = set()

        for v in graph.all_nodes():
            if v.type in (VariableType.POINT, VariableType.COORDINATE):
                val = variable_values.get(v.id)
                if val is not None:
                    try:
                        axis_val = val[axis_idx] if isinstance(val, (list, tuple)) else val
                    except (IndexError, TypeError):
                        continue
                    if axis_val in seen:
                        return ConstraintResult(
                            constraint_id=self._metadata.id,
                            passed=False,
                            severity=Severity.WARNING,
                            retry_reason=RetryReason.INVALID_COORDINATE,
                            variables_involved=(v.id,),
                            expected_condition=f"{self._axis}-coordinates must be unique",
                            actual_values={v.id: val},
                            message=f"Duplicate {self._axis}-coordinate {axis_val}",
                        )
                    seen.add(axis_val)

        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message=f"All {self._axis}-coordinates are unique",
        )
