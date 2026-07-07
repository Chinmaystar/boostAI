from __future__ import annotations


class GeneratorError(Exception):
    """Base exception for all generator framework errors."""


class NoValidAssignmentError(GeneratorError):
    """Raised when retry manager exhausts attempts finding valid values."""


class QuestionAssemblyError(GeneratorError):
    """Raised when question assembly fails (e.g. invalid pattern)."""


class PluginRegistrationError(GeneratorError):
    """Raised when a plugin cannot be registered."""


class MissingDependencyError(GeneratorError):
    """Raised when a required engine or component is not available."""


class UnsolvedError(GeneratorError):
    """Raised when expected answer cannot be computed."""
