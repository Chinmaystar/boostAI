from __future__ import annotations

from typing import Any

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class ProbabilityRange(Constraint):
    _metadata = ConstraintMetadata(
        id="probability_range",
        name="Probability Range",
        description="Probability must be between 0 and 1 inclusive",
        domain="statistics",
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
            if v.type == VariableType.PROBABILITY:
                val = variable_values.get(v.id)
                if val is not None:
                    if not isinstance(val, (int, float)):
                        return ConstraintResult(
                            constraint_id=self._metadata.id,
                            passed=False,
                            severity=Severity.ERROR,
                            retry_reason=RetryReason.INVALID_PROBABILITY,
                            variables_involved=(v.id,),
                            expected_condition="0 ≤ probability ≤ 1",
                            actual_values={v.id: val},
                            message=f"Probability value {val} is not numeric",
                        )
                    if val < 0 or val > 1:
                        return ConstraintResult(
                            constraint_id=self._metadata.id,
                            passed=False,
                            severity=Severity.ERROR,
                            retry_reason=RetryReason.INVALID_PROBABILITY,
                            variables_involved=(v.id,),
                            expected_condition="0 ≤ probability ≤ 1",
                            actual_values={v.id: val},
                            message=f"Probability {val} is out of [0, 1] range",
                        )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All probabilities are in [0, 1]",
        )


class PercentageRange(Constraint):
    _metadata = ConstraintMetadata(
        id="percentage_range",
        name="Percentage Range",
        description="Percentage must be between 0 and 100 inclusive",
        domain="statistics",
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
            if v.type == VariableType.PERCENTAGE:
                val = variable_values.get(v.id)
                if val is not None and isinstance(val, (int, float)):
                    if val < 0 or val > 100:
                        return ConstraintResult(
                            constraint_id=self._metadata.id,
                            passed=False,
                            severity=Severity.ERROR,
                            retry_reason=RetryReason.INVALID_PERCENTAGE,
                            variables_involved=(v.id,),
                            expected_condition="0% ≤ percentage ≤ 100%",
                            actual_values={v.id: val},
                            message=f"Percentage {val} is out of [0, 100] range",
                        )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All percentages are in [0, 100]",
        )
