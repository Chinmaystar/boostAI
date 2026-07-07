from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .base import ConstraintResult, RetryReason, Severity


@dataclass(frozen=True)
class Diagnostic:
    constraint_id: str
    constraint_name: str
    severity: Severity
    passed: bool
    variables_involved: tuple[str, ...] = ()
    expected_condition: str = ""
    actual_values: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    code: str = ""

    def to_dict(self) -> dict:
        return {
            "constraint_id": self.constraint_id,
            "constraint_name": self.constraint_name,
            "severity": self.severity.value,
            "passed": self.passed,
            "variables_involved": list(self.variables_involved),
            "expected_condition": self.expected_condition,
            "actual_values": self.actual_values,
            "message": self.message,
            "code": self.code,
        }


@dataclass(frozen=True)
class ValidationStats:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    warnings: int = 0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class ConstraintValidationResult:
    valid: bool
    diagnostics: tuple[Diagnostic, ...] = ()
    retry_reason: RetryReason = RetryReason.NONE
    execution_trace: tuple[str, ...] = ()
    stats: ValidationStats = field(default_factory=ValidationStats)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "retry_reason": self.retry_reason.value,
            "execution_trace": list(self.execution_trace),
            "stats": self.stats.to_dict(),
        }

    @staticmethod
    def from_results(
        results: list[ConstraintResult],
        trace: Optional[list[str]] = None,
    ) -> ConstraintValidationResult:
        diagnostics: list[Diagnostic] = []
        retry = RetryReason.NONE
        total = len(results)
        passed = 0
        failed = 0
        errors = 0
        warnings = 0

        for r in results:
            is_error = r.severity == Severity.ERROR
            diag = Diagnostic(
                constraint_id=r.constraint_id,
                constraint_name=r.constraint_id,
                severity=r.severity,
                passed=r.passed,
                variables_involved=r.variables_involved,
                expected_condition=r.expected_condition,
                actual_values=r.actual_values,
                message=r.message,
                code=r.retry_reason.value if r.retry_reason != RetryReason.NONE else "",
            )
            diagnostics.append(diag)

            if r.passed:
                passed += 1
            elif is_error:
                failed += 1
                if r.retry_reason != RetryReason.NONE and retry == RetryReason.NONE:
                    retry = r.retry_reason
            else:
                warnings += 1

        stats = ValidationStats(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            warnings=warnings,
        )
        valid = failed == 0

        return ConstraintValidationResult(
            valid=valid,
            diagnostics=tuple(diagnostics),
            retry_reason=retry,
            execution_trace=tuple(trace or []),
            stats=stats,
        )
