from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .diagram_template import DiagramTemplate, SUPPORTED_DIAGRAM_TYPES


@dataclass
class RegistryEntry:
    """An entry in the diagram registry."""
    template_id: str
    template: DiagramTemplate
    tags: list[str] = field(default_factory=list)
    concept: str = ""
    diagram_type: str = ""
    subject: str = "Mathematics"

    def matches_query(self, query: RegistryLookup) -> bool:
        if query.template_id and self.template_id != query.template_id:
            return False
        if query.diagram_type and self.diagram_type != query.diagram_type:
            return False
        if query.subject and self.subject != query.subject:
            return False
        if query.concept and query.concept.lower() not in self.concept.lower():
            return False
        if query.tags:
            if not all(t in self.tags for t in query.tags):
                return False
        return True


@dataclass
class RegistryLookup:
    """Query parameters for registry lookup."""
    template_id: Optional[str] = None
    diagram_type: Optional[str] = None
    concept: Optional[str] = None
    subject: Optional[str] = None
    tags: Optional[list[str]] = None


class DuplicateTemplateError(ValueError):
    """Raised when registering a template with a duplicate ID."""


class TemplateNotFoundError(KeyError):
    """Raised when a template ID is not found in the registry."""


class DiagramRegistry:
    """Registry for reusable diagram templates.

    Supports lookup by template ID, diagram type, concept, subject,
    and tags.  Follows the same pattern as ``TemplateRegistry``
    and ``VariableRegistry`` in the expression engine.
    """

    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}

    # ---- registration ---------------------------------------------------

    def register(
        self,
        template: DiagramTemplate,
        tags: list[str] | None = None,
        concept: str | None = None,
        subject: str | None = None,
        allow_overwrite: bool = False,
    ) -> str:
        tid = template.metadata.template_id
        if tid in self._entries and not allow_overwrite:
            raise DuplicateTemplateError(
                f"Template '{tid}' is already registered. "
                "Use allow_overwrite=True to replace it."
            )
        self._entries[tid] = RegistryEntry(
            template_id=tid,
            template=template,
            tags=tags or template.metadata.tags,
            concept=concept or template.metadata.concept,
            diagram_type=template.metadata.diagram_type,
            subject=subject or template.metadata.subject,
        )
        return tid

    def unregister(self, template_id: str) -> None:
        if template_id not in self._entries:
            raise TemplateNotFoundError(f"Template '{template_id}' not found.")
        del self._entries[template_id]

    # ---- lookup ---------------------------------------------------------

    def get(self, template_id: str) -> Optional[DiagramTemplate]:
        entry = self._entries.get(template_id)
        return entry.template if entry else None

    def get_entry(self, template_id: str) -> Optional[RegistryEntry]:
        return self._entries.get(template_id)

    def find(self, query: RegistryLookup) -> list[DiagramTemplate]:
        return [
            entry.template
            for entry in self._entries.values()
            if entry.matches_query(query)
        ]

    def find_by_type(self, diagram_type: str) -> list[DiagramTemplate]:
        return [
            entry.template
            for entry in self._entries.values()
            if entry.diagram_type == diagram_type
        ]

    def find_by_concept(self, concept: str) -> list[DiagramTemplate]:
        return [
            entry.template
            for entry in self._entries.values()
            if concept.lower() in entry.concept.lower()
        ]

    def find_by_tag(self, tag: str) -> list[DiagramTemplate]:
        return [
            entry.template
            for entry in self._entries.values()
            if tag in entry.tags
        ]

    # ---- enumeration ----------------------------------------------------

    def list_ids(self) -> list[str]:
        return list(self._entries.keys())

    def list_types(self) -> list[str]:
        types: set[str] = set()
        for entry in self._entries.values():
            if entry.diagram_type:
                types.add(entry.diagram_type)
        return sorted(types)

    def list_concepts(self) -> list[str]:
        concepts: set[str] = set()
        for entry in self._entries.values():
            if entry.concept:
                concepts.add(entry.concept)
        return sorted(concepts)

    def count(self) -> int:
        return len(self._entries)

    # ---- lifecycle ------------------------------------------------------

    def clear(self) -> None:
        self._entries.clear()

    def to_dict(self) -> dict:
        return {
            "entries": {
                tid: {
                    "template_id": entry.template_id,
                    "diagram_type": entry.diagram_type,
                    "concept": entry.concept,
                    "subject": entry.subject,
                    "tags": list(entry.tags),
                    "is_parameterized": entry.template.is_parameterized,
                }
                for tid, entry in self._entries.items()
            },
            "count": self.count(),
            "types": self.list_types(),
            "concepts": self.list_concepts(),
        }
