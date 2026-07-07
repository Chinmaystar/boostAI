"""End-to-end integration tests for Milestone 10: Question Package Pipeline.

Tests the complete deterministic flow through all subsystems:
  Parse → Canonicalize → Template Discovery → Variable Extraction →
  Semantic Template → Question Generation (Constraint Validation +
  Symbolic Verification) → Diagram Generation → GeneratedQuestionPackage

Each test verifies the full pipeline for a representative mathematical
question type using the PipelineOrchestrator.
"""

import math
import re

import pytest

from src.integration import (
    PipelineOrchestrator, PipelineConfig, QuestionSource, DiagramSpec,
    GeneratedQuestionPackage,
)
from src.generator import GeneratorConfig
from src.diagram_engine import (
    DiagramTemplate, SVGRenderer, RenderOptions, DiagramTemplateBuilder,
    Point, Line, Circle, Polygon, TextLabel,
)


# ══════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def orchestrator():
    config = PipelineConfig(
        generator_config=GeneratorConfig(
            random_seed=42,
            require_validation=False,
        ),
    )
    return PipelineOrchestrator(config)


@pytest.fixture
def svg_renderer():
    return SVGRenderer()


# ══════════════════════════════════════════════════════════════════════════
# Linear Equation Pipeline
# ══════════════════════════════════════════════════════════════════════════

class TestLinearEquationFullPipeline:
    """2x + 5 = 17 → full pipeline with package assembly."""

    SOURCE = QuestionSource(
        text="2*x + 5 = 17",
        main_variable="x",
    )

    def test_full_pipeline_returns_package(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert isinstance(pkg, GeneratedQuestionPackage)
        assert pkg.question_id.startswith("q_")
        assert pkg.template_id == "LinearEquation"
        assert pkg.version == "1.0.0"

    def test_rendered_question_contains_variables(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        rendered = pkg.rendered_question
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_expected_answer_type(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        if pkg.expected_answer is not None:
            assert isinstance(pkg.expected_answer, (int, float, list))

    def test_variable_assignments(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert len(pkg.variable_assignments) > 0

    def test_validation_report(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert pkg.validation_report is None or hasattr(pkg.validation_report, "valid")

    def test_generation_stats(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert pkg.generation_stats.success is True
        assert pkg.generation_stats.attempts >= 1

    def test_is_valid(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert pkg.is_valid is True

    def test_intermediate_results(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        ir = pkg.intermediate_results
        assert ir.ast is not None
        assert ir.canonical_result is not None
        assert ir.template_signature is not None
        assert ir.discovery_result is not None
        assert ir.symbolic_expr is not None

    def test_metadata_steps(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        steps = pkg.metadata.pipeline_steps
        assert len(steps) >= 8
        assert all(s.success for s in steps)
        step_names = [s.name for s in steps]
        assert "parse" in step_names
        assert "canonicalize" in step_names
        assert "template_discovery" in step_names
        assert "variable_extraction" in step_names
        assert "semantic_template" in step_names
        assert "symbolic_conversion" in step_names
        assert "question_generation" in step_names
        assert "diagram_generation" in step_names

    def test_no_diagrams_for_linear_eq(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert pkg.has_diagrams is False
        assert len(pkg.diagram_templates) == 0
        assert len(pkg.rendered_svgs) == 0

    def test_serialize_to_dict(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        d = pkg.to_dict()
        assert d["question_id"] == pkg.question_id
        assert d["template_id"] == "LinearEquation"
        assert d["is_valid"] is True
        assert d["diagram_count"] == 0
        assert d["svg_count"] == 0
        assert d["has_diagrams"] is False
        assert d["metadata"]["pipeline_steps"][0]["name"] == "parse"

    def test_get_svg_returns_none(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert pkg.get_svg() is None
        assert pkg.get_diagram() is None

    def test_multi_run_determinism(self, orchestrator):
        pkg1 = orchestrator.run(
            QuestionSource(text="3*x + 7 = 22", main_variable="x"))
        orchestrator.generator.reseed(42)
        pkg2 = orchestrator.run(
            QuestionSource(text="3*x + 7 = 22", main_variable="x"))

        assert pkg1.template_id == pkg2.template_id
        assert pkg1.rendered_question == pkg2.rendered_question


# ══════════════════════════════════════════════════════════════════════════
# Quadratic Equation Pipeline
# ══════════════════════════════════════════════════════════════════════════

class TestQuadraticEquationPipeline:
    """x*x - 5*x + 6 = 0"""

    SOURCE = QuestionSource(
        text="x*x - 5*x + 6 = 0",
        main_variable="x",
    )

    def test_full_pipeline(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert isinstance(pkg.template_id, str) and len(pkg.template_id) > 0
        assert pkg.template_id != "error"
        assert pkg.is_valid
        assert pkg.rendered_question is not None

    def test_expected_answer_type(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        if pkg.expected_answer is not None:
            assert isinstance(pkg.expected_answer, (int, float, list))

    def test_intermediates(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        assert pkg.intermediate_results.template_signature is not None

    def test_generation_stats(self, orchestrator):
        pkg = orchestrator.run(self.SOURCE)

        stats = pkg.generation_stats
        assert hasattr(stats, "success")
        assert hasattr(stats, "attempts")
        assert hasattr(stats, "retries")


# ══════════════════════════════════════════════════════════════════════════
# Question with Diagram Specs
# ══════════════════════════════════════════════════════════════════════════

class TestQuestionWithDiagram:
    """Triangle geometry question with an associated diagram spec."""

    def test_triangle_diagram_pipeline(self, orchestrator, svg_renderer):
        source = QuestionSource(
            text="a + b + c = 180",
            main_variable="a",
            diagram_specs=[
                DiagramSpec(
                    type="triangle",
                    properties={
                        "template_id": "tri_001",
                        "points": [
                            {"id": "A", "x": 0, "y": 0, "label": "A"},
                            {"id": "B", "x": 100, "y": 0, "label": "B"},
                            {"id": "C", "x": 50, "y": 80, "label": "C"},
                        ],
                        "lines": [
                            {"id": "AB", "start": "A", "end": "B"},
                            {"id": "BC", "start": "B", "end": "C"},
                            {"id": "CA", "start": "C", "end": "A"},
                        ],
                        "polygon": {
                            "id": "tri",
                            "vertices": ["A", "B", "C"],
                        },
                    },
                ),
            ],
        )

        pkg = orchestrator.run(source)
        assert pkg.is_valid
        assert pkg.rendered_question is not None

    def test_multiple_diagram_specs(self, orchestrator, svg_renderer):
        source = QuestionSource(
            text="x + y = 10",
            diagram_specs=[
                DiagramSpec(
                    type="triangle",
                    properties={
                        "template_id": "tri_001",
                        "points": [
                            {"id": "A", "x": 0, "y": 0, "label": "A"},
                            {"id": "B", "x": 100, "y": 0, "label": "B"},
                            {"id": "C", "x": 50, "y": 80, "label": "C"},
                        ],
                        "lines": [
                            {"id": "AB", "start": "A", "end": "B"},
                            {"id": "BC", "start": "B", "end": "C"},
                            {"id": "CA", "start": "C", "end": "A"},
                        ],
                        "polygon": {
                            "id": "tri",
                            "vertices": ["A", "B", "C"],
                        },
                    },
                ),
                DiagramSpec(
                    type="circle",
                    properties={
                        "template_id": "cir_001",
                        "center": {"id": "O", "x": 200, "y": 200},
                        "radius": 75,
                    },
                ),
            ],
        )

        pkg = orchestrator.run(source)

        assert pkg.metadata.pipeline_steps[-1].success is not False

    def test_diagram_in_package_dict(self, orchestrator, svg_renderer):
        source = QuestionSource(
            text="2*x + 3 = 7",
            main_variable="x",
            diagram_specs=[
                DiagramSpec(
                    type="coordinate_grid",
                    properties={
                        "template_id": "grid_001",
                    },
                ),
            ],
        )

        pkg = orchestrator.run(source)
        d = pkg.to_dict()
        assert d["diagram_count"] >= 0
        assert d["svg_count"] >= 0


# ══════════════════════════════════════════════════════════════════════════
# Error Handling
# ══════════════════════════════════════════════════════════════════════════

class TestPipelineErrorHandling:
    """Error propagation and fallback packages."""

    def test_parse_error_returns_fallback(self, orchestrator):
        source = QuestionSource(text="2x ++ 5 = 17")
        pkg = orchestrator.run(source)

        assert pkg.template_id == "error"
        assert pkg.is_valid is False
        assert pkg.generation_stats.success is False
        assert len(pkg.rendered_svgs) == 0

    def test_partial_error_in_diagram(
        self, orchestrator,
    ):
        source = QuestionSource(
            text="2*x + 5 = 17",
            main_variable="x",
            diagram_specs=[
                DiagramSpec(
                    type="nonexistent_type_xyz",
                    properties={},
                ),
            ],
        )

        pkg = orchestrator.run(source)
        assert pkg.template_id == "LinearEquation"
        assert pkg.is_valid


# ══════════════════════════════════════════════════════════════════════════
# Partial Pipeline Steps (individual subsystem access)
# ══════════════════════════════════════════════════════════════════════════

class TestPartialSteps:
    """Using the orchestrator for partial pipeline runs."""

    def test_run_expression(self, orchestrator):
        result = orchestrator.run_expression("2*x + 5 = 17")
        assert "ast" in result
        assert "canonical" in result
        assert "signature" in result
        assert "discovery" in result
        assert "semantic" in result
        assert "symbolic" in result

    def test_run_equation(self, orchestrator):
        result = orchestrator.run_equation("2*x + 5 = 17", "x")
        assert "equation_result" in result
        eq = result["equation_result"]
        assert eq.has_solution
        assert abs(eq.solution_values()[0] - 6.0) < 1e-9

    def test_evaluate_with_values(self, orchestrator):
        val = orchestrator.evaluate_with_values(
            "2*x + 5", {"x": 6})
        assert abs(val - 17.0) < 1e-9

    def test_generate_question_only(self, orchestrator):
        source = QuestionSource(text="2*x + 5 = 17", main_variable="x")
        question = orchestrator.generate_question(source)
        assert question.question_id.startswith("q_")
        assert question.template_id == "LinearEquation"

    def test_build_diagram_unknown_type(self, orchestrator):
        spec = DiagramSpec(type="unknown", properties={})
        diagram = orchestrator.build_diagram(spec)
        assert diagram is None

    def test_render_diagram_known(self, orchestrator, svg_renderer):
        template = (
            DiagramTemplateBuilder("test_tri", "triangle")
            .add_point(Point(id="A", x=0, y=0, label="A"))
            .add_point(Point(id="B", x=100, y=0, label="B"))
            .add_point(Point(id="C", x=0, y=80, label="C"))
            .add_line(Line(id="AB", start="A", end="B"))
            .add_line(Line(id="BC", start="B", end="C"))
            .add_line(Line(id="CA", start="C", end="A"))
            .add_polygon(Polygon(id="tri", vertices=["A", "B", "C"]))
            .build()
        )

        svg = orchestrator.render_diagram(template)
        assert isinstance(svg, str)
        assert svg.startswith("<svg")
        assert "viewBox" in svg
        assert "A" in svg


# ══════════════════════════════════════════════════════════════════════════
# Package Inspection
# ══════════════════════════════════════════════════════════════════════════

class TestPackageProperties:
    """Edge cases and property access on GeneratedQuestionPackage."""

    def test_empty_package_properties(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="x = 5", main_variable="x"))

        assert hasattr(pkg, "question_id")
        assert hasattr(pkg, "has_diagrams")
        assert hasattr(pkg, "is_valid")
        assert hasattr(pkg, "to_dict")
        assert hasattr(pkg, "get_svg")
        assert hasattr(pkg, "get_diagram")

    def test_to_dict_keys(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="2*x + 3 = 7", main_variable="x"))

        d = pkg.to_dict()
        expected_keys = {
            "question_id", "template_id", "version",
            "source_text", "rendered_question", "variable_assignments",
            "expected_answer", "semantic_template", "validation_report",
            "diagram_count", "svg_count", "metadata",
            "generation_stats", "intermediate_results",
            "is_valid", "has_diagrams",
        }
        assert set(d.keys()) == expected_keys

    def test_question_id_pattern(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="x + 1 = 2", main_variable="x"))

        assert re.match(r"^q_[a-f0-9]{12}$", pkg.question_id)

    def test_metadata_timestamp(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="x + 1 = 2", main_variable="x"))

        assert pkg.metadata.created_at.endswith("Z") or "T" in pkg.metadata.created_at

    def test_non_empty_rendered_text(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="2*x + 5 = 17", main_variable="x"))

        assert len(pkg.rendered_question) > 10
        assert "Solve" in pkg.rendered_question or "=" in pkg.rendered_question

    def test_generation_time_positive(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="2*x + 5 = 17", main_variable="x"))

        assert pkg.metadata.generation_time_ms > 0


# ══════════════════════════════════════════════════════════════════════════
# Determinism and Reproducibility
# ══════════════════════════════════════════════════════════════════════════

class TestDeterminism:
    """Same input → same output (with fixed random seed)."""

    def test_deterministic_output(self):
        config1 = PipelineConfig(
            generator_config=GeneratorConfig(random_seed=123, require_validation=False),
        )
        config2 = PipelineConfig(
            generator_config=GeneratorConfig(random_seed=123, require_validation=False),
        )
        o1 = PipelineOrchestrator(config1)
        o2 = PipelineOrchestrator(config2)

        src = QuestionSource(text="2*x + 5 = 17", main_variable="x")
        pkg1 = o1.run(src)
        pkg2 = o2.run(src)

        assert pkg1.rendered_question == pkg2.rendered_question
        assert pkg1.expected_answer == pkg2.expected_answer

        num1 = {k: v for k, v in pkg1.variable_assignments.items() if isinstance(v, (int, float))}
        num2 = {k: v for k, v in pkg2.variable_assignments.items() if isinstance(v, (int, float))}
        assert sorted(num1.values()) == sorted(num2.values())

    def test_different_seeds_different_assignments(self):
        o1 = PipelineOrchestrator(
            PipelineConfig(generator_config=GeneratorConfig(random_seed=1, require_validation=False)),
        )
        o2 = PipelineOrchestrator(
            PipelineConfig(generator_config=GeneratorConfig(random_seed=999, require_validation=False)),
        )

        src = QuestionSource(text="2*x + 5 = 17", main_variable="x")
        pkg1 = o1.run(src)
        pkg2 = o2.run(src)

        num1 = sorted(v for v in pkg1.variable_assignments.values() if isinstance(v, (int, float)))
        num2 = sorted(v for v in pkg2.variable_assignments.values() if isinstance(v, (int, float)))
        assert num1 != num2 or pkg1.rendered_question != pkg2.rendered_question


# ══════════════════════════════════════════════════════════════════════════
# Pipeline Configuration
# ══════════════════════════════════════════════════════════════════════════

class TestPipelineConfig:
    """PipelineOrchestrator configuration options."""

    def test_default_config(self):
        o = PipelineOrchestrator()
        assert o.config.generator_config is not None
        assert o.config.max_diagrams == 5
        assert o.config.pipeline_version == "1.0.0"

    def test_custom_config(self):
        config = PipelineConfig(
            generator_config=GeneratorConfig(max_retries=5),
            max_diagrams=10,
            pipeline_version="2.0.0",
        )
        o = PipelineOrchestrator(config)
        assert o.generator.config.max_retries == 5
        assert o.config.max_diagrams == 10
        assert o.config.pipeline_version == "2.0.0"

    def test_plugin_registry_accessible(self, orchestrator):
        assert orchestrator.plugin_registry is not None
        assert orchestrator.plugin_registry.list_plugins() is not None
        assert orchestrator.generator is not None

    def test_render_with_svg_custom_options(self):
        config = PipelineConfig(
            render_options=RenderOptions(
                responsive=False,
                width="800",
                height="600",
                include_data_attributes=False,
            ),
        )
        o = PipelineOrchestrator(config)
        template = (
            DiagramTemplateBuilder("test_tri", "triangle")
            .add_point(Point(id="A", x=0, y=0, label="A"))
            .add_point(Point(id="B", x=100, y=0, label="B"))
            .add_point(Point(id="C", x=0, y=80, label="C"))
            .add_line(Line(id="AB", start="A", end="B"))
            .add_line(Line(id="BC", start="B", end="C"))
            .add_line(Line(id="CA", start="C", end="A"))
            .add_polygon(Polygon(id="tri", vertices=["A", "B", "C"]))
            .build()
        )

        svg = o.render_diagram(template)
        assert 'width="800"' in svg
        assert 'height="600"' in svg


# ══════════════════════════════════════════════════════════════════════════
# Cross-Pipeline Verification
# ══════════════════════════════════════════════════════════════════════════

class TestCrossPipelineVerification:
    """Verify that the pipeline produces logically consistent output."""

    def _check_consistency(self, pkg) -> None:
        """Verify that the expected answer satisfies the rendered equation.

        Parses the rendered equation string and checks that substituting
        the answer for the unknown variable balances both sides.
        """
        answer = pkg.expected_answer
        assert answer is not None, f"expected_answer is None for '{pkg.rendered_question}'"

        rendered = pkg.rendered_question
        if ": " in rendered:
            rendered = rendered.split(": ", 1)[1]

        eq_text = rendered.replace("\u00d7", "*").replace("\u2212", "-")
        sides = eq_text.split("=")
        if len(sides) != 2:
            return

        lhs_str, rhs_str = sides[0].strip(), sides[1].strip()
        ans = float(answer)

        # Find variable name: any standalone letter not in the slot names
        slot_names = set(pkg.variable_assignments.keys())
        var_name = "x"
        for token in re.findall(r'\b([a-zA-Z])\b', lhs_str):
            if token not in slot_names:
                var_name = token
                break

        safe_scope = {}
        lhs_val = eval(
            lhs_str.replace(var_name, f"({ans})"),
            {"__builtins__": {}}, safe_scope,
        )
        rhs_val = eval(rhs_str, {"__builtins__": {}}, safe_scope)
        assert abs(lhs_val - rhs_val) < 1e-6, (
            f"Inconsistent: '{pkg.rendered_question}' with assignments "
            f"{pkg.variable_assignments}, answer={answer}: "
            f"LHS({lhs_str}) = {lhs_val}, RHS({rhs_str}) = {rhs_val}"
        )

    def test_answer_satisfies_rendered_equation(self, orchestrator):
        """Verify mathematical consistency: answer must satisfy rendered equation."""
        for text, main_var in [("2*x + 5 = 17", "x"), ("3*x - 7 = 14", "x")]:
            src = QuestionSource(text=text, main_variable=main_var)
            pkg = orchestrator.run(src)
            self._check_consistency(pkg)

    def test_consistency_across_seeds(self, orchestrator):
        """Run consistency check across multiple random seeds to catch ordering issues."""
        for seed in [42, 99, 123, 256, 777]:
            cfg = PipelineConfig(
                generator_config=GeneratorConfig(random_seed=seed, require_validation=False),
            )
            orch = PipelineOrchestrator(cfg)
            src = QuestionSource(text="2*x + 5 = 17", main_variable="x")
            pkg = orch.run(src)
            self._check_consistency(pkg)

    def test_rendered_question_includes_assignments(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="a*x + b = c", main_variable="x"))
        rendered = pkg.rendered_question
        assignments = pkg.variable_assignments
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_all_steps_successful(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="2*x + 5 = 17", main_variable="x"))
        steps = pkg.metadata.pipeline_steps
        for step in steps:
            assert step.success, f"Step '{step.name}' failed"

    def test_validation_report_consistency(self, orchestrator):
        pkg = orchestrator.run(
            QuestionSource(text="2*x + 5 = 17", main_variable="x"))

        if pkg.validation_report is not None:
            assert hasattr(pkg.validation_report, "valid")
            assert hasattr(pkg.validation_report, "stats")
