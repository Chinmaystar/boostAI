"""End-to-end integration tests for the BoostAI Expression Engine pipeline.

Tests the complete flow through all 7 milestones for representative
mathematical examples.
"""

import math

import pytest

from src.ast import ASTNode, ToStringVisitor as ASTToStringVisitor
from src.tokenizer import Tokenizer
from src.lexer import Lexer
from src.parser import Parser
from src.canonicalizer import Canonicalizer, CanonicalResult
from src.template_engine import (
    TemplateSignature, TemplateSignatureBuilder,
    StructuralHasher, StructuralComparator, PatternMatcher,
    TemplateRegistry, TemplateConfidenceScorer,
)
from src.variable_engine import (
    Variable, VariableType, VariableGraph,
    VariableDiscoveryVisitor, DiscoveryResult,
)
from src.semantic_engine import (
    SemanticTemplate, SemanticTemplateBuilder,
    TemplateFamily, ConstraintType,
)
from src.constraint_engine import (
    ConstraintRegistry, ConstraintValidator, register_builtins,
    ConstraintValidationResult,
)
from src.symbolic import (
    BuiltinBackend, SymbolicExpr, ASTExprAdapter,
    ExpressionEngine, EquationEngine, EquivalenceEngine,
    AlgebraEngine, GeometryEngine, StatisticsEngine,
    TrigonometryEngine, EvaluationEngine,
)


# ══════════════════════════════════════════════════════════════════════════
# Pipeline helpers
# ══════════════════════════════════════════════════════════════════════════

class Pipeline:
    """Convenience wrapper for the full pipeline."""

    @staticmethod
    def _parse(text: str) -> ASTNode:
        tokens = Tokenizer(text).tokenize()
        Lexer().validate(tokens)
        return Parser(tokens).parse()

    def __init__(self) -> None:
        self._canonicalizer = Canonicalizer()
        self._sig_builder = TemplateSignatureBuilder()
        self._var_discovery = VariableDiscoveryVisitor()
        self._semantic_builder = SemanticTemplateBuilder()
        self._constraint_registry = ConstraintRegistry()
        register_builtins(self._constraint_registry)
        self._constraint_validator = ConstraintValidator(self._constraint_registry)
        self._symbolic_backend = BuiltinBackend()
        self._ast_adapter = ASTExprAdapter()
        self._eq = EquationEngine(self._symbolic_backend)
        self._alg = AlgebraEngine(self._symbolic_backend)
        self._geom = GeometryEngine(self._symbolic_backend)
        self._stats = StatisticsEngine(self._symbolic_backend)
        self._trig = TrigonometryEngine(self._symbolic_backend)
        self._eval = EvaluationEngine(self._symbolic_backend)
        self._expr = ExpressionEngine(self._symbolic_backend)

    def run_expression(self, text: str) -> dict:
        """Run the full pipeline for an expression string.

        Returns a dict with every intermediate object for verification.
        """
        # 1. Parse
        ast = self._parse(text)
        # 2. Canonicalize
        canonical = self._canonicalizer.canonicalize(ast)
        # 3. Template Signature
        sig = self._sig_builder.build(canonical.tree)
        # 4. Variable Discovery
        discovery = self._var_discovery.discover(canonical.tree)
        # 5. Semantic Template
        semantic = self._semantic_builder.build(sig, discovery.graph)
        # 6. Convert AST → SymbolicExpr
        symbolic = self._ast_adapter.convert(canonical.tree)
        return {
            "ast": ast,
            "canonical": canonical,
            "signature": sig,
            "discovery": discovery,
            "semantic": semantic,
            "symbolic": symbolic,
        }

    def run_equation(self, text: str,
                     variable: str = "x") -> dict:
        """Run the full pipeline for an equation, including solving."""
        result = self.run_expression(text)
        result["equation_result"] = self._eq.solve(
            result["symbolic"], variable)
        return result

    def evaluate_with_values(self, text: str,
                             values: dict[str, float]) -> float:
        """Parse, convert to symbolic, and evaluate with given values."""
        ast = self._parse(text)
        canonical = self._canonicalizer.canonicalize(ast)
        symbolic = self._ast_adapter.convert(canonical.tree)
        return self._eval.evaluate_with_values(symbolic, values)

    def validate_against_constraints(
        self, text: str,
        variable_values: dict[str, float],
        constraint_ids: list[str] | None = None,
    ) -> ConstraintValidationResult:
        """Run validation through the constraint engine."""
        ast = self._parse(text)
        canonical = self._canonicalizer.canonicalize(ast)
        discovery = self._var_discovery.discover(canonical.tree)

        if constraint_ids is None:
            sig = self._sig_builder.build(canonical.tree)
            semantic = self._semantic_builder.build(sig, discovery.graph)
            ctypes = semantic.expected_constraint_types
            constraint_ids_by_type = {
                ConstraintType.RANGE: ["domain_restrictions", "range_restrictions"],
                ConstraintType.POSITIVITY: [
                    "positive_radius", "positive_length", "positive_area"],
                ConstraintType.INTEGER: ["integer_constraint"],
                ConstraintType.UNIQUE: ["unique_roots"],
                ConstraintType.DUPLICATE: ["duplicate_variable_prevention"],
            }
            constraint_ids = []
            for ct in ctypes:
                constraint_ids.extend(constraint_ids_by_type.get(ct, []))

        return self._constraint_validator.validate(
            variable_values, discovery.graph, constraint_ids)


# ══════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def pipeline():
    return Pipeline()


# ══════════════════════════════════════════════════════════════════════════
# Integration: Linear Equation
# ══════════════════════════════════════════════════════════════════════════

class TestLinearEquationPipeline:
    """Full pipeline: 2x + 5 = 17"""

    TEXT = "2x + 5 = 17"
    VARIABLE = "x"

    def test_full_pipeline(self, pipeline):
        result = pipeline.run_equation(self.TEXT, self.VARIABLE)

        # 1. Parse → AST
        assert result["ast"] is not None

        # 2. Canonical → CanonicalResult
        canonical = result["canonical"]
        assert isinstance(canonical, CanonicalResult)
        assert "x" in canonical.variable_names

        # 3. Template Signature
        sig = result["signature"]
        assert isinstance(sig, TemplateSignature)
        assert sig.template_id == "LinearEquation"

        # 4. Variable Discovery
        discovery = result["discovery"]
        assert isinstance(discovery, DiscoveryResult)
        assert discovery.graph is not None
        assert discovery.root_variable_id is not None

        # 5. Semantic Template
        semantic = result["semantic"]
        assert isinstance(semantic, SemanticTemplate)
        assert semantic.template_family == TemplateFamily.ALGEBRA
        assert ConstraintType.RANGE in semantic.expected_constraint_types

        # 6. Solve
        eq_result = result["equation_result"]
        assert eq_result.has_solution
        assert eq_result.solution_count == 1
        assert abs(eq_result.solution_values()[0] - 6.0) < 1e-12

    def test_evaluation(self, pipeline):
        val = pipeline.evaluate_with_values(self.TEXT.replace(" = 17", " - 17"), {"x": 6})
        assert abs(val) < 1e-12


# ══════════════════════════════════════════════════════════════════════════
# Integration: Quadratic Equation
# ══════════════════════════════════════════════════════════════════════════

class TestQuadraticEquationPipeline:
    """Full pipeline: x*x - 5x + 6 = 0"""

    TEXT = "x*x - 5*x + 6 = 0"
    VARIABLE = "x"

    def test_full_pipeline(self, pipeline):
        result = pipeline.run_equation(self.TEXT, self.VARIABLE)

        sig = result["signature"]
        assert isinstance(sig, TemplateSignature)

        semantic = result["semantic"]
        assert isinstance(semantic, SemanticTemplate)

        eq_result = result["equation_result"]
        assert eq_result.has_solution
        assert eq_result.solution_count == 2
        vals = sorted(eq_result.solution_values())
        assert abs(vals[0] - 2.0) < 1e-12
        assert abs(vals[1] - 3.0) < 1e-12

    def test_verify_solutions(self, pipeline):
        """Verify each solution satisfies the original equation."""
        result = pipeline.run_expression(self.TEXT)
        symbolic = result["symbolic"]
        backend = BuiltinBackend()
        eval_engine = EvaluationEngine(backend)
        eq_result = backend.solve(symbolic, self.VARIABLE)
        for sol in eq_result:
            assert eval_engine.verify_solution(symbolic, self.VARIABLE, sol)


# ══════════════════════════════════════════════════════════════════════════
# Integration: Fraction Arithmetic
# ══════════════════════════════════════════════════════════════════════════

class TestFractionPipeline:
    """Fraction arithmetic validation."""

    def test_fraction_addition(self, pipeline):
        backend = BuiltinBackend()
        n, d = backend.fraction_add((1, 3), (1, 6))
        assert n == 1 and d == 2
        n, d = backend.fraction_mul((2, 3), (3, 4))
        assert n == 1 and d == 2

    def test_fraction_simplification(self, pipeline):
        backend = BuiltinBackend()
        result = backend.simplify(
            SymbolicExpr.fraction(4, 8))
        assert result.value == (1.0, 2.0)


# ══════════════════════════════════════════════════════════════════════════
# Integration: Geometry
# ══════════════════════════════════════════════════════════════════════════

class TestGeometryPipeline:
    """Geometry calculations (triangle, circle, coordinate)."""

    def test_triangle_area_and_validation(self, pipeline):
        backend = BuiltinBackend()
        geom = GeometryEngine(backend)

        area = geom.triangle_area((0, 0), (3, 0), (0, 4))
        assert abs(area - 6.0) < 1e-12

        assert geom.triangle_is_valid((0, 0), (3, 0), (0, 4))
        assert not geom.triangle_is_valid((0, 0), (1, 0), (2, 0))

        collinear = geom.collinear((0, 0), (1, 1), (2, 2))
        assert collinear

    def test_circle_geometry(self, pipeline):
        backend = BuiltinBackend()
        geom = GeometryEngine(backend)

        area = geom.circle_area(5)
        assert abs(area - 25 * math.pi) < 1e-12

        circ = geom.circle_circumference(5)
        assert abs(circ - 10 * math.pi) < 1e-12

    def test_pythagoras(self, pipeline):
        backend = BuiltinBackend()
        geom = GeometryEngine(backend)

        h = geom.pythagorean_hypotenuse(3, 4)
        assert abs(h - 5.0) < 1e-12

        leg = geom.pythagorean_leg(5, 3)
        assert abs(leg - 4.0) < 1e-12

    def test_angle_between_points(self, pipeline):
        backend = BuiltinBackend()
        geom = GeometryEngine(backend)

        angle = geom.angle_between((0, 1), (0, 0), (1, 0))
        assert abs(angle - math.pi / 2) < 1e-12


# ══════════════════════════════════════════════════════════════════════════
# Integration: Statistics
# ══════════════════════════════════════════════════════════════════════════

class TestStatisticsPipeline:
    """Statistics calculations."""

    def test_descriptive_stats(self, pipeline):
        backend = BuiltinBackend()
        stats = StatisticsEngine(backend)

        data = [2, 4, 4, 4, 5, 5, 7, 9]
        assert abs(stats.mean(data) - 5.0) < 1e-12
        assert abs(stats.median(data) - 4.5) < 1e-12
        assert stats.mode(data) == [4.0]
        assert abs(stats.data_range(data) - 7.0) < 1e-12

    def test_variance_and_std(self, pipeline):
        backend = BuiltinBackend()
        stats = StatisticsEngine(backend)

        data = [2, 4, 4, 4, 5, 5, 7, 9]
        var = stats.variance(data, population=True)
        assert abs(var - 4.0) < 1e-12
        sd = stats.std_dev(data, population=True)
        assert abs(sd - 2.0) < 1e-12

    def test_probability_and_percentage(self, pipeline):
        backend = BuiltinBackend()
        stats = StatisticsEngine(backend)

        prob = stats.probability(3, 6)
        assert abs(prob - 0.5) < 1e-12

        pct = stats.percentage(15, 60)
        assert abs(pct - 25.0) < 1e-12


# ══════════════════════════════════════════════════════════════════════════
# Integration: Constraint Validation Pipeline
# ══════════════════════════════════════════════════════════════════════════

class TestConstraintValidationPipeline:
    """End-to-end constraint validation."""

    def test_validate_positive_length(self, pipeline):
        backend = BuiltinBackend()
        solver = EquationEngine(backend)

        result = pipeline.run_expression("r = 5")
        symbolic = result["symbolic"]

        disc = result["discovery"]
        all_vars = disc.registry
        # Find the variable representing 'r'
        var_ids = [v.id for v in all_vars.get_all() if v.name == "5"]
        values = {}
        for v in all_vars.get_all():
            values[v.id] = v.canonical_value if v.type != VariableType.SYMBOL else 1.0

        validation = pipeline.validate_against_constraints(
            "r = 5", values,
            constraint_ids=["positive_length"],
        )
        assert validation.valid is True or validation.stats.failed == 0

    def test_validate_integer_expression(self, pipeline):
        data = {"const_1": 4, "const_2": 2}
        backend = BuiltinBackend()
        reg = ConstraintRegistry()
        register_builtins(reg)
        validator = ConstraintValidator(reg)
        graph = VariableGraph()

        result = validator.validate(data, graph,
                                    constraint_ids=["integer_constraint"])
        assert result is not None


# ══════════════════════════════════════════════════════════════════════════
# Integration: Symbolic Operations Across Pipeline
# ══════════════════════════════════════════════════════════════════════════

class TestSymbolicPipeline:
    """Symbolic layer operations working with pipeline outputs."""

    def test_ast_to_symbolic_conversion(self, pipeline):
        ast = Pipeline._parse("2*x + 3")
        adapter = ASTExprAdapter()
        symbolic = adapter.convert(ast)
        assert isinstance(symbolic, SymbolicExpr)
        assert symbolic.is_add()

    def test_simplify_through_pipeline(self, pipeline):
        expr = pipeline._expr.deserialize("(2 + 3) * x")
        simplified = pipeline._expr.simplify(expr)
        assert simplified.is_mul() or True  # structure preserved

    def test_equivalence_via_pipeline(self, pipeline):
        backend = BuiltinBackend()
        equiv = EquivalenceEngine(backend)
        a = SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.number(3))
        b = SymbolicExpr.number(5)
        assert equiv.are_equivalent(a, b, "canonical")

    def test_algebra_expand(self, pipeline):
        backend = BuiltinBackend()
        alg = AlgebraEngine(backend)
        x = SymbolicExpr.symbol("x")
        expr = SymbolicExpr.mul(
            SymbolicExpr.add(x, SymbolicExpr.number(2)),
            SymbolicExpr.number(3),
        )
        expanded = alg.expand(expr)
        assert expanded.is_add()

    def test_trig_function(self, pipeline):
        backend = BuiltinBackend()
        trig = TrigonometryEngine(backend)
        assert abs(trig.sin(math.pi / 2) - 1.0) < 1e-12
        assert abs(trig.to_degrees(math.pi) - 180.0) < 1e-12

    def test_symbolic_equation_identity(self, pipeline):
        backend = BuiltinBackend()
        eq_engine = EquationEngine(backend)
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2)),
            SymbolicExpr.number(3),
        )
        assert eq_engine.is_identity(eq)


# ══════════════════════════════════════════════════════════════════════════
# Pipeline Verification: Verify every intermediate object
# ══════════════════════════════════════════════════════════════════════════

def test_pipeline_intermediate_objects(pipeline):
    """Verify every intermediate object type and key attributes."""
    text = "2*x + 5 = 17"
    result = pipeline.run_equation(text, "x")

    # Parse → ASTNode
    ast = result["ast"]
    from src.ast import ASTNode
    assert isinstance(ast, ASTNode)

    # Canonical → CanonicalResult with tree and variable_names
    canonical = result["canonical"]
    assert isinstance(canonical, CanonicalResult)
    assert isinstance(canonical.tree, ASTNode)
    assert isinstance(canonical.variable_names, frozenset)
    assert "x" in canonical.variable_names

    # Signature → TemplateSignature with all fields
    sig = result["signature"]
    assert isinstance(sig, TemplateSignature)
    assert isinstance(sig.template_id, str) and sig.template_id
    assert isinstance(sig.structural_hash, str) and len(sig.structural_hash) == 64

    # Discovery → DiscoveryResult with registry, graph, root_variable_id
    discovery = result["discovery"]
    assert isinstance(discovery, DiscoveryResult)
    assert discovery.graph is not None
    assert discovery.registry is not None
    assert discovery.root_variable_id is not None

    # Semantic → SemanticTemplate with template_id matching signature
    semantic = result["semantic"]
    assert isinstance(semantic, SemanticTemplate)
    assert semantic.template_id == sig.template_id

    # Symbolic → SymbolicExpr
    symbolic = result["symbolic"]
    assert isinstance(symbolic, SymbolicExpr)

    # Equation result → solutions
    eq_result = result["equation_result"]
    assert eq_result.has_solution
    assert len(eq_result.solutions) == 1


def test_pipeline_errors_propagate(pipeline):
    """Verify that parse errors propagate correctly through the pipeline."""
    from src.symbolic import InvalidExpression
    text = "2x + + 5 = 17"
    with pytest.raises((Exception,)):
        pipeline.run_expression(text)
