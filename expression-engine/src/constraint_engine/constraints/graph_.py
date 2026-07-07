from __future__ import annotations

from typing import Any, Optional

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class GraphBounds(Constraint):
    _metadata = ConstraintMetadata(
        id="graph_bounds",
        name="Graph Bounds",
        description="Values must be within graph boundaries",
        domain="graph",
    )

    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        variable_ids: tuple[str, ...] = (),
    ) -> None:
        self._min = min_value
        self._max = max_value
        self._variable_ids = variable_ids

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        ids = self._variable_ids or list(variable_values.keys())
        for vid in ids:
            val = variable_values.get(vid)
            if val is None or not isinstance(val, (int, float)):
                continue
            if self._min is not None and val < self._min:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.GRAPH_BOUNDS_EXCEEDED,
                    variables_involved=(vid,),
                    expected_condition=f"value >= {self._min}",
                    actual_values={vid: val},
                    message=f"Value {val} is below minimum {self._min}",
                )
            if self._max is not None and val > self._max:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.GRAPH_BOUNDS_EXCEEDED,
                    variables_involved=(vid,),
                    expected_condition=f"value <= {self._max}",
                    actual_values={vid: val},
                    message=f"Value {val} exceeds maximum {self._max}",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values within graph bounds",
        )


class AxisLimits(Constraint):
    _metadata = ConstraintMetadata(
        id="axis_limits",
        name="Axis Limits",
        description="Axis minimum must be less than maximum",
        domain="graph",
    )

    def __init__(self, axis: str = "x") -> None:
        self._axis = axis

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        min_key = f"{self._axis}_axis_min"
        max_key = f"{self._axis}_axis_max"
        vmin = variable_values.get(min_key)
        vmax = variable_values.get(max_key)
        if vmin is not None and vmax is not None:
            if vmin >= vmax:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.INVALID_AXIS_LIMITS,
                    variables_involved=(),
                    expected_condition=f"{self._axis}_min < {self._axis}_max",
                    actual_values={min_key: vmin, max_key: vmax},
                    message=f"{self._axis}-axis min {vmin} >= max {vmax}",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message=f"{self._axis}-axis limits are valid",
        )


class Monotonicity(Constraint):
    _metadata = ConstraintMetadata(
        id="monotonicity",
        name="Monotonicity",
        description="Values must form a monotonic sequence",
        domain="graph",
    )

    def __init__(self, direction: str = "increasing") -> None:
        self._direction = direction

    def dependencies(self) -> list[str]:
        return ["graph_bounds"]

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        sorted_ids = sorted(variable_values.keys())
        values = [variable_values[k] for k in sorted_ids if isinstance(variable_values[k], (int, float))]

        if len(values) < 2:
            return ConstraintResult(
                constraint_id=self._metadata.id,
                passed=True,
                severity=Severity.INFO,
                message="Not enough values to check monotonicity",
            )

        for i in range(1, len(values)):
            if self._direction == "increasing" and values[i] <= values[i - 1]:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.WARNING,
                    retry_reason=RetryReason.NON_MONOTONIC,
                    variables_involved=(),
                    expected_condition=f"sequence must be {self._direction}",
                    actual_values={"sequence": values},
                    message=f"Value {values[i]} at index {i} breaks {self._direction} order",
                )
            if self._direction == "decreasing" and values[i] >= values[i - 1]:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.WARNING,
                    retry_reason=RetryReason.NON_MONOTONIC,
                    variables_involved=(),
                    expected_condition=f"sequence must be {self._direction}",
                    actual_values={"sequence": values},
                    message=f"Value {values[i]} at index {i} breaks {self._direction} order",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message=f"Sequence is {self._direction}",
        )
