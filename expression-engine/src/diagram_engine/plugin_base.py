from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from .diagram_template import DiagramTemplate, DiagramTemplateBuilder
from .primitives import BoundingBox


class PluginRegistrationError(Exception):
    """Raised when a diagram plugin cannot be registered."""


class DiagramPlugin(ABC):
    """Base class for diagram type plugins.

    Each plugin is responsible for:
    * Detecting whether it can handle a given input.
    * Building a ``DiagramTemplate`` from structured input data.
    * Providing metadata for registration.
    """

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Unique name for this plugin."""
        ...

    @property
    @abstractmethod
    def supported_diagram_types(self) -> list[str]:
        """Diagram type strings this plugin can handle."""
        ...

    @abstractmethod
    def can_handle_input(self, input_data: dict[str, Any]) -> bool:
        """Return ``True`` if this plugin can process the input data."""
        ...

    @abstractmethod
    def build_template(
        self,
        input_data: dict[str, Any],
        template_id: str | None = None,
    ) -> DiagramTemplate:
        """Build a ``DiagramTemplate`` from structured input data.

        Args:
            input_data: A dictionary with keys like ``"drawings"``,
                ``"text_labels"``, ``"bbox"``, ``"metadata"``, etc.
            template_id: Optional override for the template ID.

        Returns:
            A fully constructed ``DiagramTemplate``.
        """
        ...


class DiagramPluginRegistry:
    """Registry for diagram plugins.

    Follows the same pattern as ``GeneratorPluginRegistry``.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, DiagramPlugin] = {}

    def register(self, plugin: DiagramPlugin) -> None:
        name = plugin.plugin_name
        if name in self._plugins:
            raise PluginRegistrationError(
                f"Plugin '{name}' is already registered."
            )
        self._plugins[name] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def get(self, name: str) -> Optional[DiagramPlugin]:
        return self._plugins.get(name)

    def get_for_input(self, input_data: dict[str, Any]) -> Optional[DiagramPlugin]:
        for plugin in self._plugins.values():
            if plugin.can_handle_input(input_data):
                return plugin
        return None

    def get_for_type(self, diagram_type: str) -> Optional[DiagramPlugin]:
        for plugin in self._plugins.values():
            if diagram_type in plugin.supported_diagram_types:
                return plugin
        return None

    def has(self, name: str) -> bool:
        return name in self._plugins

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())

    def clear(self) -> None:
        self._plugins.clear()

    @property
    def count(self) -> int:
        return len(self._plugins)
