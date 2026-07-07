from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.semantic_engine import (
    DifficultyLevel, GeneratorType, SolverType, TemplateFamily,
    SemanticMetadata,
)
from src.constraint_engine import ConstraintValidationResult


@dataclass(frozen=True)
class GenerationStats:
    attempts: int = 0
    retries: int = 0
    total_time_ms: float = 0.0
    validation_calls: int = 0
    constraint_failures: dict[str, int] = field(default_factory=dict)
    success: bool = False


@dataclass(frozen=True)
class GeneratedQuestion:
    question_id: str
    template_id: str
    version: str
    template_family: TemplateFamily
    generator_type: GeneratorType
    solver_type: SolverType
    concept: str
    difficulty: DifficultyLevel
    rendered_question: str
    variable_assignments: dict[str, Any]
    expected_answer: Any
    metadata: SemanticMetadata
    generation_stats: GenerationStats
    validation_report: ConstraintValidationResult | None = None
