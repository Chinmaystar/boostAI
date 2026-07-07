from __future__ import annotations

from typing import Any, Optional

from src.variable_engine import VariableGraph

from .base import Constraint, ConstraintResult, RetryReason
from .constraint_graph import ConstraintGraph
from .registry import ConstraintRegistry
from .result import ConstraintValidationResult, ValidationStats


class ConstraintValidator:
    """Performs mathematical validation of variable assignments.

    The validator:
    1. Selects constraints relevant to the given template/variables
    2. Resolves dependency order via ``ConstraintGraph``
    3. Executes each constraint
    4. Aggregates results into a ``ConstraintValidationResult``
    """

    def __init__(self, registry: ConstraintRegistry) -> None:
        self._registry = registry

    def validate(
        self,
        variable_values: dict[str, Any],
        variable_graph: VariableGraph,
        constraint_ids: Optional[list[str]] = None,
    ) -> ConstraintValidationResult:
        """Validate variable assignments against a set of constraints.

        Args:
            variable_values: Mapping of ``{variable_id: proposed_value}``.
            variable_graph: The ``VariableGraph`` from Milestone 3.
            constraint_ids: Specific constraint IDs to check. If ``None``,
                all registered constraints are used.

        Returns:
            A ``ConstraintValidationResult`` with diagnostics.
        """
        if constraint_ids is not None:
            constraints = self._registry.get_by_ids(constraint_ids)
        else:
            constraints = self._registry.get_all()

        graph = ConstraintGraph()
        for c in constraints:
            graph.add_node(c.metadata.id)
            for dep_id in c.dependencies():
                graph.add_dependency(c.metadata.id, dep_id)

        try:
            order = graph.execution_order()
        except ValueError:
            return ConstraintValidationResult(
                valid=False,
                retry_reason=RetryReason.CONSTRAINT_VIOLATION,
                execution_trace=("cycle_detected",),
                stats=ValidationStats(),
            )

        ordered: list[Constraint] = []
        seen: set[str] = set()
        for cid in order:
            if cid not in seen:
                c = self._registry.get(cid)
                if c is not None:
                    ordered.append(c)
                    seen.add(cid)

        results: list[ConstraintResult] = []
        trace: list[str] = []

        for c in ordered:
            try:
                result = c.validate(variable_values, variable_graph)
                results.append(result)
                trace.append(f"{c.metadata.id}:{'PASS' if result.passed else 'FAIL'}")
            except Exception as exc:
                results.append(ConstraintResult(
                    constraint_id=c.metadata.id,
                    passed=False,
                    message=f"Constraint execution error: {exc}",
                ))
                trace.append(f"{c.metadata.id}:ERROR")

        return ConstraintValidationResult.from_results(results, trace=trace)
