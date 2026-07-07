from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from .backend import SymbolicBackend
from .expression import SymbolicExpr
from .exceptions import PluginRegistrationError, BackendNotFound


@dataclass
class PluginMetadata:
    """Metadata for a registered plugin."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    dependencies: list[str] = field(default_factory=list)


class SymbolicPlugin(ABC):
    """Base class for symbolic plugins.

    Implementations can provide new:
    - Symbolic operations
    - Mathematical domains
    - Equation solvers
    - Simplifiers
    """

    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""

    @abstractmethod
    def initialize(self, backend: SymbolicBackend) -> None:
        """Initialize the plugin with the active backend."""

    @abstractmethod
    def operations(self) -> dict[str, callable]:
        """Return a dict of operation names to callables."""


class SymbolicPluginRegistry:
    """Registry for symbolic plugins.

    Plugins can register new operations, solvers, and simplifiers
    without modifying the core engine.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, SymbolicPlugin] = {}
        self._operations: dict[str, callable] = {}
        self._solvers: dict[str, callable] = {}
        self._simplifiers: list[callable] = []

    def register(self, plugin: SymbolicPlugin,
                 backend: SymbolicBackend
                 ) -> None:
        """Register a plugin and activate it.

        Parameters
        ----------
        plugin : SymbolicPlugin
            Plugin instance.
        backend : SymbolicBackend
            Active backend to pass to the plugin.
        """
        meta = plugin.metadata()
        if meta.name in self._plugins:
            raise PluginRegistrationError(
                f"Plugin '{meta.name}' is already registered")
        plugin.initialize(backend)
        self._plugins[meta.name] = plugin
        for op_name, op_fn in plugin.operations().items():
            self._operations[op_name] = op_fn
        if hasattr(plugin, "solvers"):
            for name, solver in plugin.solvers().items():
                self._solvers[name] = solver
        if hasattr(plugin, "simplifiers"):
            for simplifier in plugin.simplifiers():
                self._simplifiers.append(simplifier)

    def unregister(self, name: str) -> None:
        """Unregister a plugin and remove its operations."""
        plugin = self._plugins.pop(name, None)
        if plugin is None:
            raise PluginRegistrationError(
                f"Plugin '{name}' is not registered")
        for op_name in plugin.operations():
            self._operations.pop(op_name, None)

    def get_plugin(self, name: str) -> SymbolicPlugin:
        """Get a registered plugin by name."""
        plugin = self._plugins.get(name)
        if plugin is None:
            raise BackendNotFound(f"Plugin '{name}' not found")
        return plugin

    def get_operation(self, name: str) -> callable:
        """Get a registered operation by name."""
        op = self._operations.get(name)
        if op is None:
            raise BackendNotFound(f"Operation '{name}' not found")
        return op

    def get_solver(self, name: str) -> callable:
        """Get a registered solver by name."""
        solver = self._solvers.get(name)
        if solver is None:
            raise BackendNotFound(f"Solver '{name}' not found")
        return solver

    @property
    def plugins(self) -> dict[str, SymbolicPlugin]:
        return dict(self._plugins)

    @property
    def operations(self) -> dict[str, callable]:
        return dict(self._operations)

    @property
    def solvers(self) -> dict[str, callable]:
        return dict(self._solvers)

    @property
    def simplifiers(self) -> list[callable]:
        return list(self._simplifiers)

    def clear(self) -> None:
        """Remove all registered plugins."""
        self._plugins.clear()
        self._operations.clear()
        self._solvers.clear()
        self._simplifiers.clear()
