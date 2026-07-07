from __future__ import annotations

import pytest

from src.semantic_engine import (
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
    SemanticTemplateRegistry,
    SemanticTemplateBuilder,
)
from src.template_engine import TemplateSignature, TemplateSignatureBuilder
from src.variable_engine import VariableGraph, VariableDiscoveryVisitor
from src.canonicalizer import Canonicalizer
from src.tokenizer import Tokenizer
from src.lexer import Lexer
from src.parser import Parser


# =========================================================================
# Helpers
# =========================================================================

def canonical_ast(expr: str):
    tokens = Tokenizer(expr).tokenize()
    Lexer().validate(tokens)
    ast = Parser(tokens).parse()
    return Canonicalizer(rename_variables=False).canonicalize(ast).tree


def build_signature(expr: str) -> TemplateSignature:
    return TemplateSignatureBuilder().build(canonical_ast(expr))


def discover_variables(expr: str):
    ast = canonical_ast(expr)
    return VariableDiscoveryVisitor(expression=expr).discover(ast)


# =========================================================================
# Enum Tests
# =========================================================================

class TestEnums:

    def test_template_family_values(self):
        assert TemplateFamily.ALGEBRA.value == "algebra"
        assert TemplateFamily.ARITHMETIC.value == "arithmetic"
        assert TemplateFamily.GEOMETRY.value == "geometry"

    def test_template_family_all_members(self):
        expected = {
            "ARITHMETIC", "ALGEBRA", "GEOMETRY", "COORDINATE_GEOMETRY",
            "MENSURATION", "STATISTICS", "PROBABILITY", "TRIGONOMETRY",
            "CALCULUS", "MATRICES", "VECTORS", "GRAPHS",
            "NUMBER_SYSTEM", "DATA_INTERPRETATION",
        }
        actual = set(TemplateFamily.__members__)
        assert actual == expected

    def test_template_status_values(self):
        assert TemplateStatus.DRAFT.value == "draft"
        assert TemplateStatus.APPROVED.value == "approved"
        assert TemplateStatus.DEPRECATED.value == "deprecated"

    def test_difficulty_level_values(self):
        assert DifficultyLevel.EASY.value == "easy"
        assert DifficultyLevel.MEDIUM.value == "medium"
        assert DifficultyLevel.HARD.value == "hard"

    def test_generator_type_values(self):
        assert GeneratorType.ALGEBRAIC.value == "algebraic"
        assert GeneratorType.NUMERIC.value == "numeric"
        assert GeneratorType.GEOMETRIC.value == "geometric"

    def test_solver_type_values(self):
        assert SolverType.LINEAR.value == "linear"
        assert SolverType.EVALUATION.value == "evaluation"
        assert SolverType.NONE.value == "none"

    def test_diagram_type_values(self):
        assert DiagramType.NONE.value == "none"
        assert DiagramType.LINE.value == "line"
        assert DiagramType.COORDINATE_PLANE.value == "coordinate_plane"

    def test_constraint_type_values(self):
        assert ConstraintType.RANGE.value == "range"
        assert ConstraintType.POSITIVITY.value == "positivity"
        assert ConstraintType.INTEGER.value == "integer"


# =========================================================================
# LearningOutcome Tests
# =========================================================================

class TestLearningOutcome:

    def test_create(self):
        lo = LearningOutcome("LO-01", "Solve equations")
        assert lo.code == "LO-01"
        assert lo.description == "Solve equations"

    def test_to_dict(self):
        lo = LearningOutcome("LO-01", "Solve equations")
        d = lo.to_dict()
        assert d["code"] == "LO-01"
        assert d["description"] == "Solve equations"


# =========================================================================
# SemanticMetadata Tests
# =========================================================================

class TestSemanticMetadata:

    def test_create_with_minimal_args(self):
        m = SemanticMetadata(template_id="LinearEquation")
        assert m.template_id == "LinearEquation"
        assert m.version == "1.0.0"
        assert m.status == TemplateStatus.DRAFT
        assert m.display_name == ""

    def test_create_with_all_args(self):
        m = SemanticMetadata(
            template_id="LinearEquation",
            display_name="Linear Equation",
            internal_name="linear_equation",
            version="2.0.0",
            status=TemplateStatus.APPROVED,
            confidence_score=0.95,
            plugin_source="custom",
            review_status="peer_reviewed",
        )
        assert m.display_name == "Linear Equation"
        assert m.internal_name == "linear_equation"
        assert m.version == "2.0.0"
        assert m.status == TemplateStatus.APPROVED
        assert m.confidence_score == 0.95
        assert m.plugin_source == "custom"

    def test_timestamps_are_iso(self):
        m = SemanticMetadata(template_id="T1")
        assert "T" in m.created_at
        assert m.created_at.endswith("+00:00") or "+00:00" in m.created_at or "Z" in m.created_at

    def test_to_dict(self):
        m = SemanticMetadata(
            template_id="T1",
            display_name="Test",
            internal_name="test",
            status=TemplateStatus.DRAFT,
        )
        d = m.to_dict()
        assert d["template_id"] == "T1"
        assert d["display_name"] == "Test"
        assert d["status"] == "draft"
        assert "created_at" in d
        assert "updated_at" in d


# =========================================================================
# SemanticTemplate Tests
# =========================================================================

class TestSemanticTemplate:

    def test_create_minimal(self):
        m = SemanticMetadata(template_id="ConstantExpression")
        t = SemanticTemplate(
            template_id="ConstantExpression",
            template_family=TemplateFamily.ARITHMETIC,
            metadata=m,
        )
        assert t.template_id == "ConstantExpression"
        assert t.template_family == TemplateFamily.ARITHMETIC
        assert t.subject == "Mathematics"
        assert t.difficulty == DifficultyLevel.MEDIUM
        assert t.template_version == "1.0.0"

    def test_create_with_all_fields(self):
        m = SemanticMetadata(
            template_id="LinearEquation",
            display_name="Linear Equation",
        )
        lo = LearningOutcome("LO-01", "Solve")
        t = SemanticTemplate(
            template_id="LinearEquation",
            template_family=TemplateFamily.ALGEBRA,
            subject="Mathematics",
            chapter="Linear Equations",
            topic="Solving",
            concept="Solve ax + b = c",
            difficulty=DifficultyLevel.HARD,
            variable_graph=VariableGraph(),
            expected_constraint_types=(ConstraintType.RANGE,),
            generator_type=GeneratorType.ALGEBRAIC,
            solver_type=SolverType.LINEAR,
            diagram_type=DiagramType.NONE,
            metadata=m,
            template_version="2.0.0",
            tags=("algebra", "linear"),
            learning_outcomes=(lo,),
        )
        assert t.chapter == "Linear Equations"
        assert t.difficulty == DifficultyLevel.HARD
        assert t.expected_constraint_types == (ConstraintType.RANGE,)
        assert t.template_version == "2.0.0"
        assert t.tags == ("algebra", "linear")

    def test_to_dict(self):
        m = SemanticMetadata(template_id="LinearEquation", display_name="Linear Equation")
        t = SemanticTemplate(
            template_id="LinearEquation",
            template_family=TemplateFamily.ALGEBRA,
            metadata=m,
            tags=("algebra",),
        )
        d = t.to_dict()
        assert d["template_id"] == "LinearEquation"
        assert d["template_family"] == "algebra"
        assert d["metadata"]["display_name"] == "Linear Equation"
        assert d["tags"] == ["algebra"]
        assert d["difficulty"] == "medium"

    def test_to_dict_no_metadata(self):
        """SemanticTemplate with metadata=None should still serialize."""
        t = SemanticTemplate(
            template_id="T1",
            template_family=TemplateFamily.ALGEBRA,
        )
        d = t.to_dict()
        assert d["metadata"] is None

    def test_variable_graph_attachment(self):
        g = VariableGraph()
        m = SemanticMetadata(template_id="T1")
        t = SemanticTemplate(
            template_id="T1",
            template_family=TemplateFamily.ALGEBRA,
            variable_graph=g,
            metadata=m,
        )
        assert t.variable_graph is g


# =========================================================================
# SemanticTemplateRegistry Tests
# =========================================================================

class TestSemanticTemplateRegistry:

    def make_template(self, tid: str, family: TemplateFamily = TemplateFamily.ALGEBRA,
                      concept: str = "", gen: GeneratorType = GeneratorType.ALGEBRAIC,
                      tags: tuple[str, ...] = (),
                      constraints: tuple[ConstraintType, ...] = ()) -> SemanticTemplate:
        m = SemanticMetadata(template_id=tid)
        return SemanticTemplate(
            template_id=tid,
            template_family=family,
            concept=concept,
            generator_type=gen,
            tags=tags,
            expected_constraint_types=constraints,
            metadata=m,
        )

    def test_register_new(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("LinearEquation")
        assert r.register(t) is True
        assert r.count() == 1

    def test_register_duplicate(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("LinearEquation")
        r.register(t)
        assert r.register(self.make_template("LinearEquation")) is False
        assert r.count() == 1

    def test_lookup_by_id(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("LinearEquation")
        r.register(t)
        assert r.lookup_by_id("LinearEquation") == t
        assert r.lookup_by_id("NonExistent") is None

    def test_lookup_by_family(self):
        r = SemanticTemplateRegistry()
        a = self.make_template("T1", family=TemplateFamily.ALGEBRA)
        b = self.make_template("T2", family=TemplateFamily.ALGEBRA)
        c = self.make_template("T3", family=TemplateFamily.ARITHMETIC)
        r.register(a)
        r.register(b)
        r.register(c)
        algebra = r.lookup_by_family(TemplateFamily.ALGEBRA)
        assert len(algebra) == 2
        arith = r.lookup_by_family(TemplateFamily.ARITHMETIC)
        assert len(arith) == 1
        assert r.lookup_by_family(TemplateFamily.GEOMETRY) == []

    def test_lookup_by_concept(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("LinearEquation", concept="Solve ax + b = c")
        r.register(t)
        found = r.lookup_by_concept("Solve ax + b = c")
        assert len(found) == 1
        assert found[0].template_id == "LinearEquation"
        assert r.lookup_by_concept("nonexistent") == []

    def test_lookup_by_generator(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("T1", gen=GeneratorType.NUMERIC)
        r.register(t)
        found = r.lookup_by_generator(GeneratorType.NUMERIC)
        assert len(found) == 1
        assert r.lookup_by_generator(GeneratorType.GEOMETRIC) == []

    def test_lookup_by_constraint(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("T1", constraints=(ConstraintType.RANGE, ConstraintType.INTEGER))
        r.register(t)
        found = r.lookup_by_constraint(ConstraintType.RANGE)
        assert len(found) == 1
        found2 = r.lookup_by_constraint(ConstraintType.INTEGER)
        assert len(found2) == 1
        assert r.lookup_by_constraint(ConstraintType.POSITIVITY) == []

    def test_lookup_by_tags_require_all(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("T1", tags=("algebra", "linear", "equation"))
        r.register(t)
        assert len(r.lookup_by_tags({"algebra", "linear"}, require_all=True)) == 1
        assert len(r.lookup_by_tags({"algebra", "nonexistent"}, require_all=True)) == 0

    def test_lookup_by_tags_require_any(self):
        r = SemanticTemplateRegistry()
        t1 = self.make_template("T1", tags=("algebra", "linear"))
        t2 = self.make_template("T2", tags=("geometry", "circle"))
        r.register(t1)
        r.register(t2)
        any_match = r.lookup_by_tags({"algebra", "geometry"}, require_all=False)
        assert len(any_match) == 2
        assert r.lookup_by_tags({"algebra"}, require_all=False) == [t1]

    def test_version_management(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("LinearEquation")
        r.register(t)
        versions = r.get_versions("LinearEquation")
        assert versions == ["1.0.0"]
        assert r.get_versions("NonExistent") == []
        assert r.get_latest_version("LinearEquation") == t
        assert r.get_latest_version("NonExistent") is None

    def test_has_id(self):
        r = SemanticTemplateRegistry()
        t = self.make_template("T1")
        r.register(t)
        assert r.has_id("T1") is True
        assert r.has_id("T2") is False

    def test_get_all(self):
        r = SemanticTemplateRegistry()
        t1 = self.make_template("T1")
        t2 = self.make_template("T2")
        r.register(t1)
        r.register(t2)
        all_t = r.get_all()
        assert len(all_t) == 2
        assert t1 in all_t
        assert t2 in all_t

    def test_get_all_ids(self):
        r = SemanticTemplateRegistry()
        r.register(self.make_template("T1"))
        r.register(self.make_template("T2"))
        assert set(r.get_all_ids()) == {"T1", "T2"}

    def test_get_all_families(self):
        r = SemanticTemplateRegistry()
        r.register(self.make_template("T1", family=TemplateFamily.ALGEBRA))
        r.register(self.make_template("T2", family=TemplateFamily.ARITHMETIC))
        assert r.get_all_families() == {TemplateFamily.ALGEBRA, TemplateFamily.ARITHMETIC}

    def test_clear(self):
        r = SemanticTemplateRegistry()
        r.register(self.make_template("T1"))
        r.clear()
        assert r.count() == 0
        assert r.get_all() == []


# =========================================================================
# SemanticTemplateBuilder Tests
# =========================================================================

class TestSemanticTemplateBuilder:

    def test_build_linear_equation(self):
        sig = build_signature("7x + 3 = 38")
        assert sig.template_id == "LinearEquation"
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "LinearEquation"
        assert t.template_family == TemplateFamily.ALGEBRA
        assert t.chapter == "Linear Equations"
        assert t.topic == "Solving Linear Equations"
        assert t.concept == "Solve ax + b = c in one variable"
        assert t.difficulty == DifficultyLevel.MEDIUM
        assert t.solver_type == SolverType.LINEAR
        assert t.diagram_type == DiagramType.NONE
        assert len(t.expected_constraint_types) == 3
        assert len(t.tags) == 4
        assert len(t.learning_outcomes) == 2

    def test_build_simple_linear_equation(self):
        sig = build_signature("x + 5 = 12")
        assert sig.template_id == "SimpleLinearEquation"
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "SimpleLinearEquation"
        assert t.template_family == TemplateFamily.ALGEBRA
        assert t.chapter == "Linear Equations"
        assert t.topic == "Basic Equations"
        assert t.concept == "Solve x + a = b"

    def test_build_distributive_multiplication(self):
        sig = build_signature("2(x+3)")
        assert sig.template_id == "DistributiveMultiplication"
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "DistributiveMultiplication"
        assert t.topic == "Distributive Property"
        assert t.solver_type == SolverType.TRANSFORMATION

    def test_build_scalar_multiplication(self):
        sig = build_signature("5x")
        assert sig.template_id == "ScalarMultiplication"
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "ScalarMultiplication"
        assert t.template_family == TemplateFamily.ALGEBRA

    def test_build_linear_expression(self):
        sig = build_signature("x + 5")
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "LinearExpression"
        assert t.solver_type == SolverType.EVALUATION

    def test_build_constant_expression(self):
        sig = build_signature("42")
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "ConstantExpression"
        assert t.template_family == TemplateFamily.ARITHMETIC
        assert t.generator_type == GeneratorType.ARITHMETIC

    def test_build_variable_expression(self):
        sig = build_signature("x")
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.template_id == "VariableExpression"
        assert t.solver_type == SolverType.NONE

    def test_build_with_overrides(self):
        sig = build_signature("7x + 3 = 38")
        builder = SemanticTemplateBuilder(overrides={
            "chapter": "Custom Chapter",
            "difficulty": "hard",
            "subject": "Advanced Mathematics",
            "display_name": "My Equation",
        })
        t = builder.build(sig)
        assert t.chapter == "Custom Chapter"
        assert t.difficulty == DifficultyLevel.HARD
        assert t.subject == "Advanced Mathematics"
        assert t.metadata.display_name == "My Equation"

    def test_build_with_variable_graph(self):
        sig = build_signature("7x + 3 = 38")
        result = discover_variables("7x + 3 = 38")
        builder = SemanticTemplateBuilder()
        t = builder.build(sig, variable_graph=result.graph)
        assert t.variable_graph is result.graph
        assert t.variable_graph.node_count() > 0

    def test_build_with_status_override(self):
        sig = build_signature("x + 5 = 12")
        builder = SemanticTemplateBuilder(overrides={"status": "approved"})
        t = builder.build(sig)
        assert t.metadata.status == TemplateStatus.APPROVED

    def test_build_deterministic(self):
        sig1 = build_signature("7x + 3 = 38")
        sig2 = build_signature("5y + 2 = 17")
        builder = SemanticTemplateBuilder()
        t1 = builder.build(sig1)
        t2 = builder.build(sig2)
        assert t1.template_id == t2.template_id
        assert t1.chapter == t2.chapter
        assert t1.concept == t2.concept
        assert t1.tags == t2.tags

    def test_build_unknown_template(self):
        sig = build_signature("x / 2 = 5")
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        # Unknown templates fall back to default family
        assert t.template_family == TemplateFamily.ALGEBRA
        assert t.generator_type == GeneratorType.ALGEBRAIC


# =========================================================================
# End-to-End Pipeline Tests
# =========================================================================

class TestEndToEndPipeline:

    def test_full_pipeline_linear_equation(self):
        """Parse → canonicalize → signature → variables → semantic template."""
        expr = "7x + 3 = 38"
        ast = canonical_ast(expr)

        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_id == "LinearEquation"

        result = VariableDiscoveryVisitor(expression=expr).discover(ast)
        assert result.registry.count() > 1
        assert result.graph.node_count() > 0

        builder = SemanticTemplateBuilder()
        t = builder.build(sig, variable_graph=result.graph)

        assert t.template_id == "LinearEquation"
        assert t.template_family == TemplateFamily.ALGEBRA
        assert t.chapter == "Linear Equations"
        assert t.variable_graph is result.graph
        assert len(t.expected_constraint_types) == 3
        assert t.metadata.status == TemplateStatus.DRAFT
        assert t.metadata.template_id == "LinearEquation"

    def test_full_pipeline_constant(self):
        expr = "42"
        ast = canonical_ast(expr)
        sig = TemplateSignatureBuilder().build(ast)
        result = VariableDiscoveryVisitor(expression=expr).discover(ast)
        t = SemanticTemplateBuilder().build(sig, variable_graph=result.graph)
        assert t.template_id == "ConstantExpression"
        assert t.template_family == TemplateFamily.ARITHMETIC

    def test_full_pipeline_distributive(self):
        expr = "2(x+3)"
        ast = canonical_ast(expr)
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_id == "DistributiveMultiplication"
        result = VariableDiscoveryVisitor(expression=expr).discover(ast)
        t = SemanticTemplateBuilder().build(sig, variable_graph=result.graph)
        assert t.template_family == TemplateFamily.ALGEBRA
        assert t.topic == "Distributive Property"
        assert t.variable_graph.node_count() > 0

    def test_full_pipeline_serialization(self):
        expr = "7x + 3 = 38"
        ast = canonical_ast(expr)
        sig = TemplateSignatureBuilder().build(ast)
        result = VariableDiscoveryVisitor(expression=expr).discover(ast)
        t = SemanticTemplateBuilder().build(sig, variable_graph=result.graph)
        d = t.to_dict()
        assert d["template_id"] == "LinearEquation"
        assert d["chapter"] == "Linear Equations"
        assert "metadata" in d
        assert "template_version" in d


# =========================================================================
# Edge Cases
# =========================================================================

class TestEdgeCases:

    def test_empty_tags(self):
        m = SemanticMetadata(template_id="T1")
        t = SemanticTemplate(
            template_id="T1",
            template_family=TemplateFamily.ALGEBRA,
            tags=(),
            metadata=m,
        )
        assert t.tags == ()

    def test_empty_constraint_types(self):
        m = SemanticMetadata(template_id="T1")
        t = SemanticTemplate(
            template_id="T1",
            template_family=TemplateFamily.ALGEBRA,
            expected_constraint_types=(),
            metadata=m,
        )
        assert t.expected_constraint_types == ()

    def test_deprecated_status(self):
        m = SemanticMetadata(template_id="OldTemplate", status=TemplateStatus.DEPRECATED)
        t = SemanticTemplate(
            template_id="OldTemplate",
            template_family=TemplateFamily.ALGEBRA,
            metadata=m,
        )
        assert t.metadata.status == TemplateStatus.DEPRECATED

    def test_easy_difficulty(self):
        m = SemanticMetadata(template_id="EasyTemplate")
        t = SemanticTemplate(
            template_id="EasyTemplate",
            template_family=TemplateFamily.ARITHMETIC,
            difficulty=DifficultyLevel.EASY,
            metadata=m,
        )
        assert t.difficulty == DifficultyLevel.EASY

    def test_registry_multiple_families(self):
        r = SemanticTemplateRegistry()
        for i, fam in enumerate([TemplateFamily.ALGEBRA, TemplateFamily.GEOMETRY,
                                TemplateFamily.STATISTICS, TemplateFamily.CALCULUS]):
            m = SemanticMetadata(template_id=f"T{i}")
            r.register(SemanticTemplate(
                template_id=f"T{i}", template_family=fam, metadata=m,
            ))
        assert r.count() == 4
        assert len(r.lookup_by_family(TemplateFamily.ALGEBRA)) == 1
        assert len(r.lookup_by_family(TemplateFamily.CALCULUS)) == 1

    def test_registry_lookup_by_tags_empty(self):
        r = SemanticTemplateRegistry()
        t = SemanticTemplate(
            template_id="NoTags",
            template_family=TemplateFamily.ALGEBRA,
            tags=(),
            metadata=SemanticMetadata(template_id="NoTags"),
        )
        r.register(t)
        assert r.lookup_by_tags({"algebra"}, require_all=False) == []
        assert r.lookup_by_tags(set()) == []

    def test_builder_override_status_enum(self):
        sig = build_signature("x")
        builder = SemanticTemplateBuilder(overrides={
            "status": TemplateStatus.APPROVED,
        })
        t = builder.build(sig)
        assert t.metadata.status == TemplateStatus.APPROVED

    def test_builder_override_difficulty_enum(self):
        sig = build_signature("x")
        builder = SemanticTemplateBuilder(overrides={
            "difficulty": DifficultyLevel.EASY,
        })
        t = builder.build(sig)
        assert t.difficulty == DifficultyLevel.EASY

    def test_builder_unknown_template_tags_and_outcomes(self):
        sig = build_signature("5/2 = x")
        builder = SemanticTemplateBuilder()
        t = builder.build(sig)
        assert t.tags == ()
        assert t.learning_outcomes == ()

    def test_builder_overrides_tags_and_outcomes(self):
        sig = build_signature("x")
        custom_tags = ("custom", "test")
        custom_lo = (LearningOutcome("LO-CUSTOM", "Custom"),)
        builder = SemanticTemplateBuilder(overrides={
            "tags": custom_tags,
            "learning_outcomes": custom_lo,
        })
        t = builder.build(sig)
        assert t.tags == custom_tags
        assert t.learning_outcomes == custom_lo

    def test_semantic_template_with_diagram_type(self):
        m = SemanticMetadata(template_id="GeoTemplate")
        t = SemanticTemplate(
            template_id="GeoTemplate",
            template_family=TemplateFamily.GEOMETRY,
            diagram_type=DiagramType.TRIANGLE,
            metadata=m,
        )
        assert t.diagram_type == DiagramType.TRIANGLE

    def test_semantic_template_with_non_default_generator(self):
        m = SemanticMetadata(template_id="StatTemplate")
        t = SemanticTemplate(
            template_id="StatTemplate",
            template_family=TemplateFamily.STATISTICS,
            generator_type=GeneratorType.STATISTICAL,
            metadata=m,
        )
        assert t.generator_type == GeneratorType.STATISTICAL

    def test_registry_lookup_by_multiple_constraints(self):
        r = SemanticTemplateRegistry()
        t = SemanticTemplate(
            template_id="MultiConstraint",
            template_family=TemplateFamily.ALGEBRA,
            expected_constraint_types=(
                ConstraintType.RANGE,
                ConstraintType.POSITIVITY,
                ConstraintType.INTEGER,
                ConstraintType.PARITY,
            ),
            metadata=SemanticMetadata(template_id="MultiConstraint"),
        )
        r.register(t)
        assert len(r.lookup_by_constraint(ConstraintType.PARITY)) == 1
        assert len(r.lookup_by_constraint(ConstraintType.RANGE)) == 1
        assert len(r.lookup_by_constraint(ConstraintType.COPRIME)) == 0
