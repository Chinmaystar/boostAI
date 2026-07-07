from __future__ import annotations

from typing import Any

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class UniqueRoots(Constraint):
    _metadata = ConstraintMetadata(
        id="unique_roots",
        name="Unique Roots",
        description="Equation must have distinct roots",
        domain="algebra",
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
        root_values: list[Any] = []

        for v in graph.all_nodes():
            if v.type == VariableType.SYMBOL:
                val = variable_values.get(v.id)
                if val is not None:
                    root_values.append(val)

        seen = set()
        for val in root_values:
            if val in seen:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.NON_UNIQUE_ROOT,
                    variables_involved=(),
                    expected_condition="all roots must be distinct",
                    actual_values={"roots": root_values},
                    message=f"Duplicate root value {val}",
                )
            seen.add(val)

        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All roots are distinct",
        )


class IntegerSolution(Constraint):
    _metadata = ConstraintMetadata(
        id="integer_solution",
        name="Integer Solution",
        description="Solution must be an integer",
        domain="algebra",
    )

    def __init__(self, variable_ids: tuple[str, ...] = ()) -> None:
        self._variable_ids = variable_ids

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

        ids = self._variable_ids
        if not ids:
            ids = [
                v.id for v in graph.all_nodes()
                if v.type == VariableType.SYMBOL
            ]

        for vid in ids:
            val = variable_values.get(vid)
            if val is not None and not isinstance(val, int):
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.NON_INTEGER_SOLUTION,
                    variables_involved=(vid,),
                    expected_condition="solution must be an integer",
                    actual_values={vid: val},
                    message=f"Solution value {val} is not an integer",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="Solution is an integer",
        )
