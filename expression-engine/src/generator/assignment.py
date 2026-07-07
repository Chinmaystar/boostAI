from __future__ import annotations

from typing import Any

from src.variable_engine import Variable, VariableGraph, VariableType

from .sampler import DomainSampler


class VariableAssignmentGenerator:
    def __init__(self, sampler: DomainSampler) -> None:
        self._sampler = sampler

    def generate(
        self,
        graph: VariableGraph,
        strategy: str = "uniform",
    ) -> dict[str, Any]:
        assignments: dict[str, Any] = {}
        for var in graph.all_nodes():
            if not var.metadata.can_randomize:
                assignments[var.id] = var.original_value
                continue
            val = self._sampler.sample(var.domain, var.type, strategy)
            assignments[var.id] = val
        return assignments

    def generate_one(
        self,
        variable: Variable,
        strategy: str = "uniform",
    ) -> Any:
        return self._sampler.sample(variable.domain, variable.type, strategy)
