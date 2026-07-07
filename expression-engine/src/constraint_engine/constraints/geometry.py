from __future__ import annotations

from typing import Any

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class PositiveRadius(Constraint):
    _metadata = ConstraintMetadata(
        id="positive_radius",
        name="Positive Radius",
        description="Radius must be greater than zero",
        domain="geometry",
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
        for v in graph.all_nodes():
            if v.type == VariableType.RADIUS:
                val = variable_values.get(v.id)
                if val is not None and val <= 0:
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NEGATIVE_RADIUS,
                        variables_involved=(v.id,),
                        expected_condition="radius > 0",
                        actual_values={v.id: val},
                        message=f"Radius value {val} is not positive",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All radii are positive",
        )


class PositiveLength(Constraint):
    _metadata = ConstraintMetadata(
        id="positive_length",
        name="Positive Length",
        description="Length must be greater than zero",
        domain="geometry",
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
        for v in graph.all_nodes():
            if v.type == VariableType.LENGTH:
                val = variable_values.get(v.id)
                if val is not None and val <= 0:
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NEGATIVE_LENGTH,
                        variables_involved=(v.id,),
                        expected_condition="length > 0",
                        actual_values={v.id: val},
                        message=f"Length value {val} is not positive",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All lengths are positive",
        )


class PositiveArea(Constraint):
    _metadata = ConstraintMetadata(
        id="positive_area",
        name="Positive Area",
        description="Area must be greater than zero",
        domain="geometry",
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
        for v in graph.all_nodes():
            if v.type == VariableType.AREA:
                val = variable_values.get(v.id)
                if val is not None and val <= 0:
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NEGATIVE_AREA,
                        variables_involved=(v.id,),
                        expected_condition="area > 0",
                        actual_values={v.id: val},
                        message=f"Area value {val} is not positive",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All areas are positive",
        )


class TriangleInequality(Constraint):
    _metadata = ConstraintMetadata(
        id="triangle_inequality",
        name="Triangle Inequality",
        description="Sum of any two sides must exceed the third",
        domain="geometry",
    )

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def dependencies(self) -> list[str]:
        return ["positive_length"]

    def _find_sides(self, graph: object) -> list[str]:
        from src.variable_engine import VariableType
        return [
            v.id for v in graph.all_nodes()
            if v.type == VariableType.LENGTH
        ]

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        sides = self._find_sides(variable_graph)
        if len(sides) < 3:
            return ConstraintResult(
                constraint_id=self._metadata.id,
                passed=True,
                severity=Severity.INFO,
                message="Not enough sides for triangle inequality",
            )

        values = [variable_values.get(s) for s in sides]
        if any(v is None for v in values):
            return ConstraintResult(
                constraint_id=self._metadata.id,
                passed=True,
                severity=Severity.WARNING,
                message="Cannot check triangle inequality: missing side values",
            )

        a, b, c = values[0], values[1], values[2]
        if (a + b > c) and (a + c > b) and (b + c > a):
            return ConstraintResult(
                constraint_id=self._metadata.id,
                passed=True,
                severity=Severity.INFO,
                expected_condition="a + b > c, a + c > b, b + c > a",
                actual_values={"a": a, "b": b, "c": c},
                message="Triangle inequality holds",
            )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=False,
            severity=Severity.ERROR,
            retry_reason=RetryReason.INVALID_TRIANGLE,
            variables_involved=(sides[0], sides[1], sides[2]),
            expected_condition="a + b > c, a + c > b, b + c > a",
            actual_values={"a": a, "b": b, "c": c},
            message=f"Sides {a}, {b}, {c} do not satisfy triangle inequality",
        )
