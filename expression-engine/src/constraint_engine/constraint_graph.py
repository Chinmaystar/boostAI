from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class DependencyEdge:
    source_id: str
    target_id: str

    def to_dict(self) -> dict:
        return {"source": self.source_id, "target": self.target_id}


class ConstraintGraph:
    """Dependency graph for constraint execution ordering.

    Nodes are constraint IDs. A directed edge ``A → B`` means
    ``A`` depends on ``B`` (B must execute before A).

    Supports topological sorting for execution order and cycle
    detection.
    """

    def __init__(self) -> None:
        self._nodes: set[str] = set()
        self._edges: list[DependencyEdge] = []
        self._forward: dict[str, set[str]] = {}   # A → {B} means A depends on B
        self._reverse: dict[str, set[str]] = {}   # B → {A} means B is required by A

    def add_node(self, constraint_id: str) -> None:
        self._nodes.add(constraint_id)

    def add_dependency(self, constraint_id: str, depends_on: str) -> None:
        self._nodes.add(constraint_id)
        self._nodes.add(depends_on)
        self._edges.append(DependencyEdge(constraint_id, depends_on))
        self._forward.setdefault(constraint_id, set()).add(depends_on)
        self._reverse.setdefault(depends_on, set()).add(constraint_id)

    def has_node(self, constraint_id: str) -> bool:
        return constraint_id in self._nodes

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return len(self._edges)

    def dependencies_of(self, constraint_id: str) -> list[str]:
        return list(self._forward.get(constraint_id, set()))

    def dependents_of(self, constraint_id: str) -> list[str]:
        return list(self._reverse.get(constraint_id, set()))

    def has_cycle(self) -> bool:
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for dep in self._forward.get(node, set()):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in in_stack:
                    return True
            in_stack.discard(node)
            return False

        for n in self._nodes:
            if n not in visited:
                if dfs(n):
                    return True
        return False

    def execution_order(self) -> list[str]:
        """Return constraint IDs in topological order (dependencies first).

        Raises ``ValueError`` if the graph contains a cycle.
        """
        if self.has_cycle():
            raise ValueError("ConstraintGraph contains a cycle; cannot determine execution order")

        visited: set[str] = set()
        order: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            for dep in self._forward.get(node, set()):
                dfs(dep)
            visited.add(node)
            order.append(node)

        for n in sorted(self._nodes):
            if n not in visited:
                dfs(n)

        return order

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()
        self._forward.clear()
        self._reverse.clear()

    def to_dict(self) -> dict:
        return {
            "nodes": list(self._nodes),
            "edges": [e.to_dict() for e in self._edges],
            "execution_order": self.execution_order() if not self.has_cycle() else [],
        }
