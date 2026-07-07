from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TemplateFamily(Enum):
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    COORDINATE_GEOMETRY = "coordinate_geometry"
    MENSURATION = "mensuration"
    STATISTICS = "statistics"
    PROBABILITY = "probability"
    TRIGONOMETRY = "trigonometry"
    CALCULUS = "calculus"
    MATRICES = "matrices"
    VECTORS = "vectors"
    GRAPHS = "graphs"
    NUMBER_SYSTEM = "number_system"
    DATA_INTERPRETATION = "data_interpretation"


class TemplateStatus(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GeneratorType(Enum):
    NUMERIC = "numeric"
    ALGEBRAIC = "algebraic"
    GEOMETRIC = "geometric"
    STATISTICAL = "statistical"
    MIXED = "mixed"
    ARITHMETIC = "arithmetic"
    TRIGONOMETRIC = "trigonometric"
    CALCULUS = "calculus"
    MATRIX = "matrix"
    GRAPH = "graph"
    DATA = "data"


class SolverType(Enum):
    NONE = "none"
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    SIMULTANEOUS = "simultaneous"
    ARITHMETIC_OP = "arithmetic_op"
    GEOMETRIC_FORMULA = "geometric_formula"
    TRIGONOMETRIC = "trigonometric"
    CALCULUS = "calculus"
    STATISTICAL = "statistical"
    PROBABILISTIC = "probabilistic"
    MATRIX = "matrix"
    GRAPHICAL = "graphical"
    EVALUATION = "evaluation"
    TRANSFORMATION = "transformation"


class DiagramType(Enum):
    NONE = "none"
    LINE = "line"
    TRIANGLE = "triangle"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    COORDINATE_PLANE = "coordinate_plane"
    NUMBER_LINE = "number_line"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    VENN = "venn"
    GRAPH = "graph"
    SHAPE = "shape"


class ConstraintType(Enum):
    RANGE = "range"
    SET = "set"
    POSITIVITY = "positivity"
    INTEGER = "integer"
    PARITY = "parity"
    MULTIPLE = "multiple"
    PRIME = "prime"
    FRACTION = "fraction"
    DECIMAL = "decimal"
    INEQUALITY = "inequality"
    PERFECT_SQUARE = "perfect_square"
    COPRIME = "coprime"


@dataclass(frozen=True)
class SemanticMetadata:
    """Metadata attached to every semantic template.

    Attributes:
        template_id: Unique identifier for the template.
        display_name: Human-readable name for UIs.
        internal_name: Internal code name.
        version: Version string for change tracking.
        created_at: ISO-8601 UTC timestamp of creation.
        updated_at: ISO-8601 UTC timestamp of last modification.
        status: Lifecycle status (draft, approved, deprecated).
        confidence_score: Float in [0.0, 1.0] indicating confidence.
        plugin_source: Name of the plugin/extension that created this.
        review_status: Review lifecycle indicator.
    """
    template_id: str
    display_name: str = ""
    internal_name: str = ""
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: _now_iso())
    updated_at: str = field(default_factory=lambda: _now_iso())
    status: TemplateStatus = TemplateStatus.DRAFT
    confidence_score: float = 1.0
    plugin_source: str = "builtin"
    review_status: str = "unreviewed"

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "display_name": self.display_name,
            "internal_name": self.internal_name,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "plugin_source": self.plugin_source,
            "review_status": self.review_status,
        }


@dataclass(frozen=True)
class LearningOutcome:
    """A single measurable learning outcome."""
    code: str
    description: str

    def to_dict(self) -> dict:
        return {"code": self.code, "description": self.description}


@dataclass(frozen=True)
class SemanticTemplate:
    """Fully-semantic template bridging structural patterns to
    curriculum metadata.

    This is the final output of the expression-analysis pipeline.
    Future systems (constraint engine, question generator,
    difficulty engine, diagram renderer) consume this model exclusively.

    Attributes:
        template_id: Human-readable ID (e.g. ``"LinearEquation"``).
        template_family: High-level mathematical family.
        subject: Subject area (e.g. ``"Mathematics"``).
        chapter: Textbook chapter name.
        topic: Section topic within the chapter.
        concept: Specific concept being exercised.
        difficulty: Target difficulty level.
        variable_graph: The ``VariableGraph`` produced by the
            ``VariableDiscoveryVisitor``.
        expected_constraint_types: Constraint types this template
            expects (e.g. range, positivity, integer).
        generator_type: The kind of generator that can produce
            variants of this template.
        solver_type: The strategy required to solve expressions
            matching this template.
        diagram_type: The kind of diagram (if any) associated.
        metadata: Full ``SemanticMetadata`` instance.
        template_version: Schema version of the semantic template model.
        tags: Categorisation tags.
        learning_outcomes: Tuple of ``LearningOutcome`` instances.
    """
    template_id: str
    template_family: TemplateFamily
    subject: str = "Mathematics"
    chapter: str = ""
    topic: str = ""
    concept: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    variable_graph: object = None
    expected_constraint_types: tuple[ConstraintType, ...] = ()
    generator_type: GeneratorType = GeneratorType.ALGEBRAIC
    solver_type: SolverType = SolverType.LINEAR
    diagram_type: DiagramType = DiagramType.NONE
    metadata: SemanticMetadata = None
    template_version: str = "1.0.0"
    tags: tuple[str, ...] = ()
    learning_outcomes: tuple[LearningOutcome, ...] = ()

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "template_family": self.template_family.value,
            "subject": self.subject,
            "chapter": self.chapter,
            "topic": self.topic,
            "concept": self.concept,
            "difficulty": self.difficulty.value,
            "expected_constraint_types": [c.value for c in self.expected_constraint_types],
            "generator_type": self.generator_type.value,
            "solver_type": self.solver_type.value,
            "diagram_type": self.diagram_type.value,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "template_version": self.template_version,
            "tags": list(self.tags),
            "learning_outcomes": [lo.to_dict() for lo in self.learning_outcomes],
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
