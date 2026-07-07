from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.semantic_engine import SemanticTemplate, TemplateFamily
from src.template_engine import TemplateSignature

from .question import GeneratedQuestion


class GeneratorPlugin(ABC):
    @property
    @abstractmethod
    def family(self) -> TemplateFamily:
        ...

    @abstractmethod
    def generate(
        self,
        template: SemanticTemplate,
        signature: TemplateSignature,
        **kwargs: Any,
    ) -> GeneratedQuestion:
        ...

    @abstractmethod
    def can_handle(self, template: SemanticTemplate) -> bool:
        ...


class GeneratorPluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, GeneratorPlugin] = {}

    def register(self, plugin: GeneratorPlugin) -> None:
        key = plugin.family.value
        if key in self._plugins:
            from .errors import PluginRegistrationError
            raise PluginRegistrationError(
                f"Plugin for family '{key}' is already registered"
            )
        self._plugins[key] = plugin

    def unregister(self, family: TemplateFamily) -> None:
        self._plugins.pop(family.value, None)

    def get(self, family: TemplateFamily) -> GeneratorPlugin | None:
        return self._plugins.get(family.value)

    def get_for_template(
        self, template: SemanticTemplate,
    ) -> GeneratorPlugin | None:
        for plugin in self._plugins.values():
            if plugin.can_handle(template):
                return plugin
        return None

    def has(self, family: TemplateFamily) -> bool:
        return family.value in self._plugins

    def clear(self) -> None:
        self._plugins.clear()

    @property
    def families(self) -> list[TemplateFamily]:
        return [TemplateFamily(k) for k in self._plugins]
