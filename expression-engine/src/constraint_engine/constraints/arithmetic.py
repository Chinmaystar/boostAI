from __future__ import annotations

from typing import Any

from ..base import (
    Constraint, ConstraintResult, ConstraintMetadata,
    Severity, RetryReason,
)


class NonZeroDenominator(Constraint):
    _metadata = ConstraintMetadata(
        id="non_zero_denominator",
        name="Non-Zero Denominator",
        description="Denominator must not be zero",
        domain="arithmetic",
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
        denominators = [
            v for v in graph.all_nodes()
            if v.type == VariableType.CONSTANT
        ]
        for v in denominators:
            parents = graph.parents(v.id)
            is_denominator_spot = any(
                p.type == VariableType.EXPRESSION
                for p in parents
            )
            if not is_denominator_spot:
                continue
            val = variable_values.get(v.id)
            if val is not None and val == 0:
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.ZERO_DENOMINATOR,
                    variables_involved=(v.id,),
                    expected_condition="denominator != 0",
                    actual_values={v.id: val},
                    message=f"Denominator value {val} is zero",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All denominators are non-zero",
        )


class IntegerConstraint(Constraint):
    _metadata = ConstraintMetadata(
        id="integer_constraint",
        name="Integer Constraint",
        description="Value must be an integer",
        domain="arithmetic",
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
        ids = self._variable_ids or list(variable_values.keys())
        for vid in ids:
            val = variable_values.get(vid)
            if val is not None and not isinstance(val, int):
                return ConstraintResult(
                    constraint_id=self._metadata.id,
                    passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.NON_INTEGER_SOLUTION,
                    variables_involved=(vid,),
                    expected_condition="value must be an integer",
                    actual_values={vid: val},
                    message=f"Value {val} is not an integer",
                )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values are integers",
        )


class PrimeNumber(Constraint):
    _metadata = ConstraintMetadata(
        id="prime_number",
        name="Prime Number",
        description="Value must be a prime number",
        domain="arithmetic",
    )

    def __init__(self, variable_ids: tuple[str, ...] = ()) -> None:
        self._variable_ids = variable_ids

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    @staticmethod
    def _is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        ids = self._variable_ids or list(variable_values.keys())
        for vid in ids:
            val = variable_values.get(vid)
            if val is not None and isinstance(val, int) and val >= 0:
                if not self._is_prime(val):
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NOT_PRIME,
                        variables_involved=(vid,),
                        expected_condition="value must be prime",
                        actual_values={vid: val},
                        message=f"Value {val} is not prime",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values are prime",
        )


class CompositeNumber(Constraint):
    _metadata = ConstraintMetadata(
        id="composite_number",
        name="Composite Number",
        description="Value must be a composite number",
        domain="arithmetic",
    )

    def __init__(self, variable_ids: tuple[str, ...] = ()) -> None:
        self._variable_ids = variable_ids

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    @staticmethod
    def _is_composite(n: int) -> bool:
        if n < 4:
            return False
        i = 2
        while i * i <= n:
            if n % i == 0:
                return True
            i += 1
        return False

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        ids = self._variable_ids or list(variable_values.keys())
        for vid in ids:
            val = variable_values.get(vid)
            if val is not None and isinstance(val, int) and val >= 0:
                if not self._is_composite(val):
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NOT_COMPOSITE,
                        variables_involved=(vid,),
                        expected_condition="value must be composite",
                        actual_values={vid: val},
                        message=f"Value {val} is not composite",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values are composite",
        )


class PerfectSquare(Constraint):
    _metadata = ConstraintMetadata(
        id="perfect_square",
        name="Perfect Square",
        description="Value must be a perfect square",
        domain="arithmetic",
    )

    def __init__(self, variable_ids: tuple[str, ...] = ()) -> None:
        self._variable_ids = variable_ids

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    @staticmethod
    def _is_perfect_square(n: int) -> bool:
        if n < 0:
            return False
        r = int(n ** 0.5)
        return r * r == n

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        ids = self._variable_ids or list(variable_values.keys())
        for vid in ids:
            val = variable_values.get(vid)
            if val is not None and isinstance(val, int) and val >= 0:
                if not self._is_perfect_square(val):
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NOT_PERFECT_SQUARE,
                        variables_involved=(vid,),
                        expected_condition="value must be a perfect square",
                        actual_values={vid: val},
                        message=f"Value {val} is not a perfect square",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values are perfect squares",
        )


class PerfectCube(Constraint):
    _metadata = ConstraintMetadata(
        id="perfect_cube",
        name="Perfect Cube",
        description="Value must be a perfect cube",
        domain="arithmetic",
    )

    def __init__(self, variable_ids: tuple[str, ...] = ()) -> None:
        self._variable_ids = variable_ids

    @property
    def metadata(self) -> ConstraintMetadata:
        return self._metadata

    @staticmethod
    def _is_perfect_cube(n: int) -> bool:
        if n < 0:
            return False
        r = round(n ** (1 / 3))
        return r * r * r == n

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: object,
    ) -> ConstraintResult:
        ids = self._variable_ids or list(variable_values.keys())
        for vid in ids:
            val = variable_values.get(vid)
            if val is not None and isinstance(val, int) and val >= 0:
                if not self._is_perfect_cube(val):
                    return ConstraintResult(
                        constraint_id=self._metadata.id,
                        passed=False,
                        severity=Severity.ERROR,
                        retry_reason=RetryReason.NOT_PERFECT_CUBE,
                        variables_involved=(vid,),
                        expected_condition="value must be a perfect cube",
                        actual_values={vid: val},
                        message=f"Value {val} is not a perfect cube",
                    )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="All values are perfect cubes",
        )


class FactorisablePolynomial(Constraint):
    _metadata = ConstraintMetadata(
        id="factorisable_polynomial",
        name="Factorisable Polynomial",
        description="Coefficients must allow factorisation",
        domain="arithmetic",
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
            if v.type != VariableType.COEFFICIENT:
                continue
            coeff = variable_values.get(v.id)
            if coeff is None:
                continue
            parents = graph.parents(v.id)
            for p in parents:
                if p.type != VariableType.EXPRESSION:
                    continue
                siblings = graph.children(p.id)
                sibling_coeffs = [
                    variable_values.get(s.id)
                    for s in siblings
                    if s.type == VariableType.COEFFICIENT
                    and s.id != v.id
                    and variable_values.get(s.id) is not None
                ]
                for sc in sibling_coeffs:
                    if isinstance(coeff, (int, float)) and isinstance(sc, (int, float)):
                        if sc == 0 or coeff % sc in (0, 1):
                            continue
                        candidates = [
                            (a, b)
                            for a in range(1, abs(coeff) + 1)
                            for b in range(1, abs(sc) + 1)
                            if a * b == abs(coeff) or a * b == abs(sc)
                        ]
                        if not candidates:
                            return ConstraintResult(
                                constraint_id=self._metadata.id,
                                passed=False,
                                severity=Severity.ERROR,
                                retry_reason=RetryReason.NOT_FACTORISABLE,
                                variables_involved=(v.id,),
                                expected_condition="coefficients should allow factorisation",
                                actual_values={v.id: coeff, s.id: sc},
                                message=f"Polynomial with coeffs {coeff}, {sc} may not factorise",
                            )
        return ConstraintResult(
            constraint_id=self._metadata.id,
            passed=True,
            severity=Severity.INFO,
            message="Polynomial is factorisable",
        )
