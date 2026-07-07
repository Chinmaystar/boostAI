from __future__ import annotations

from typing import Optional

from .base import Constraint, ConstraintMetadata


class ConstraintRegistry:
    """Plugin registry for constraint discovery and registration.

    Every constraint implementation registers itself with a unique ID.
    The registry supports lookup by ID, domain, and priority-based
    ordering.
    """

    def __init__(self) -> None:
        self._constraints: dict[str, Constraint] = {}
        self._by_domain: dict[str, list[Constraint]] = {}
        self._metadata: dict[str, ConstraintMetadata] = {}

    def register(self, constraint: Constraint) -> bool:
        """Register a constraint plugin.

        Args:
            constraint: A ``Constraint`` instance.

        Returns:
            ``True`` if this ID is new, ``False`` if a constraint with
            the same ID is already registered.
        """
        cid = constraint.metadata.id
        if cid in self._constraints:
            return False

        self._constraints[cid] = constraint
        self._metadata[cid] = constraint.metadata

        domain = constraint.metadata.domain
        self._by_domain.setdefault(domain, []).append(constraint)

        return True

    def register_many(self, constraints: list[Constraint]) -> int:
        """Register multiple constraints.

        Args:
            constraints: A list of ``Constraint`` instances.

        Returns:
            The number of newly registered constraints.
        """
        count = 0
        for c in constraints:
            if self.register(c):
                count += 1
        return count

    def get(self, constraint_id: str) -> Optional[Constraint]:
        return self._constraints.get(constraint_id)

    def get_metadata(self, constraint_id: str) -> Optional[ConstraintMetadata]:
        return self._metadata.get(constraint_id)

    def get_by_domain(self, domain: str) -> list[Constraint]:
        return list(self._by_domain.get(domain, []))

    def get_by_ids(self, ids: list[str]) -> list[Constraint]:
        result: list[Constraint] = []
        for cid in ids:
            c = self._constraints.get(cid)
            if c is not None:
                result.append(c)
        return result

    def get_all(self) -> list[Constraint]:
        return list(self._constraints.values())

    def get_all_domains(self) -> set[str]:
        return set(self._by_domain.keys())

    def count(self) -> int:
        return len(self._constraints)

    def has(self, constraint_id: str) -> bool:
        return constraint_id in self._constraints

    def clear(self) -> None:
        self._constraints.clear()
        self._by_domain.clear()
        self._metadata.clear()
