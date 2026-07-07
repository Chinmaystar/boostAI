from __future__ import annotations

from typing import Optional

from .semantic_template import (
    SemanticTemplate,
    GeneratorType,
    TemplateFamily,
    ConstraintType,
)


class SemanticTemplateRegistry:
    """Manages registered ``SemanticTemplate`` instances.

    Supports lookup by:
    - Template ID (unique)
    - Template family (one-to-many)
    - Concept (one-to-many)
    - Generator type (one-to-many)
    - Constraint type (one-to-many)
    - Tags (intersection)

    Version management is provided via ``get_versions`` and
    ``get_latest_version`` which rely on the template's
    ``metadata.version`` field.
    """

    def __init__(self) -> None:
        self._by_id: dict[str, SemanticTemplate] = {}
        self._by_family: dict[TemplateFamily, list[SemanticTemplate]] = {}
        self._by_concept: dict[str, list[SemanticTemplate]] = {}
        self._by_generator: dict[GeneratorType, list[SemanticTemplate]] = {}
        self._by_constraint: dict[ConstraintType, list[SemanticTemplate]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, template: SemanticTemplate) -> bool:
        """Register a semantic template.

        Args:
            template: The ``SemanticTemplate`` to register.

        Returns:
            ``True`` if this is a new template (ID not previously seen),
            ``False`` if a template with the same ID already exists.
        """
        tid = template.template_id
        if tid in self._by_id:
            return False

        self._by_id[tid] = template

        family = template.template_family
        self._by_family.setdefault(family, []).append(template)

        concept = template.concept
        if concept:
            self._by_concept.setdefault(concept, []).append(template)

        gen = template.generator_type
        self._by_generator.setdefault(gen, []).append(template)

        for ct in template.expected_constraint_types:
            self._by_constraint.setdefault(ct, []).append(template)

        return True

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def lookup_by_id(self, template_id: str) -> Optional[SemanticTemplate]:
        return self._by_id.get(template_id)

    def lookup_by_family(
        self, family: TemplateFamily,
    ) -> list[SemanticTemplate]:
        return list(self._by_family.get(family, []))

    def lookup_by_concept(self, concept: str) -> list[SemanticTemplate]:
        return list(self._by_concept.get(concept, []))

    def lookup_by_generator(
        self, generator: GeneratorType,
    ) -> list[SemanticTemplate]:
        return list(self._by_generator.get(generator, []))

    def lookup_by_constraint(
        self, constraint: ConstraintType,
    ) -> list[SemanticTemplate]:
        return list(self._by_constraint.get(constraint, []))

    def lookup_by_tags(
        self, tags: set[str], require_all: bool = True,
    ) -> list[SemanticTemplate]:
        """Look up templates containing the given tags.

        Args:
            tags: Set of tag strings to match.
            require_all: If ``True`` only templates that have *all*
                specified tags are returned; if ``False`` any template
                with *at least one* matching tag is returned.

        Returns:
            A list of matching ``SemanticTemplate`` instances.
        """
        if not tags:
            return []
        result: list[SemanticTemplate] = []
        for t in self._by_id.values():
            t_tags = set(t.tags)
            if require_all:
                if tags.issubset(t_tags):
                    result.append(t)
            else:
                if tags & t_tags:
                    result.append(t)
        return result

    # ------------------------------------------------------------------
    # Version management
    # ------------------------------------------------------------------

    def get_versions(self, template_id: str) -> list[str]:
        """Return all version strings for the given template ID.

        Since the current implementation stores only the latest
        version under each ID, this returns ``[version]`` if the
        template exists or ``[]`` otherwise.
        """
        t = self._by_id.get(template_id)
        if t is None:
            return []
        return [t.metadata.version]

    def get_latest_version(self, template_id: str) -> Optional[SemanticTemplate]:
        return self._by_id.get(template_id)

    def has_id(self, template_id: str) -> bool:
        return template_id in self._by_id

    # ------------------------------------------------------------------
    # Collection queries
    # ------------------------------------------------------------------

    def count(self) -> int:
        return len(self._by_id)

    def get_all(self) -> list[SemanticTemplate]:
        return list(self._by_id.values())

    def get_all_ids(self) -> list[str]:
        return list(self._by_id.keys())

    def get_all_families(self) -> set[TemplateFamily]:
        return set(self._by_family.keys())

    def clear(self) -> None:
        self._by_id.clear()
        self._by_family.clear()
        self._by_concept.clear()
        self._by_generator.clear()
        self._by_constraint.clear()
