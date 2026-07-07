from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .variable import Variable


@dataclass(frozen=True)
class GraphEdge:
    """A directed, labelled relationship between two variables."""
    source_id: str
    target_id: str
    relationship: str  # "contains", "coefficient_of", "left_side", "right_side", etc.

    def to_dict(self) -> dict:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "relationship": self.relationship,
        }


class VariableGraph:
    """A directed graph that captures relationships between variables.

    Nodes are ``Variable`` instances keyed by their ``id``.  Edges are
    ``GraphEdge`` records with labelled relationship types.

    The graph is the primary output of the ``VariableDiscoveryVisitor``
    and will be consumed by future engines (constraint, difficulty,
    diagram).
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Variable] = {}
        self._edges: list[GraphEdge] = []

    # ---- node management ------------------------------------------------

    def add_node(self, variable: Variable) -> None:
        self._nodes[variable.id] = variable

    def get_node(self, var_id: str) -> Optional[Variable]:
        return self._nodes.get(var_id)

    def has_node(self, var_id: str) -> bool:
        return var_id in self._nodes

    def all_nodes(self) -> list[Variable]:
        return list(self._nodes.values())

    def node_count(self) -> int:
        return len(self._nodes)

    # ---- edge management ------------------------------------------------

    def add_edge(self, source_id: str, target_id: str, relationship: str) -> None:
        self._edges.append(GraphEdge(source_id, target_id, relationship))

    def get_edges(self) -> list[GraphEdge]:
        return list(self._edges)

    def edge_count(self) -> int:
        return len(self._edges)

    def get_outgoing(self, var_id: str) -> list[GraphEdge]:
        return [e for e in self._edges if e.source_id == var_id]

    def get_incoming(self, var_id: str) -> list[GraphEdge]:
        return [e for e in self._edges if e.target_id == var_id]

    # ---- roots (nodes with no incoming edges) --------------------------

    def roots(self) -> list[Variable]:
        has_incoming: set[str] = {e.target_id for e in self._edges}
        return [n for n in self._nodes.values() if n.id not in has_incoming]

    # ---- children / parents -------------------------------------------

    def children(self, var_id: str) -> list[Variable]:
        return [
            self._nodes[e.target_id]
            for e in self._edges
            if e.source_id == var_id and e.target_id in self._nodes
        ]

    def parents(self, var_id: str) -> list[Variable]:
        return [
            self._nodes[e.source_id]
            for e in self._edges
            if e.target_id == var_id and e.source_id in self._nodes
        ]

    # ---- serialisation --------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "edges": [e.to_dict() for e in self._edges],
            "roots": [v.id for v in self.roots()],
        }

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()
