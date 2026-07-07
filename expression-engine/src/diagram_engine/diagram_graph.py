from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class RelationType(Enum):
    BELONGS_TO = "belongs_to"
    CONNECTS = "connects"
    ATTACHED_TO = "attached_to"
    CONTAINS = "contains"
    ADJACENT_TO = "adjacent_to"
    INTERSECTS = "intersects"
    PARALLEL_TO = "parallel_to"
    PERPENDICULAR_TO = "perpendicular_to"
    LABEL_FOR = "label_for"
    CENTER_OF = "center_of"
    RADIUS_OF = "radius_of"
    DIAMETER_OF = "diameter_of"
    CHORD_OF = "chord_of"
    TANGENT_TO = "tangent_to"
    SIDE_OF = "side_of"
    VERTEX_OF = "vertex_of"
    ANGLE_AT = "angle_at"
    BISECTS = "bisects"
    INTERSECTION_OF = "intersection_of"
    PROJECTION_OF = "projection_of"
    MIDPOINT_OF = "midpoint_of"
    REFLECTION_OF = "reflection_of"
    TRANSLATION_OF = "translation_of"


@dataclass(frozen=True)
class DiagramEdge:
    source_id: str
    target_id: str
    relation: RelationType
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "metadata": self.metadata,
        }


class DiagramGraph:
    """A directed graph describing relationships between diagram primitives.

    Nodes are primitive IDs (``str``).  Edges are ``DiagramEdge`` records
    that capture geometric, topological, or semantic relationships.
    """

    def __init__(self) -> None:
        self._edges: list[DiagramEdge] = []
        self._node_metadata: dict[str, dict[str, Any]] = {}

    # ---- edge management -------------------------------------------------

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: RelationType,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._edges.append(DiagramEdge(source_id, target_id, relation, metadata))

    def add_edge_str(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        rel = RelationType(relation)
        self._edges.append(DiagramEdge(source_id, target_id, rel, metadata))

    def get_edges(self) -> list[DiagramEdge]:
        return list(self._edges)

    def edge_count(self) -> int:
        return len(self._edges)

    def clear_edges(self) -> None:
        self._edges.clear()

    # ---- traversal -------------------------------------------------------

    def get_outgoing(self, primitive_id: str) -> list[DiagramEdge]:
        return [e for e in self._edges if e.source_id == primitive_id]

    def get_incoming(self, primitive_id: str) -> list[DiagramEdge]:
        return [e for e in self._edges if e.target_id == primitive_id]

    def get_relations(
        self, primitive_id: str, relation: RelationType,
    ) -> list[DiagramEdge]:
        return [
            e for e in self._edges
            if e.source_id == primitive_id and e.relation == relation
        ]

    def get_related(
        self, primitive_id: str, relation: RelationType,
    ) -> list[str]:
        return [
            e.target_id for e in self._edges
            if e.source_id == primitive_id and e.relation == relation
        ]

    def get_related_by_any(
        self, primitive_id: str,
    ) -> list[tuple[str, RelationType]]:
        result: list[tuple[str, RelationType]] = []
        for e in self._edges:
            if e.source_id == primitive_id:
                result.append((e.target_id, e.relation))
            if e.target_id == primitive_id:
                result.append((e.source_id, e.relation))
        return result

    def has_path(self, source_id: str, target_id: str) -> bool:
        visited: set[str] = set()
        stack = [source_id]
        while stack:
            current = stack.pop()
            if current == target_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            for e in self._edges:
                if e.source_id == current:
                    stack.append(e.target_id)
        return False

    # ---- node metadata ---------------------------------------------------

    def set_metadata(self, primitive_id: str, **kwargs: Any) -> None:
        if primitive_id not in self._node_metadata:
            self._node_metadata[primitive_id] = {}
        self._node_metadata[primitive_id].update(kwargs)

    def get_metadata(self, primitive_id: str) -> dict[str, Any]:
        return self._node_metadata.get(primitive_id, {})

    def all_nodes(self) -> set[str]:
        nodes: set[str] = set()
        for e in self._edges:
            nodes.add(e.source_id)
            nodes.add(e.target_id)
        nodes.update(self._node_metadata.keys())
        return nodes

    # ---- roots (primitives with no incoming edges) -----------------------

    def roots(self) -> list[str]:
        has_incoming: set[str] = {e.target_id for e in self._edges}
        return [n for n in self.all_nodes() if n not in has_incoming]

    # ---- serialization ---------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "edges": [e.to_dict() for e in self._edges],
            "node_metadata": {
                k: dict(v) for k, v in self._node_metadata.items()
            },
            "roots": self.roots(),
        }

    def clear(self) -> None:
        self._edges.clear()
        self._node_metadata.clear()
