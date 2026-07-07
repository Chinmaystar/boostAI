from __future__ import annotations

from typing import Any, Optional

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class DomainRestrictions(Constraint):
    _metadata = ConstraintMetadata(
        id="domain_restrictions",
        name="Domain Restrictions",
        description="Values must be within the permitted domain",
        domain="domain",
    )

    def __init__(
        self,
        domain_map: Optional[dict[str, tuple[Optional[float], Optional[float]]]] = None,
    ) -> None:
        self._domain_map: dict[str, tuple[Optional[float], Optional[float]]] = domain_map or {}

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        for vid, (vmin, vmax) in self._domain_map.items():
            val = variable_values.get(vid)
            if val is None or not isinstance(val, (int, float)):
                continue
            if vmin is not None and val < vmin:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.DOMAIN_VIOLATION,
                    variables_involved=(vid,),
                    expected_condition=f"value >= {vmin}",
                    actual_values={vid: val},
                    message=f"Value {val} is below domain minimum {vmin}",
                )
            if vmax is not None and val > vmax:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.DOMAIN_VIOLATION,
                    variables_involved=(vid,),
                    expected_condition=f"value <= {vmax}",
                    actual_values={vid: val},
                    message=f"Value {val} exceeds domain maximum {vmax}",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values within domain",
        )


class RangeRestrictions(Constraint):
    _metadata = ConstraintMetadata(
        id="range_restrictions",
        name="Range Restrictions",
        description="Values must be within range",
        domain="domain",
    )

    def __init__(
        self,
        range_map: Optional[dict[str, tuple[Optional[float], Optional[float]]]] = None,
    ) -> None:
        self._range_map: dict[str, tuple[Optional[float], Optional[float]]] = range_map or {}

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        for vid, (rmin, rmax) in self._range_map.items():
            val = variable_values.get(vid)
            if val is None or not isinstance(val, (int, float)):
                continue
            if rmin is not None and val < rmin:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.RANGE_VIOLATION,
                    variables_involved=(vid,),
                    expected_condition=f"value >= {rmin}",
                    actual_values={vid: val},
                    message=f"Value {val} is below range minimum {rmin}",
                )
            if rmax is not None and val > rmax:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.RANGE_VIOLATION,
                    variables_involved=(vid,),
                    expected_condition=f"value <= {rmax}",
                    actual_values={vid: val},
                    message=f"Value {val} exceeds range maximum {rmax}",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values within range",
        )


class DuplicateVariablePrevention(Constraint):
    _metadata = ConstraintMetadata(
        id="duplicate_variable_prevention",
        name="Duplicate Variable Prevention",
        description="No two variables may share the same value where forbidden",
        domain="domain",
    )

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        seen: dict[Any, str] = {}
        for vid, val in variable_values.items():
            if val is None:
                continue
            if val in seen:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.DUPLICATE_VARIABLE,
                    variables_involved=(seen[val], vid),
                    expected_condition="variable values must be distinct",
                    actual_values={vid: val},
                    message=f"Variables '{seen[val]}' and '{vid}' both have value {val}",
                )
            seen[val] = vid
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="No duplicate variable values",
        )


class ExpressionValidity(Constraint):
    _metadata = ConstraintMetadata(
        id="expression_validity",
        name="Expression Validity",
        description="Expression must evaluate without error",
        domain="domain",
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
            if v.type in (VariableType.EXPRESSION, VariableType.EQUATION):
                children = graph.children(v.id)
                for child in children:
                    val = variable_values.get(child.id)
                    if val is not None:
                        try:
                            float(val)
                        except (TypeError, ValueError):
                            return ConstraintResult(
                                constraint_id=self._metadata.id,
                                passed=False,
                                severity=Severity.ERROR,
                                retry_reason=RetryReason.INVALID_EXPRESSION,
                                variables_involved=(child.id,),
                                expected_condition="value must be numeric",
                                actual_values={child.id: val},
                                message=f"Invalid numeric value {val} for variable '{child.name}'",
                            )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All expression values are valid",
        )
