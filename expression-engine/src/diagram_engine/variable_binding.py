from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class BindingScope(Enum):
    GEOMETRY = "geometry"
    COORDINATE = "coordinate"
    MEASUREMENT = "measurement"
    ANGLE = "angle"
    RADIUS = "radius"
    LABEL = "label"
    POSITION = "position"
    SIZE = "size"
    CUSTOM = "custom"


@dataclass(frozen=True)
class VariableBinding:
    """Links a primitive property to a named variable.

    Attributes:
        primitive_id: The ``id`` of the primitive being bound.
        property_name: The property path on the primitive
            (e.g. ``"radius"``, ``"x"``, ``"length"``).
        variable_name: The variable name in the ``VariableGraph``.
        scope: The semantic scope of this binding.
        default_value: Fallback value when no variable assignment is provided.
        description: Human-readable description of the binding.
    """
    primitive_id: str
    property_name: str
    variable_name: str
    scope: BindingScope = BindingScope.CUSTOM
    default_value: Optional[Any] = None
    description: str = ""

    def binding_key(self) -> str:
        return f"{self.primitive_id}.{self.property_name}"

    def to_dict(self) -> dict:
        return {
            "primitive_id": self.primitive_id,
            "property_name": self.property_name,
            "variable_name": self.variable_name,
            "scope": self.scope.value,
            "default_value": self.default_value,
            "description": self.description,
        }


class VariableBindingEngine:
    """Manages bindings between diagram primitives and variables.

    The engine allows:
    * Binding a primitive property to a variable name.
    * Resolving concrete values from a variable assignment dictionary.
    * Exporting bindings to a ``VariableGraph`` for integration with
      the constraint engine.
    """

    def __init__(self) -> None:
        self._bindings: dict[str, VariableBinding] = {}

    # ---- binding management ----------------------------------------------

    def bind(
        self,
        primitive_id: str,
        property_name: str,
        variable_name: str,
        scope: BindingScope = BindingScope.CUSTOM,
        default_value: Any = None,
        description: str = "",
    ) -> VariableBinding:
        binding = VariableBinding(
            primitive_id=primitive_id,
            property_name=property_name,
            variable_name=variable_name,
            scope=scope,
            default_value=default_value,
            description=description,
        )
        key = binding.binding_key()
        self._bindings[key] = binding
        return binding

    def unbind(self, primitive_id: str, property_name: str) -> None:
        key = f"{primitive_id}.{property_name}"
        self._bindings.pop(key, None)

    def unbind_all_for_primitive(self, primitive_id: str) -> None:
        keys = [
            k for k in self._bindings
            if k.startswith(f"{primitive_id}.")
        ]
        for k in keys:
            self._bindings.pop(k, None)

    def clear(self) -> None:
        self._bindings.clear()

    # ---- query -----------------------------------------------------------

    def get_binding(
        self, primitive_id: str, property_name: str,
    ) -> Optional[VariableBinding]:
        key = f"{primitive_id}.{property_name}"
        return self._bindings.get(key)

    def get_bindings_for_primitive(
        self, primitive_id: str,
    ) -> list[VariableBinding]:
        return [
            b for b in self._bindings.values()
            if b.primitive_id == primitive_id
        ]

    def get_bindings_by_scope(self, scope: BindingScope) -> list[VariableBinding]:
        return [b for b in self._bindings.values() if b.scope == scope]

    def get_all_bindings(self) -> list[VariableBinding]:
        return list(self._bindings.values())

    def binding_count(self) -> int:
        return len(self._bindings)

    def has_binding(self, primitive_id: str, property_name: str) -> bool:
        return self.get_binding(primitive_id, property_name) is not None

    # ---- resolution ------------------------------------------------------

    def resolve(
        self,
        primitive_id: str,
        property_name: str,
        variables: dict[str, Any] | None = None,
    ) -> Any:
        binding = self.get_binding(primitive_id, property_name)
        if binding is None:
            return None
        if variables and binding.variable_name in variables:
            return variables[binding.variable_name]
        return binding.default_value

    def resolve_all(
        self,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for binding in self._bindings.values():
            key = binding.binding_key()
            if variables and binding.variable_name in variables:
                result[key] = variables[binding.variable_name]
            else:
                result[key] = binding.default_value
        return result

    # ---- export ----------------------------------------------------------

    def get_variable_names(self) -> list[str]:
        seen: set[str] = set()
        names: list[str] = []
        for b in self._bindings.values():
            if b.variable_name not in seen:
                seen.add(b.variable_name)
                names.append(b.variable_name)
        return names

    def to_dict(self) -> dict:
        return {
            "bindings": [b.to_dict() for b in self._bindings.values()],
            "variable_names": self.get_variable_names(),
        }
