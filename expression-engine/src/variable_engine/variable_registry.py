from __future__ import annotations

from typing import Optional

from .variable import Variable


class VariableRegistry:
    """Central registry for all variables discovered during extraction.

    Responsibilities:
        * Store variables keyed by their unique ID.
        * Prevent duplicates (same ID cannot be registered twice).
        * Look up by ID or by name.
    """

    def __init__(self) -> None:
        self._by_id: dict[str, Variable] = {}
        self._by_name: dict[str, list[Variable]] = {}

    def register(self, variable: Variable) -> bool:
        """Register a variable.

        Returns:
            ``True`` if the variable was newly registered,
            ``False`` if a variable with the same ID already exists.
        """
        if variable.id in self._by_id:
            return False

        self._by_id[variable.id] = variable
        name = variable.name
        if name not in self._by_name:
            self._by_name[name] = []
        self._by_name[name].append(variable)
        return True

    def lookup(self, var_id: str) -> Optional[Variable]:
        return self._by_id.get(var_id)

    def lookup_by_name(self, name: str) -> list[Variable]:
        return list(self._by_name.get(name, []))

    def get_all(self) -> list[Variable]:
        return list(self._by_id.values())

    def count(self) -> int:
        return len(self._by_id)

    def clear(self) -> None:
        self._by_id.clear()
        self._by_name.clear()
