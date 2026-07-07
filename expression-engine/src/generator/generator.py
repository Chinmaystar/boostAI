from __future__ import annotations

import time
import uuid
from typing import Any

from src.template_engine import TemplateSignature
from src.semantic_engine import SemanticTemplate
from src.constraint_engine import (
    ConstraintRegistry, ConstraintValidator, ConstraintValidationResult,
    ValidationStats, RetryReason,
    register_builtins,
)
from src.variable_engine import VariableGraph
from src.symbolic import SymbolicExpr

from .config import GeneratorConfig
from .sampler import DomainSampler
from .assignment import VariableAssignmentGenerator
from .retry import RetryManager
from .session import GeneratorSession
from .assembly import QuestionAssemblyEngine
from .plugin import GeneratorPluginRegistry
from .question import GeneratedQuestion, GenerationStats
from src.semantic_engine import ConstraintType as SemConstraintType

from .errors import (
    GeneratorError, NoValidAssignmentError, QuestionAssemblyError,
    UnsolvedError,
)


class Generator:
    def __init__(self, config: GeneratorConfig | None = None) -> None:
        self._config = config or GeneratorConfig()
        self._sampler = DomainSampler(self._config.random_seed)
        self._assignment_gen = VariableAssignmentGenerator(self._sampler)
        self._retry_mgr = RetryManager(self._config)
        self._assembly = QuestionAssemblyEngine()
        self._plugin_registry = GeneratorPluginRegistry()
        self._constraint_registry = ConstraintRegistry()
        register_builtins(self._constraint_registry)
        self._constraint_validator = ConstraintValidator(self._constraint_registry)

    @property
    def config(self) -> GeneratorConfig:
        return self._config

    @property
    def plugins(self) -> GeneratorPluginRegistry:
        return self._plugin_registry

    @property
    def sampler(self) -> DomainSampler:
        return self._sampler

    def generate(
        self,
        template: SemanticTemplate,
        signature: TemplateSignature,
        symbolic_expr: SymbolicExpr | None = None,
        main_variable: str | None = None,
    ) -> GeneratedQuestion:
        session = GeneratorSession(
            template_id=template.template_id,
            max_retries=self._config.max_retries,
        )

        var_graph = template.variable_graph
        if not isinstance(var_graph, VariableGraph):
            raise GeneratorError(
                "SemanticTemplate must have a VariableGraph attached")

        last_result: ConstraintValidationResult | None = None
        final_assignments: dict[str, Any] | None = None

        while True:
            session.record_attempt()

            assignments = self._assignment_gen.generate(
                var_graph, self._config.sampling_strategy,
            )

            if self._config.require_validation:
                session.record_validation_call()
                constraint_ids = self._resolve_constraint_ids(template)
                result = self._constraint_validator.validate(
                    assignments, var_graph, constraint_ids,
                )
                last_result = result

                if result.valid:
                    final_assignments = assignments
                    session.mark_success()
                    break

                session.record_retry(result.retry_reason)
                for diag in result.diagnostics:
                    if not diag.passed:
                        session.record_constraint_failure(
                            diag.constraint_id)
                if not session.can_retry:
                    self._retry_mgr.raise_if_exhausted(session)
                self._apply_backoff(session)
            else:
                final_assignments = assignments
                last_result = ConstraintValidationResult(
                    valid=True,
                    execution_trace=("validation_skipped",),
                    stats=ValidationStats(total=0, passed=0, failed=0, errors=0, warnings=0),
                )
                session.mark_success()
                break

        if final_assignments is None:
            self._retry_mgr.raise_if_exhausted(session)

        try:
            rendered = self._assembly.render(
                signature, final_assignments, template)
        except Exception as exc:
            raise QuestionAssemblyError(
                f"Failed to render question: {exc}") from exc

        try:
            expected_answer = self._assembly.compute_expected_answer(
                symbolic_expr, final_assignments, template, main_variable)
        except UnsolvedError:
            expected_answer = None

        question_id = f"q_{uuid.uuid4().hex[:12]}"

        stats = session.to_stats()

        return GeneratedQuestion(
            question_id=question_id,
            template_id=template.template_id,
            version=template.template_version,
            template_family=template.template_family,
            generator_type=template.generator_type,
            solver_type=template.solver_type,
            concept=template.concept,
            difficulty=template.difficulty,
            rendered_question=rendered,
            variable_assignments=final_assignments,
            expected_answer=expected_answer,
            metadata=template.metadata,
            generation_stats=stats,
            validation_report=last_result,
        )

    def _resolve_constraint_ids(
        self, template: SemanticTemplate,
    ) -> list[str] | None:
        if not template.expected_constraint_types:
            return None
        ids: list[str] = []
        mapping = {
            SemConstraintType.RANGE: [
                "domain_restrictions", "range_restrictions"],
            SemConstraintType.POSITIVITY: [
                "positive_radius", "positive_length", "positive_area"],
            SemConstraintType.INTEGER: ["integer_constraint"],
            SemConstraintType.FRACTION: ["non_zero_denominator"],
            SemConstraintType.SET: ["expression_validity"],
            SemConstraintType.PARITY: ["integer_constraint"],
            SemConstraintType.MULTIPLE: ["integer_constraint"],
            SemConstraintType.PRIME: ["prime_number"],
            SemConstraintType.PERFECT_SQUARE: ["perfect_square"],
            SemConstraintType.COPRIME: ["integer_constraint"],
            SemConstraintType.DECIMAL: ["expression_validity"],
            SemConstraintType.INEQUALITY: [
                "domain_restrictions", "range_restrictions"],
        }
        for ct in template.expected_constraint_types:
            ids.extend(mapping.get(ct, []))
        return ids if ids else None

    def _apply_backoff(self, session: GeneratorSession) -> None:
        backoff = self._retry_mgr.get_backoff_ms(session.retries)
        time.sleep(backoff / 1000.0)

    def reseed(self, seed: int) -> None:
        self._sampler.reseed(seed)
