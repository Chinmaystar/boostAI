from __future__ import annotations

from typing import Any, Optional

from src.template_engine import TemplateSignature
from src.variable_engine import VariableGraph

from .semantic_template import (
    SemanticTemplate,
    SemanticMetadata,
    TemplateFamily,
    TemplateStatus,
    DifficultyLevel,
    GeneratorType,
    SolverType,
    DiagramType,
    ConstraintType,
    LearningOutcome,
)


# =========================================================================
# Deterministic mapping tables
# =========================================================================

_KNOWN_TEMPLATE_MAP: dict[str, dict[str, Any]] = {
    "LinearEquation": {
        "family": TemplateFamily.ALGEBRA,
        "chapter": "Linear Equations",
        "topic": "Solving Linear Equations",
        "concept": "Solve ax + b = c in one variable",
        "constraint_types": (ConstraintType.RANGE, ConstraintType.POSITIVITY, ConstraintType.INTEGER),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.LINEAR,
        "generator_type": GeneratorType.ALGEBRAIC,
        "tags": ("linear", "equation", "one-variable", "algebra"),
        "learning_outcomes": (
            LearningOutcome("LO-SLE-01", "Solve linear equations of the form ax + b = c"),
            LearningOutcome("LO-SLE-02", "Identify the variable, coefficient, and constant terms"),
        ),
    },
    "SimpleLinearEquation": {
        "family": TemplateFamily.ALGEBRA,
        "chapter": "Linear Equations",
        "topic": "Basic Equations",
        "concept": "Solve x + a = b",
        "constraint_types": (ConstraintType.RANGE, ConstraintType.POSITIVITY),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.LINEAR,
        "generator_type": GeneratorType.ALGEBRAIC,
        "tags": ("linear", "equation", "simple", "algebra"),
        "learning_outcomes": (
            LearningOutcome("LO-BE-01", "Solve simple equations of the form x + a = b"),
        ),
    },
    "DistributiveMultiplication": {
        "family": TemplateFamily.ALGEBRA,
        "chapter": "Linear Equations",
        "topic": "Distributive Property",
        "concept": "Expand and simplify a(b + x)",
        "constraint_types": (ConstraintType.RANGE, ConstraintType.POSITIVITY),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.TRANSFORMATION,
        "generator_type": GeneratorType.ALGEBRAIC,
        "tags": ("distributive", "multiplication", "expansion", "algebra"),
        "learning_outcomes": (
            LearningOutcome("LO-DP-01", "Apply the distributive property to expand expressions"),
            LearningOutcome("LO-DP-02", "Simplify products involving variables and constants"),
        ),
    },
    "ScalarMultiplication": {
        "family": TemplateFamily.ALGEBRA,
        "chapter": "Algebraic Expressions",
        "topic": "Multiplication",
        "concept": "Multiply a constant and a variable",
        "constraint_types": (ConstraintType.RANGE, ConstraintType.INTEGER),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.ARITHMETIC_OP,
        "generator_type": GeneratorType.ALGEBRAIC,
        "tags": ("multiplication", "monomial", "algebra"),
        "learning_outcomes": (
            LearningOutcome("LO-SM-01", "Multiply a constant by a variable"),
        ),
    },
    "LinearExpression": {
        "family": TemplateFamily.ALGEBRA,
        "chapter": "Algebraic Expressions",
        "topic": "Linear Expressions",
        "concept": "Evaluate and simplify ax + b",
        "constraint_types": (ConstraintType.RANGE, ConstraintType.POSITIVITY),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.EVALUATION,
        "generator_type": GeneratorType.ALGEBRAIC,
        "tags": ("expression", "linear", "algebra"),
        "learning_outcomes": (
            LearningOutcome("LO-LE-01", "Evaluate linear expressions for given values"),
        ),
    },
    "ConstantExpression": {
        "family": TemplateFamily.ARITHMETIC,
        "chapter": "Numbers and Operations",
        "topic": "Evaluation",
        "concept": "Evaluate a constant arithmetic expression",
        "constraint_types": (ConstraintType.INTEGER,),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.EVALUATION,
        "generator_type": GeneratorType.ARITHMETIC,
        "tags": ("constant", "evaluation", "arithmetic"),
        "learning_outcomes": (
            LearningOutcome("LO-CE-01", "Evaluate constant arithmetic expressions"),
        ),
    },
    "VariableExpression": {
        "family": TemplateFamily.ALGEBRA,
        "chapter": "Algebraic Expressions",
        "topic": "Variables",
        "concept": "Identify and work with variable terms",
        "constraint_types": (),
        "diagram_type": DiagramType.NONE,
        "solver_type": SolverType.NONE,
        "generator_type": GeneratorType.ALGEBRAIC,
        "tags": ("variable", "expression", "algebra"),
        "learning_outcomes": (
            LearningOutcome("LO-VE-01", "Recognise variable terms in expressions"),
        ),
    },
}

_FAMILY_GENERATOR_MAP: dict[str, GeneratorType] = {
    "Algebra": GeneratorType.ALGEBRAIC,
    "Expression": GeneratorType.ALGEBRAIC,
}

_FAMILY_ENUM_MAP: dict[str, TemplateFamily] = {
    "Algebra": TemplateFamily.ALGEBRA,
    "Expression": TemplateFamily.ALGEBRA,
}

_DEFAULT_FAMILY = TemplateFamily.ALGEBRA
_DEFAULT_GENERATOR = GeneratorType.ALGEBRAIC


# =========================================================================
# Builder
# =========================================================================

class SemanticTemplateBuilder:
    """Builds a ``SemanticTemplate`` from a ``TemplateSignature`` and
    ``VariableGraph`` using pure deterministic mapping.

    Usage::

        builder = SemanticTemplateBuilder()
        template = builder.build(signature, variable_graph)
    """

    def __init__(self, overrides: Optional[dict[str, Any]] = None) -> None:
        """Initialise the builder with optional field overrides.

        Args:
            overrides: A dict of field names to values that will
                override any automatically-derived values. Supported
                keys include ``chapter``, ``topic``, ``concept``,
                ``difficulty``, ``subject``, ``tags``, etc.
        """
        self._overrides: dict[str, Any] = overrides or {}

    def build(
        self,
        signature: TemplateSignature,
        variable_graph: VariableGraph | None = None,
    ) -> SemanticTemplate:
        """Build a fully-populated ``SemanticTemplate``.

        Args:
            signature: The ``TemplateSignature`` from the template engine.
            variable_graph: The ``VariableGraph`` from the variable engine.

        Returns:
            A ``SemanticTemplate`` instance with all fields populated.
        """
        tid = signature.template_id
        family_str = signature.template_family

        known = _KNOWN_TEMPLATE_MAP.get(tid, {})

        family = known.get("family") or _FAMILY_ENUM_MAP.get(family_str, _DEFAULT_FAMILY)

        chapter = self._overrides.get("chapter", known.get("chapter", ""))
        topic = self._overrides.get("topic", known.get("topic", ""))
        concept = self._overrides.get("concept", known.get("concept", ""))
        difficulty_str = self._overrides.get("difficulty", "medium")

        if isinstance(difficulty_str, str):
            difficulty = next(
                (d for d in DifficultyLevel if d.value == difficulty_str),
                DifficultyLevel.MEDIUM,
            )
        else:
            difficulty = difficulty_str

        constraint_types = known.get("constraint_types", ())
        diagram_type = known.get("diagram_type", DiagramType.NONE)
        solver_type = known.get("solver_type", SolverType.EVALUATION)
        generator_type = known.get("generator_type") or _FAMILY_GENERATOR_MAP.get(family_str, _DEFAULT_GENERATOR)
        subject = self._overrides.get("subject", "Mathematics")
        tags = tuple(self._overrides.get("tags", known.get("tags", ())))
        learning_outcomes = tuple(self._overrides.get(
            "learning_outcomes", known.get("learning_outcomes", ())))

        display_name = self._overrides.get("display_name",
            known.get("display_name", tid))
        internal_name = self._overrides.get("internal_name",
            known.get("internal_name", tid.lower()))

        status_str = self._overrides.get("status", "draft")
        if isinstance(status_str, str):
            status = next(
                (s for s in TemplateStatus if s.value == status_str),
                TemplateStatus.DRAFT,
            )
        else:
            status = status_str

        confidence = self._overrides.get("confidence_score", signature.confidence)
        plugin_source = self._overrides.get("plugin_source", "builtin")
        review_status = self._overrides.get("review_status", "unreviewed")

        metadata = SemanticMetadata(
            template_id=tid,
            display_name=display_name,
            internal_name=internal_name,
            version=self._overrides.get("version", "1.0.0"),
            status=status,
            confidence_score=confidence,
            plugin_source=plugin_source,
            review_status=review_status,
        )

        return SemanticTemplate(
            template_id=tid,
            template_family=family,
            subject=subject,
            chapter=chapter,
            topic=topic,
            concept=concept,
            difficulty=difficulty,
            variable_graph=variable_graph,
            expected_constraint_types=constraint_types,
            generator_type=generator_type,
            solver_type=solver_type,
            diagram_type=diagram_type,
            metadata=metadata,
            template_version="1.0.0",
            tags=tags,
            learning_outcomes=learning_outcomes,
        )
