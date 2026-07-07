from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from src.tokenizer import Tokenizer
from src.lexer import Lexer
from src.parser import Parser
from src.canonicalizer import Canonicalizer, CanonicalResult
from src.template_engine import (
    TemplateSignature, TemplateSignatureBuilder,
)
from src.variable_engine import (
    VariableDiscoveryVisitor, DiscoveryResult, VariableGraph, VariableType,
)
from src.semantic_engine import (
    SemanticTemplate, SemanticTemplateBuilder,
    ConstraintType,
)
from src.constraint_engine import (
    ConstraintValidationResult,
)
from src.generator import (
    Generator, GeneratorConfig, GeneratedQuestion, GenerationStats,
)
from src.diagram_engine import (
    DiagramTemplate, DiagramTemplateBuilder, SVGRenderer,
    RenderOptions, SVGTheme, DiagramPlugin,
    Point, Line, Circle, Arc, Polygon, TextLabel,
    BoundingBox, PrimitiveType,
)
from src.diagram_engine.plugin_base import DiagramPluginRegistry
from src.symbolic import (
    SymbolicExpr, ASTExprAdapter, EquationEngine, BuiltinBackend,
)

from .models import (
    GeneratedQuestionPackage, QuestionSource, DiagramSpec,
    PipelineMetadata, PipelineStep, IntermediateResults,
)


@dataclass
class PipelineConfig:
    generator_config: GeneratorConfig | None = None
    render_options: RenderOptions | None = None
    max_diagrams: int = 5
    pipeline_version: str = "1.0.0"
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if self.generator_config is None:
            self.generator_config = GeneratorConfig(
                random_seed=self.random_seed,
                require_validation=self.random_seed is not None,
            )


class PipelineOrchestrator:
    """Orchestrates the full deterministic BoostAI pipeline end-to-end.

    Chains together:
      Parse → Canonicalize → Template Discovery → Variable Extraction →
      Semantic Template → Question Generation (Constraint Validation +
      Symbolic Verification) → Diagram Generation → Package Assembly

    Each subsystem keeps its existing responsibility.  The orchestrator
    only coordinates, never duplicates logic.
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self._config = config or PipelineConfig()

        gc = self._config.generator_config or GeneratorConfig(
            random_seed=self._config.random_seed,
        )

        self._tokenizer_cls = Tokenizer
        self._lexer = Lexer()
        self._canonicalizer = Canonicalizer()
        self._sig_builder = TemplateSignatureBuilder()
        self._var_discovery = VariableDiscoveryVisitor()
        self._semantic_builder = SemanticTemplateBuilder()
        self._ast_adapter = ASTExprAdapter()
        self._generator = Generator(gc)
        self._svgr = SVGRenderer(self._config.render_options)
        self._plugin_registry = DiagramPluginRegistry()

        self._symbolic_backend = BuiltinBackend()
        self._eq_engine = EquationEngine(self._symbolic_backend)

    @property
    def config(self) -> PipelineConfig:
        return self._config

    @property
    def generator(self) -> Generator:
        return self._generator

    @property
    def plugin_registry(self) -> DiagramPluginRegistry:
        return self._plugin_registry

    def register_diagram_plugin(self, plugin: DiagramPlugin) -> None:
        self._plugin_registry.register(plugin)

    # ──────────────────────────────────────────────────────────────────
    # Public pipeline entry point
    # ──────────────────────────────────────────────────────────────────

    def run(
        self,
        source: QuestionSource,
    ) -> GeneratedQuestionPackage:
        steps: list[PipelineStep] = []
        start = time.time()

        question_id = f"q_{uuid.uuid4().hex[:12]}"

        # 1. Parse
        t0 = time.time()
        try:
            ast = self._parse(source.text)
            steps.append(self._step("parse", t0, True))
        except Exception as exc:
            steps.append(self._step("parse", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 2. Canonicalize
        t0 = time.time()
        try:
            canonical = self._canonicalizer.canonicalize(ast)
            steps.append(self._step("canonicalize", t0, True))
        except Exception as exc:
            steps.append(self._step("canonicalize", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 3. Template Signature
        t0 = time.time()
        try:
            sig = self._sig_builder.build(canonical.tree)
            steps.append(self._step("template_discovery", t0, True))
        except Exception as exc:
            steps.append(self._step("template_discovery", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 4. Variable Discovery
        t0 = time.time()
        try:
            discovery = self._var_discovery.discover(canonical.tree)
            steps.append(self._step("variable_extraction", t0, True))
        except Exception as exc:
            steps.append(self._step("variable_extraction", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 5. Semantic Template
        t0 = time.time()
        try:
            semantic = self._semantic_builder.build(
                sig, discovery.graph,
            )
            steps.append(self._step("semantic_template", t0, True))
        except Exception as exc:
            steps.append(self._step("semantic_template", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 6. Convert AST → SymbolicExpr
        t0 = time.time()
        try:
            symbolic = self._ast_adapter.convert(canonical.tree)
            steps.append(self._step("symbolic_conversion", t0, True))
        except Exception as exc:
            steps.append(self._step("symbolic_conversion", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 7. Question Generation (includes constraint validation)
        t0 = time.time()
        try:
            question = self._generator.generate(
                template=semantic,
                signature=sig,
                symbolic_expr=symbolic,
                main_variable=source.main_variable,
            )
            steps.append(self._step("question_generation", t0, True))
        except Exception as exc:
            steps.append(self._step("question_generation", t0, False))
            return self._error_package(question_id, source, steps, str(exc))

        # 8. Diagram Generation
        t0 = time.time()
        try:
            diagram_templates, rendered_svgs = self._generate_diagrams(
                source, question,
            )
            steps.append(self._step("diagram_generation", t0, True))
        except Exception as exc:
            diagram_templates = []
            rendered_svgs = []
            steps.append(self._step("diagram_generation", t0, False))

        # 9. Package
        total_ms = (time.time() - start) * 1000.0

        clean_assignments = self._compute_clean_assignments(
            question.variable_assignments, semantic, sig,
        )

        intermediate = IntermediateResults(
            ast=ast,
            canonical_result=canonical,
            template_signature=sig,
            discovery_result=discovery,
            symbolic_expr=symbolic,
        )

        pkg_meta = PipelineMetadata(
            pipeline_version=self._config.pipeline_version,
            generation_time_ms=total_ms,
            pipeline_steps=steps,
        )

        return GeneratedQuestionPackage(
            question_id=question.question_id,
            template_id=question.template_id,
            version=question.version,
            source_text=source.text,
            rendered_question=question.rendered_question,
            variable_assignments=clean_assignments,
            expected_answer=question.expected_answer,
            semantic_template=semantic,
            validation_report=question.validation_report,
            diagram_templates=diagram_templates,
            rendered_svgs=rendered_svgs,
            metadata=pkg_meta,
            generation_stats=question.generation_stats,
            intermediate_results=intermediate,
        )

    # ──────────────────────────────────────────────────────────────────
    # Individual steps (exposed for testing / partial runs)
    # ──────────────────────────────────────────────────────────────────

    def run_expression(self, text: str) -> dict:
        ast = self._parse(text)
        canonical = self._canonicalizer.canonicalize(ast)
        sig = self._sig_builder.build(canonical.tree)
        discovery = self._var_discovery.discover(canonical.tree)
        semantic = self._semantic_builder.build(sig, discovery.graph)
        symbolic = self._ast_adapter.convert(canonical.tree)
        return {
            "ast": ast,
            "canonical": canonical,
            "signature": sig,
            "discovery": discovery,
            "semantic": semantic,
            "symbolic": symbolic,
        }

    def run_equation(self, text: str, variable: str = "x") -> dict:
        result = self.run_expression(text)
        result["equation_result"] = self._eq_engine.solve(
            result["symbolic"], variable,
        )
        return result

    def evaluate_with_values(
        self, text: str, values: dict[str, float],
    ) -> float:
        from src.symbolic import EvaluationEngine
        ast = self._parse(text)
        canonical = self._canonicalizer.canonicalize(ast)
        symbolic = self._ast_adapter.convert(canonical.tree)
        eval_engine = EvaluationEngine(self._symbolic_backend)
        return eval_engine.evaluate_with_values(symbolic, values)

    def generate_question(
        self,
        source: QuestionSource,
    ) -> GeneratedQuestion:
        expr = self.run_expression(source.text)
        return self._generator.generate(
            template=expr["semantic"],
            signature=expr["signature"],
            symbolic_expr=expr["symbolic"],
            main_variable=source.main_variable,
        )

    def build_diagram(
        self,
        spec: DiagramSpec,
        template_id: str = "diag_int",
    ) -> DiagramTemplate | None:
        plugin = self._plugin_registry.get_for_type(spec.type)
        if plugin is None:
            return None
        return plugin.build_template(
            spec.properties, template_id=template_id,
        )

    def render_diagram(
        self, diagram: DiagramTemplate,
        variables: dict[str, Any] | None = None,
    ) -> str:
        return self._svgr.render(diagram, variables)

    # ──────────────────────────────────────────────────────────────────
    # Internals
    # ──────────────────────────────────────────────────────────────────

    def _parse(self, text: str) -> Any:
        tokens = self._tokenizer_cls(text).tokenize()
        self._lexer.validate(tokens)
        return Parser(tokens).parse()

    def _generate_diagrams(
        self,
        source: QuestionSource,
        question: GeneratedQuestion,
    ) -> tuple[list[DiagramTemplate], list[str]]:
        templates: list[DiagramTemplate] = []
        svgs: list[str] = []

        if not source.diagram_specs:
            return templates, svgs

        assignments = dict(question.variable_assignments)

        for spec in source.diagram_specs[:self._config.max_diagrams]:
            diagram = self.build_diagram(spec, f"diag_{len(templates)}")
            if diagram is None:
                continue

            if spec.variable_bindings:
                for prop_name, var_name in spec.variable_bindings.items():
                    for prim in diagram.primitives:
                        pass

            svg = self._svgr.render(diagram, assignments)
            templates.append(diagram)
            svgs.append(svg)

        return templates, svgs

    def _compute_clean_assignments(
        self,
        raw_assignments: dict[str, Any],
        template: SemanticTemplate,
        signature: TemplateSignature,
    ) -> dict[str, Any]:
        g = template.variable_graph
        if not isinstance(g, VariableGraph):
            return dict(raw_assignments)
        numeric: list[Any] = []
        for n in g.all_nodes():
            if n.type in (
                VariableType.CONSTANT,
                VariableType.COEFFICIENT,
                VariableType.INTEGER,
            ) and n.id in raw_assignments:
                val = raw_assignments[n.id]
                if isinstance(val, (int, float)):
                    numeric.append(val)
        clean: dict[str, Any] = {}
        for i, val in enumerate(numeric):
            if i < len(signature.variable_slots):
                slot = signature.variable_slots[i]
            else:
                slot = chr(ord("a") + i)
            clean[slot] = val
        return clean

    def _error_package(
        self,
        question_id: str,
        source: QuestionSource,
        steps: list[PipelineStep],
        error_message: str,
    ) -> GeneratedQuestionPackage:
        from src.semantic_engine import SemanticMetadata, TemplateFamily, DifficultyLevel, GeneratorType, SolverType
        from src.generator import GenerationStats

        total_ms = sum(s.duration_ms for s in steps)

        meta = PipelineMetadata(
            pipeline_version=self._config.pipeline_version,
            generation_time_ms=total_ms,
            pipeline_steps=steps,
        )

        fallback_template = _create_fallback_semantic(source.text)
        stats = GenerationStats(success=False)

        return GeneratedQuestionPackage(
            question_id=question_id,
            template_id="error",
            version="1.0.0",
            source_text=source.text,
            rendered_question=f"[Pipeline Error: {error_message}]",
            variable_assignments={},
            expected_answer=None,
            semantic_template=fallback_template,
            validation_report=None,
            diagram_templates=[],
            rendered_svgs=[],
            metadata=meta,
            generation_stats=stats,
            intermediate_results=IntermediateResults(),
        )

    @staticmethod
    def _step(name: str, start: float, success: bool) -> PipelineStep:
        return PipelineStep(
            name=name,
            duration_ms=(time.time() - start) * 1000.0,
            success=success,
        )


def _create_fallback_semantic(text: str) -> Any:
    from src.semantic_engine import (
        SemanticTemplate, SemanticMetadata,
        TemplateFamily, DifficultyLevel, GeneratorType, SolverType,
        DiagramType,
    )
    return SemanticTemplate(
        template_id="fallback",
        template_family=TemplateFamily.ALGEBRA,
        metadata=SemanticMetadata(template_id="fallback"),
        concept=f"Error processing: {text[:50]}",
    )
