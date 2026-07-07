"""Comprehensive tests for the Question Generation Framework."""

import time
from dataclasses import replace

import pytest

from src.generator import (
    GeneratorConfig, GeneratedQuestion, GenerationStats,
    DomainSampler, UniformSampler,
    VariableAssignmentGenerator,
    RetryManager, GeneratorSession,
    QuestionAssemblyEngine,
    GeneratorPlugin, GeneratorPluginRegistry,
    Generator,
    GeneratorError, NoValidAssignmentError,
    QuestionAssemblyError, PluginRegistrationError,
    UnsolvedError,
)
from src.variable_engine import (
    Variable, VariableType, VariableDomain, VariableMetadata,
    SourceLocation, VariableGraph,
)
from src.semantic_engine import (
    SemanticTemplate, SemanticMetadata, TemplateFamily,
    DifficultyLevel, GeneratorType, SolverType, ConstraintType,
    TemplateStatus,
)
from src.template_engine import TemplateSignature
from src.constraint_engine import (
    ConstraintValidationResult, RetryReason, Diagnostic,
    Severity, ValidationStats,
)


# ══════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_variable_graph():
    graph = VariableGraph()
    a = Variable(
        id="v_a", name="a", type=VariableType.INTEGER,
        original_value=2, canonical_value=2,
        domain=VariableDomain(min_value=1, max_value=10, is_positive=True),
        metadata=VariableMetadata(can_randomize=True),
    )
    x = Variable(
        id="v_x", name="x", type=VariableType.SYMBOL,
        original_value="x", canonical_value="x",
        domain=VariableDomain(min_value=0, max_value=0, is_integer=False),
        metadata=VariableMetadata(can_randomize=False),
    )
    b = Variable(
        id="v_b", name="b", type=VariableType.INTEGER,
        original_value=5, canonical_value=5,
        domain=VariableDomain(min_value=1, max_value=20, is_positive=True),
        metadata=VariableMetadata(can_randomize=True),
    )
    c = Variable(
        id="v_c", name="c", type=VariableType.INTEGER,
        original_value=17, canonical_value=17,
        domain=VariableDomain(min_value=1, max_value=50, is_positive=True),
        metadata=VariableMetadata(can_randomize=True),
    )
    for var in (a, x, b, c):
        graph.add_node(var)
    graph.add_edge("v_a", "v_x", "coefficient_of")
    graph.add_edge("v_x", "v_b", "contains")
    return graph


@pytest.fixture
def sample_semantic_template(sample_variable_graph):
    return SemanticTemplate(
        template_id="LinearEquation",
        template_family=TemplateFamily.ALGEBRA,
        concept="Linear Equations",
        difficulty=DifficultyLevel.MEDIUM,
        variable_graph=sample_variable_graph,
        expected_constraint_types=(ConstraintType.RANGE, ConstraintType.POSITIVITY),
        generator_type=GeneratorType.ALGEBRAIC,
        solver_type=SolverType.LINEAR,
        metadata=SemanticMetadata(
            template_id="LinearEquation",
            display_name="Linear Equation",
            status=TemplateStatus.APPROVED,
        ),
        template_version="1.0.0",
    )


@pytest.fixture
def sample_template_signature():
    return TemplateSignature(
        template_id="LinearEquation",
        template_family="Algebra",
        canonical_pattern="a*x+b=c",
        variable_slots=("a", "x", "b", "c"),
        structural_hash="abc123",
        confidence=1.0,
    )


@pytest.fixture
def sample_template_signature_expression():
    return TemplateSignature(
        template_id="LinearExpression",
        template_family="Algebra",
        canonical_pattern="a*x+b",
        variable_slots=("a", "x", "b"),
        structural_hash="def456",
        confidence=1.0,
    )


# ══════════════════════════════════════════════════════════════════════════
# DomainSampler Tests
# ══════════════════════════════════════════════════════════════════════════

class TestDomainSampler:

    def test_uniform_integer_sampling(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(min_value=1, max_value=10, is_integer=True)
        val = sampler.sample(domain, VariableType.INTEGER)
        assert isinstance(val, int)
        assert 1 <= val <= 10

    def test_uniform_decimal_sampling(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(min_value=0.0, max_value=5.0, is_integer=False)
        val = sampler.sample(domain, VariableType.DECIMAL)
        assert isinstance(val, float)
        assert 0.0 <= val <= 5.0

    def test_allowed_values_sampling(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(allowed_values=(2, 4, 6, 8, 10))
        val = sampler.sample(domain, VariableType.INTEGER)
        assert val in (2, 4, 6, 8, 10)

    def test_deterministic_seed(self):
        s1 = DomainSampler(seed=123)
        s2 = DomainSampler(seed=123)
        d = VariableDomain(min_value=1, max_value=100, is_integer=True)
        v1 = s1.sample(d, VariableType.INTEGER)
        v2 = s2.sample(d, VariableType.INTEGER)
        assert v1 == v2

    def test_different_seeds_different_values(self):
        s1 = DomainSampler(seed=123)
        s2 = DomainSampler(seed=456)
        d = VariableDomain(min_value=1, max_value=100, is_integer=True)
        v1 = s1.sample(d, VariableType.INTEGER)
        v2 = s2.sample(d, VariableType.INTEGER)
        assert v1 != v2

    def test_reseed(self):
        sampler = DomainSampler(seed=42)
        d = VariableDomain(min_value=1, max_value=100, is_integer=True)
        v1 = sampler.sample(d, VariableType.INTEGER)
        sampler.reseed(42)
        v2 = sampler.sample(d, VariableType.INTEGER)
        assert v1 == v2

    def test_positive_domain(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(is_positive=True)
        val = sampler.sample(domain, VariableType.INTEGER)
        assert val >= 1

    def test_negative_domain(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(is_negative=True)
        val = sampler.sample(domain, VariableType.INTEGER)
        assert val <= -1

    def test_probability_sampling(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(min_value=0.0, max_value=1.0)
        val = sampler.sample(domain, VariableType.PROBABILITY)
        assert 0.0 <= val <= 1.0

    def test_percentage_sampling(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(min_value=0.0, max_value=100.0)
        val = sampler.sample(domain, VariableType.PERCENTAGE)
        assert 0.0 <= val <= 100.0

    def test_angle_sampling(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(min_value=0.0, max_value=360.0)
        val = sampler.sample(domain, VariableType.ANGLE)
        assert 0.0 <= val <= 360.0

    def test_unknown_type_falls_back_to_integer(self):
        sampler = DomainSampler(seed=42)
        domain = VariableDomain(min_value=5, max_value=15)
        val = sampler.sample(domain, VariableType.CATEGORICAL)
        assert isinstance(val, int)


# ══════════════════════════════════════════════════════════════════════════
# VariableAssignmentGenerator Tests
# ══════════════════════════════════════════════════════════════════════════

class TestVariableAssignmentGenerator:

    def test_assigns_randomizable_vars(self, sample_variable_graph):
        sampler = DomainSampler(seed=42)
        gen = VariableAssignmentGenerator(sampler)
        assignments = gen.generate(sample_variable_graph)
        # v_x has can_randomize=False, should keep original "x"
        assert assignments["v_x"] == "x"
        # v_a, v_b, v_c should be sampled integers
        assert isinstance(assignments["v_a"], int)
        assert isinstance(assignments["v_b"], int)
        assert isinstance(assignments["v_c"], int)

    def test_deterministic_assignments(self, sample_variable_graph):
        gen1 = VariableAssignmentGenerator(DomainSampler(seed=42))
        gen2 = VariableAssignmentGenerator(DomainSampler(seed=42))
        a1 = gen1.generate(sample_variable_graph)
        a2 = gen2.generate(sample_variable_graph)
        for k in a1:
            assert a1[k] == a2[k], f"Mismatch for {k}"

    def test_generate_one(self):
        sampler = DomainSampler(seed=42)
        gen = VariableAssignmentGenerator(sampler)
        var = Variable(
            id="v_n", name="n", type=VariableType.INTEGER,
            original_value=0, canonical_value=0,
            domain=VariableDomain(min_value=1, max_value=10),
        )
        val = gen.generate_one(var)
        assert 1 <= val <= 10

    def test_empty_graph(self):
        sampler = DomainSampler(seed=42)
        gen = VariableAssignmentGenerator(sampler)
        assignments = gen.generate(VariableGraph())
        assert assignments == {}


# ══════════════════════════════════════════════════════════════════════════
# RetryManager Tests
# ══════════════════════════════════════════════════════════════════════════

class TestRetryManager:

    def test_should_retry_valid_result(self):
        config = GeneratorConfig(max_retries=5)
        mgr = RetryManager(config)
        session = GeneratorSession("test", 5)
        result = ConstraintValidationResult(valid=True)
        assert not mgr.should_retry(session, result)

    def test_should_retry_invalid_with_capacity(self):
        config = GeneratorConfig(max_retries=5)
        mgr = RetryManager(config)
        session = GeneratorSession("test", 5)
        result = ConstraintValidationResult(valid=False)
        assert mgr.should_retry(session, result)

    def test_should_not_retry_when_exhausted(self):
        config = GeneratorConfig(max_retries=1)
        mgr = RetryManager(config)
        session = GeneratorSession("test", 1)
        for _ in range(2):
            session.record_retry(RetryReason.CONSTRAINT_VIOLATION)
        result = ConstraintValidationResult(valid=False)
        assert not mgr.should_retry(session, result)

    def test_backoff_increases(self):
        config = GeneratorConfig()
        mgr = RetryManager(config)
        assert mgr.get_backoff_ms(0) > 0
        assert mgr.get_backoff_ms(2) > mgr.get_backoff_ms(0)

    def test_raise_if_exhausted_ok_when_can_retry(self):
        config = GeneratorConfig(max_retries=5)
        mgr = RetryManager(config)
        session = GeneratorSession("test", 5)
        mgr.raise_if_exhausted(session)

    def test_raise_if_exhausted_raises(self):
        config = GeneratorConfig(max_retries=0)
        mgr = RetryManager(config)
        session = GeneratorSession("test", 0)
        session.record_retry(RetryReason.CONSTRAINT_VIOLATION)
        with pytest.raises(NoValidAssignmentError):
            mgr.raise_if_exhausted(session)

    def test_raise_if_exhausted_message_contains_reason(self):
        config = GeneratorConfig(max_retries=0)
        mgr = RetryManager(config)
        session = GeneratorSession("test", 0)
        session.record_retry(RetryReason.NEGATIVE_LENGTH)
        with pytest.raises(NoValidAssignmentError) as exc:
            mgr.raise_if_exhausted(session)
        assert "negative_length" in str(exc.value)


# ══════════════════════════════════════════════════════════════════════════
# GeneratorSession Tests
# ══════════════════════════════════════════════════════════════════════════

class TestGeneratorSession:

    def test_initial_state(self):
        s = GeneratorSession("test", 10)
        assert s.attempts == 0
        assert s.retries == 0
        assert s.can_retry
        assert s.last_retry_reason() is None

    def test_record_attempt(self):
        s = GeneratorSession("test", 10)
        s.record_attempt()
        assert s.attempts == 1

    def test_record_retry(self):
        s = GeneratorSession("test", 10)
        s.record_retry(RetryReason.OUT_OF_RANGE)
        assert s.retries == 1
        assert s.last_retry_reason() == RetryReason.OUT_OF_RANGE

    def test_can_retry_exhausted(self):
        s = GeneratorSession("test", 2)
        s.record_retry(RetryReason.CONSTRAINT_VIOLATION)
        assert s.can_retry
        s.record_retry(RetryReason.CONSTRAINT_VIOLATION)
        assert not s.can_retry

    def test_to_stats(self):
        s = GeneratorSession("test", 10)
        s.record_attempt()
        s.record_attempt()
        s.record_retry(RetryReason.OUT_OF_RANGE)
        s.record_validation_call()
        s.record_constraint_failure("range_restrictions")
        s.mark_success()
        stats = s.to_stats()
        assert stats.attempts == 2
        assert stats.retries == 1
        assert stats.validation_calls == 1
        assert stats.constraint_failures == {"range_restrictions": 1}
        assert stats.success
        assert stats.total_time_ms > 0

    def test_elapsed_ms(self):
        s = GeneratorSession("test", 10)
        start = s.elapsed_ms
        assert start >= 0

    def test_max_retries_zero(self):
        s = GeneratorSession("test", 0)
        assert not s.can_retry


# ══════════════════════════════════════════════════════════════════════════
# QuestionAssemblyEngine Tests
# ══════════════════════════════════════════════════════════════════════════

class TestQuestionAssemblyEngine:

    def test_render_substitutes_values(
        self, sample_semantic_template, sample_template_signature,
    ):
        engine = QuestionAssemblyEngine()
        assignments = {"v_a": 3, "v_x": "x", "v_b": 7, "v_c": 22}
        rendered = engine.render(
            sample_template_signature, assignments, sample_semantic_template,
        )
        assert "3" in rendered
        assert "7" in rendered
        assert "22" in rendered
        assert "x" in rendered

    def test_render_expression(
        self, sample_semantic_template, sample_template_signature_expression,
    ):
        engine = QuestionAssemblyEngine()
        assignments = {"v_a": 4, "v_x": "x", "v_b": 9}
        rendered = engine.render(
            sample_template_signature_expression,
            assignments, sample_semantic_template,
        )
        assert "4" in rendered
        assert "9" in rendered
        assert "x" in rendered

    def test_compute_expected_answer_none_no_symbolic(self):
        engine = QuestionAssemblyEngine()
        template = SemanticTemplate(
            template_id="test", template_family=TemplateFamily.ALGEBRA,
            concept="test", solver_type=SolverType.LINEAR,
        )
        answer = engine.compute_expected_answer(None, {}, template)
        assert answer is None

    def test_format_value_float(self):
        engine = QuestionAssemblyEngine()
        assert "5" in engine._format_value(5.0)
        assert "." in engine._format_value(3.14)

    def test_question_prefix_solve(self):
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.ALGEBRA,
            concept="c", solver_type=SolverType.LINEAR,
        )
        engine = QuestionAssemblyEngine()
        assert engine._question_prefix(template) == "Solve: "

    def test_question_prefix_evaluate(self):
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.ARITHMETIC,
            concept="c", solver_type=SolverType.EVALUATION,
        )
        engine = QuestionAssemblyEngine()
        assert engine._question_prefix(template) == "Evaluate: "

    def test_question_prefix_none(self):
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.ALGEBRA,
            concept="c", solver_type=SolverType.NONE,
        )
        engine = QuestionAssemblyEngine()
        assert engine._question_prefix(template) == ""


# ══════════════════════════════════════════════════════════════════════════
# GeneratorPlugin Tests
# ══════════════════════════════════════════════════════════════════════════

class DummyPlugin(GeneratorPlugin):

    def __init__(self):
        self._family = TemplateFamily.ALGEBRA

    @property
    def family(self):
        return self._family

    @family.setter
    def family(self, val):
        self._family = val

    def generate(self, template, signature, **kwargs):
        from src.generator.question import GeneratedQuestion, GenerationStats
        return GeneratedQuestion(
            question_id="dummy",
            template_id=template.template_id,
            version="1.0",
            template_family=template.template_family,
            generator_type=template.generator_type,
            solver_type=template.solver_type,
            concept=template.concept,
            difficulty=template.difficulty,
            rendered_question="dummy",
            variable_assignments={},
            expected_answer=None,
            metadata=template.metadata,
            generation_stats=GenerationStats(success=True),
        )

    def can_handle(self, template):
        return template.template_family == TemplateFamily.ALGEBRA


class TestGeneratorPlugin:

    def test_register_and_get(self):
        registry = GeneratorPluginRegistry()
        plugin = DummyPlugin()
        registry.register(plugin)
        assert registry.has(TemplateFamily.ALGEBRA)
        assert registry.get(TemplateFamily.ALGEBRA) is plugin

    def test_duplicate_registration_raises(self):
        registry = GeneratorPluginRegistry()
        registry.register(DummyPlugin())
        with pytest.raises(PluginRegistrationError):
            registry.register(DummyPlugin())

    def test_unregister(self):
        registry = GeneratorPluginRegistry()
        plugin = DummyPlugin()
        registry.register(plugin)
        registry.unregister(TemplateFamily.ALGEBRA)
        assert not registry.has(TemplateFamily.ALGEBRA)

    def test_clear(self):
        registry = GeneratorPluginRegistry()
        registry.register(DummyPlugin())
        registry.clear()
        assert not registry.has(TemplateFamily.ALGEBRA)

    def test_get_for_template(self):
        registry = GeneratorPluginRegistry()
        plugin = DummyPlugin()
        registry.register(plugin)
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.ALGEBRA,
            concept="c",
        )
        assert registry.get_for_template(template) is plugin

    def test_get_for_template_no_match(self):
        registry = GeneratorPluginRegistry()
        plugin = DummyPlugin()
        registry.register(plugin)
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.GEOMETRY,
            concept="c",
        )
        assert registry.get_for_template(template) is None

    def test_families_property(self):
        registry = GeneratorPluginRegistry()
        plugin = DummyPlugin()
        registry.register(plugin)
        assert TemplateFamily.ALGEBRA in registry.families

    def test_plugin_generates_question(self):
        plugin = DummyPlugin()
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.ALGEBRA,
            concept="c", difficulty=DifficultyLevel.EASY,
            generator_type=GeneratorType.ALGEBRAIC,
            solver_type=SolverType.LINEAR,
            metadata=SemanticMetadata(template_id="t"),
        )
        sig = TemplateSignature(
            template_id="t", template_family="Algebra",
            canonical_pattern="", variable_slots=(),
            structural_hash="h", confidence=1.0,
        )
        q = plugin.generate(template, sig)
        assert isinstance(q, GeneratedQuestion)
        assert q.question_id == "dummy"


# ══════════════════════════════════════════════════════════════════════════
# GeneratorConfig Tests
# ══════════════════════════════════════════════════════════════════════════

class TestGeneratorConfig:

    def test_default_values(self):
        config = GeneratorConfig()
        assert config.max_retries == 10
        assert config.random_seed is None
        assert config.sampling_strategy == "uniform"
        assert config.require_validation

    def test_custom_values(self):
        config = GeneratorConfig(
            max_retries=3, random_seed=42, sampling_strategy="weighted",
            require_validation=False,
        )
        assert config.max_retries == 3
        assert config.random_seed == 42
        assert config.sampling_strategy == "weighted"
        assert not config.require_validation

    def test_frozen(self):
        config = GeneratorConfig()
        with pytest.raises(Exception):
            config.max_retries = 99


# ══════════════════════════════════════════════════════════════════════════
# GeneratedQuestion Model Tests
# ══════════════════════════════════════════════════════════════════════════

class TestGeneratedQuestion:

    def test_create_valid(self):
        stats = GenerationStats(attempts=1, success=True)
        q = GeneratedQuestion(
            question_id="q_abc",
            template_id="LinearEquation",
            version="1.0.0",
            template_family=TemplateFamily.ALGEBRA,
            generator_type=GeneratorType.ALGEBRAIC,
            solver_type=SolverType.LINEAR,
            concept="Linear Equations",
            difficulty=DifficultyLevel.MEDIUM,
            rendered_question="Solve 3x + 5 = 14",
            variable_assignments={"v_a": 3, "v_b": 5, "v_c": 14},
            expected_answer=3.0,
            metadata=SemanticMetadata(template_id="LinearEquation"),
            generation_stats=stats,
        )
        assert q.question_id == "q_abc"
        assert q.template_family == TemplateFamily.ALGEBRA
        assert q.expected_answer == 3.0
        assert q.generation_stats.success

    def test_frozen(self):
        stats = GenerationStats()
        q = GeneratedQuestion(
            question_id="q", template_id="t", version="1",
            template_family=TemplateFamily.ARITHMETIC,
            generator_type=GeneratorType.ARITHMETIC,
            solver_type=SolverType.ARITHMETIC_OP,
            concept="c", difficulty=DifficultyLevel.EASY,
            rendered_question="", variable_assignments={},
            expected_answer=None,
            metadata=SemanticMetadata(template_id="t"),
            generation_stats=stats,
        )
        with pytest.raises(Exception):
            q.question_id = "changed"


# ══════════════════════════════════════════════════════════════════════════
# Error Tests
# ══════════════════════════════════════════════════════════════════════════

class TestGeneratorErrors:

    def test_generator_error(self):
        assert issubclass(NoValidAssignmentError, GeneratorError)
        assert issubclass(QuestionAssemblyError, GeneratorError)
        assert issubclass(PluginRegistrationError, GeneratorError)
        assert issubclass(UnsolvedError, GeneratorError)

    def test_no_valid_assignment_message(self):
        err = NoValidAssignmentError("test message")
        assert "test message" in str(err)


# ══════════════════════════════════════════════════════════════════════════
# Integration: Full Generator Pipeline
# ══════════════════════════════════════════════════════════════════════════

class TestGeneratorPipeline:

    def test_generator_initialization(self):
        gen = Generator()
        assert gen.config.max_retries == 10
        assert gen.config.random_seed is None

    def test_generator_custom_config(self):
        config = GeneratorConfig(max_retries=3, random_seed=42)
        gen = Generator(config)
        assert gen.config.max_retries == 3

    def test_generate_returns_question(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(random_seed=42, max_retries=5)
        gen = Generator(config)
        question = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        assert isinstance(question, GeneratedQuestion)
        assert question.template_id == "LinearEquation"
        assert question.generation_stats.success
        assert question.generation_stats.attempts >= 1

    def test_generate_sets_variable_assignments(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(random_seed=42)
        gen = Generator(config)
        question = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        assert "v_x" in question.variable_assignments
        assert question.variable_assignments["v_x"] == "x"

    def test_generate_renders_question_text(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(random_seed=42)
        gen = Generator(config)
        question = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        assert question.rendered_question
        assert "Solve:" in question.rendered_question

    def test_deterministic_generation(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(random_seed=99, max_retries=5)
        gen1 = Generator(config)
        q1 = gen1.generate(
            sample_semantic_template, sample_template_signature,
        )
        gen2 = Generator(config)
        q2 = gen2.generate(
            sample_semantic_template, sample_template_signature,
        )
        assert q1.variable_assignments == q2.variable_assignments
        assert q1.rendered_question == q2.rendered_question

    def test_reseed_produces_same_result(
        self, sample_semantic_template, sample_template_signature,
    ):
        gen = Generator(GeneratorConfig(random_seed=42))
        q1 = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        gen.reseed(42)
        q2 = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        for k in q1.variable_assignments:
            assert q1.variable_assignments[k] == q2.variable_assignments[k]

    def test_validation_report_present(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(random_seed=42)
        gen = Generator(config)
        question = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        assert question.validation_report is not None

    def test_generate_without_validation(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(
            random_seed=42, require_validation=False, max_retries=0,
        )
        gen = Generator(config)
        question = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        assert question.generation_stats.success

    def test_generate_no_variable_graph_fails(self):
        template = SemanticTemplate(
            template_id="t", template_family=TemplateFamily.ALGEBRA,
            concept="c",
        )
        sig = TemplateSignature(
            template_id="t", template_family="Algebra",
            canonical_pattern="", variable_slots=(),
            structural_hash="h", confidence=1.0,
        )
        gen = Generator()
        with pytest.raises(GeneratorError):
            gen.generate(template, sig)

    def test_generate_constraint_failure_recorded(
        self, sample_semantic_template, sample_template_signature,
    ):
        config = GeneratorConfig(random_seed=42, max_retries=5)
        gen = Generator(config)
        question = gen.generate(
            sample_semantic_template, sample_template_signature,
        )
        if not question.generation_stats.success:
            assert question.generation_stats.constraint_failures


# ══════════════════════════════════════════════════════════════════════════
# Edge Cases
# ══════════════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_empty_graph_no_assignments(self):
        sampler = DomainSampler(seed=42)
        gen = VariableAssignmentGenerator(sampler)
        assignments = gen.generate(VariableGraph())
        assert assignments == {}

    def test_plugin_registry_empty_initial_state(self):
        registry = GeneratorPluginRegistry()
        assert registry.families == []
        assert not registry.has(TemplateFamily.ALGEBRA)

    def test_session_max_retries_zero_cannot_retry(self):
        s = GeneratorSession("test", 0)
        assert not s.can_retry

    def test_session_no_retries_last_reason_none(self):
        s = GeneratorSession("test", 5)
        assert s.last_retry_reason() is None

    def test_session_single_retry_reason(self):
        s = GeneratorSession("test", 5)
        s.record_retry(RetryReason.ZERO_DENOMINATOR)
        assert s.last_retry_reason() == RetryReason.ZERO_DENOMINATOR

    def test_session_multiple_retry_reasons(self):
        s = GeneratorSession("test", 5)
        s.record_retry(RetryReason.OUT_OF_RANGE)
        s.record_retry(RetryReason.NEGATIVE_LENGTH)
        assert s.last_retry_reason() == RetryReason.NEGATIVE_LENGTH

    def test_generation_stats_defaults(self):
        stats = GenerationStats()
        assert stats.attempts == 0
        assert stats.retries == 0
        assert not stats.success
        assert stats.constraint_failures == {}
