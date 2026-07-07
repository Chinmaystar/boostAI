from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .diagram_template import (
    DIAGRAM_TYPE_CUSTOM, DiagramTemplate, TemplateMetadata,
)
from .primitives import BoundingBox


class FallbackReason(Enum):
    NO_VECTOR_DATA = "no_vector_data"
    UNSUPPORTED_DIAGRAM_TYPE = "unsupported_diagram_type"
    INCOMPLETE_PRIMITIVES = "incomplete_primitives"
    CORRUPTED_DATA = "corrupted_data"
    EXTRACTION_ERROR = "extraction_error"
    PLUGIN_NOT_FOUND = "plugin_not_found"
    UNKNOWN = "unknown"


@dataclass
class FallbackDiagram:
    """Represents a diagram that could not be parameterized.

    These diagrams are kept as PNG references and marked as
    non-parameterized to prevent silent incorrect output.
    """
    template_id: str
    reason: FallbackReason
    message: str
    image_path: Optional[str] = None
    original_bbox: Optional[dict[str, float]] = None
    original_metadata: Optional[dict[str, Any]] = None


class FallbackHandler:
    """Handles diagrams that cannot be reconstructed from vector primitives.

    The handler creates a minimal ``DiagramTemplate`` that is
    explicitly marked as *not* parameterized, with a reference to
    the original PNG image.  This prevents the system from silently
    producing incorrect output.
    """

    def __init__(self) -> None:
        self._fallbacks: dict[str, FallbackDiagram] = {}

    def create_fallback_template(
        self,
        template_id: str,
        reason: FallbackReason,
        message: str,
        image_path: str | None = None,
        original_bbox: dict[str, float] | None = None,
        original_metadata: dict[str, Any] | None = None,
    ) -> DiagramTemplate:
        metadata = TemplateMetadata(
            template_id=template_id,
            diagram_type=DIAGRAM_TYPE_CUSTOM,
            display_name=f"Fallback: {template_id}",
            description=message,
            plugin_source="fallback_handler",
        )

        fallback = FallbackDiagram(
            template_id=template_id,
            reason=reason,
            message=message,
            image_path=image_path,
            original_bbox=original_bbox,
            original_metadata=original_metadata,
        )
        self._fallbacks[template_id] = fallback

        template = DiagramTemplate(
            metadata=metadata,
            is_parameterized=False,
            fallback_image_path=image_path,
        )
        template._fallback_reason = reason
        return template

    def get_fallback(self, template_id: str) -> Optional[FallbackDiagram]:
        return self._fallbacks.get(template_id)

    def list_fallbacks(self) -> list[FallbackDiagram]:
        return list(self._fallbacks.values())

    def clear(self) -> None:
        self._fallbacks.clear()
