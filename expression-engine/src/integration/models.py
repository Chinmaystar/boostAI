from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from src.semantic_engine import SemanticTemplate, TemplateFamily, DifficultyLevel
from src.constraint_engine import ConstraintValidationResult
from src.generator import GeneratedQuestion, GenerationStats
from src.diagram_engine import DiagramTemplate


@dataclass(frozen=True)
class PipelineStep:
    name: str
    duration_ms: float
    success: bool

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "success": self.success,
        }


@dataclass
class PipelineMetadata:
    pipeline_version: str = "1.0.0"
    pipeline_name: str = "BoostAI Deterministic Pipeline"
    created_at: str = ""
    generation_time_ms: float = 0.0
    pipeline_steps: list[PipelineStep] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "pipeline_version": self.pipeline_version,
            "pipeline_name": self.pipeline_name,
            "created_at": self.created_at,
            "generation_time_ms": self.generation_time_ms,
            "pipeline_steps": [s.to_dict() for s in self.pipeline_steps],
        }


@dataclass
class IntermediateResults:
    ast: Any = None
    canonical_result: Any = None
    template_signature: Any = None
    discovery_result: Any = None
    symbolic_expr: Any = None

    def to_dict(self) -> dict:
        return {
            "has_ast": self.ast is not None,
            "has_canonical": self.canonical_result is not None,
            "has_signature": self.template_signature is not None,
            "has_discovery": self.discovery_result is not None,
            "has_symbolic": self.symbolic_expr is not None,
        }


@dataclass
class DiagramSpec:
    type: str = "custom"
    properties: dict[str, Any] = field(default_factory=dict)
    variable_bindings: dict[str, str] | None = None
    point_id_suffix: str = ""

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "properties": dict(self.properties),
            "variable_bindings": dict(self.variable_bindings) if self.variable_bindings else None,
        }


@dataclass
class QuestionSource:
    text: str
    main_variable: str | None = None
    diagram_specs: list[DiagramSpec] | None = None
    metadata_overrides: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "main_variable": self.main_variable,
            "diagram_count": len(self.diagram_specs) if self.diagram_specs else 0,
            "has_overrides": self.metadata_overrides is not None,
        }


@dataclass(frozen=True)
class GeneratedQuestionPackage:
    question_id: str
    template_id: str
    version: str

    source_text: str
    rendered_question: str
    variable_assignments: dict[str, Any]
    expected_answer: Any
    semantic_template: SemanticTemplate
    validation_report: ConstraintValidationResult | None

    diagram_templates: list[DiagramTemplate]
    rendered_svgs: list[str]

    metadata: PipelineMetadata
    generation_stats: GenerationStats
    intermediate_results: IntermediateResults

    @property
    def has_diagrams(self) -> bool:
        return len(self.diagram_templates) > 0

    @property
    def is_valid(self) -> bool:
        if self.validation_report is None:
            return self.generation_stats.success
        return self.validation_report.valid and self.generation_stats.success

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "template_id": self.template_id,
            "version": self.version,
            "source_text": self.source_text,
            "rendered_question": self.rendered_question,
            "variable_assignments": dict(self.variable_assignments),
            "expected_answer": str(self.expected_answer) if self.expected_answer is not None else None,
            "semantic_template": self.semantic_template.to_dict(),
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "diagram_count": len(self.diagram_templates),
            "svg_count": len(self.rendered_svgs),
            "metadata": self.metadata.to_dict(),
            "generation_stats": self._stats_to_dict(),
            "intermediate_results": self.intermediate_results.to_dict(),
            "is_valid": self.is_valid,
            "has_diagrams": self.has_diagrams,
        }

    def get_svg(self, index: int = 0) -> str | None:
        if 0 <= index < len(self.rendered_svgs):
            return self.rendered_svgs[index]
        return None

    def get_diagram(self, index: int = 0) -> DiagramTemplate | None:
        if 0 <= index < len(self.diagram_templates):
            return self.diagram_templates[index]
        return None

    def _stats_to_dict(self) -> dict:
        return {
            "attempts": self.generation_stats.attempts,
            "retries": self.generation_stats.retries,
            "total_time_ms": self.generation_stats.total_time_ms,
            "success": self.generation_stats.success,
        }
