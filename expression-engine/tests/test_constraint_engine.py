from __future__ import annotations

import pytest

from src.variable_engine import (
    Variable, VariableType, VariableDomain, VariableMetadata,
    SourceLocation, VariableGraph,
)
from src.constraint_engine import (
    Constraint, ConstraintResult, ConstraintMetadata, Severity, RetryReason,
    ConstraintValidationResult, Diagnostic, ValidationStats,
    ConstraintGraph, DependencyEdge,
    ConstraintRegistry,
    ConstraintValidator,
    register_builtins,
    # Individual constraints
    NonZeroDenominator,
    IntegerConstraint,
    PrimeNumber,
    CompositeNumber,
    PerfectSquare,
    PerfectCube,
    FactorisablePolynomial,
    UniqueRoots,
    IntegerSolution,
    PositiveRadius,
    PositiveLength,
    PositiveArea,
    TriangleInequality,
    DistinctCoordinates,
    CoordinateUniqueness,
    ProbabilityRange,
    PercentageRange,
    GraphBounds,
    AxisLimits,
    Monotonicity,
    DomainRestrictions,
    RangeRestrictions,
    DuplicateVariablePrevention,
    ExpressionValidity,
)


# =========================================================================
# Helpers
# =========================================================================

def make_var(
    vid: str,
    name: str,
    type_: VariableType,
    value: object = 0,
) -> Variable:
    return Variable(
        id=vid, name=name, type=type_,
        original_value=value, canonical_value=value,
        domain=VariableDomain(),
        metadata=VariableMetadata(ast_node_type="ConstantNode"),
    )


def graph_with_one_var(vid: str, vtype: VariableType) -> VariableGraph:
    g = VariableGraph()
    v = make_var(vid, vid, vtype)
    g.add_node(v)
    return g


def graph_with_radius(vid: str = "r") -> VariableGraph:
    return graph_with_one_var(vid, VariableType.RADIUS)


def graph_with_length(*vids: str) -> VariableGraph:
    g = VariableGraph()
    for v in vids:
        g.add_node(make_var(v, v, VariableType.LENGTH))
    return g


def graph_with_area(vid: str = "area") -> VariableGraph:
    return graph_with_one_var(vid, VariableType.AREA)


def graph_with_coordinate(vid: str = "pt",
                          coord_type: VariableType = VariableType.POINT) -> VariableGraph:
    return graph_with_one_var(vid, coord_type)


def graph_with_probability(vid: str = "p") -> VariableGraph:
    return graph_with_one_var(vid, VariableType.PROBABILITY)


def graph_with_percentage(vid: str = "pct") -> VariableGraph:
    return graph_with_one_var(vid, VariableType.PERCENTAGE)


def canonical_ast(expr: str):
    from src.tokenizer import Tokenizer
    from src.lexer import Lexer
    from src.parser import Parser
    from src.canonicalizer import Canonicalizer
    tokens = Tokenizer(expr).tokenize()
    Lexer().validate(tokens)
    ast = Parser(tokens).parse()
    return Canonicalizer(rename_variables=False).canonicalize(ast).tree


def graph_with_expression() -> VariableGraph:
    g = VariableGraph()
    expr = make_var("e1", "expr_+", VariableType.EXPRESSION, value="+")
    const = make_var("c1", "const_5", VariableType.CONSTANT, value=5)
    g.add_node(expr)
    g.add_node(const)
    g.add_edge("e1", "c1", "contains")
    return g


# =========================================================================
# Severity Tests
# =========================================================================

class TestSeverity:

    def test_values(self):
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"


# =========================================================================
# RetryReason Tests
# =========================================================================

class TestRetryReason:

    def test_values(self):
        assert RetryReason.ZERO_DENOMINATOR.value == "zero_denominator"
        assert RetryReason.NEGATIVE_RADIUS.value == "negative_radius"
        assert RetryReason.INVALID_TRIANGLE.value == "invalid_triangle"

    def test_default(self):
        assert RetryReason.NONE.value == "none"


# =========================================================================
# ConstraintMetadata Tests
# =========================================================================

class TestConstraintMetadata:

    def test_create(self):
        m = ConstraintMetadata(
            id="test_con", name="Test", description="Test constraint",
            domain="test",
        )
        assert m.id == "test_con"
        assert m.priority == 100

    def test_to_dict(self):
        m = ConstraintMetadata(
            id="tc", name="Test", description="Testing",
            domain="test", version="2.0.0", priority=50,
        )
        d = m.to_dict()
        assert d["id"] == "tc"
        assert d["version"] == "2.0.0"
        assert d["priority"] == 50


# =========================================================================
# ConstraintResult Tests
# =========================================================================

class TestConstraintResult:

    def test_passed(self):
        r = ConstraintResult(
            constraint_id="c1", passed=True,
            message="OK",
        )
        assert r.passed is True
        assert r.severity == Severity.ERROR

    def test_failed(self):
        r = ConstraintResult(
            constraint_id="c1", passed=False,
            severity=Severity.ERROR,
            retry_reason=RetryReason.ZERO_DENOMINATOR,
            variables_involved=("v1",),
            expected_condition="x != 0",
            actual_values={"v1": 0},
            message="Denominator is zero",
        )
        assert r.passed is False
        assert r.retry_reason == RetryReason.ZERO_DENOMINATOR

    def test_to_dict(self):
        r = ConstraintResult(
            constraint_id="c1", passed=True,
        )
        d = r.to_dict()
        assert d["constraint_id"] == "c1"
        assert d["passed"] is True


# =========================================================================
# Base Constraint Tests
# =========================================================================

class TestConstraintABC:

    def test_default_severity(self):
        c = NonZeroDenominator()
        assert c.severity() == Severity.ERROR

    def test_default_dependencies(self):
        c = NonZeroDenominator()
        assert c.dependencies() == []

    def test_describe(self):
        c = NonZeroDenominator()
        assert "Denominator" in c.describe()


# =========================================================================
# Diagnostic Tests
# =========================================================================

class TestDiagnostic:

    def test_create(self):
        d = Diagnostic(
            constraint_id="c1", constraint_name="Test",
            severity=Severity.ERROR, passed=False,
            message="Failed",
        )
        assert d.passed is False
        assert d.constraint_id == "c1"

    def test_to_dict(self):
        d = Diagnostic(
            constraint_id="c1", constraint_name="Test",
            severity=Severity.ERROR, passed=True,
            code="OK",
        )
        dd = d.to_dict()
        assert dd["constraint_id"] == "c1"
        assert dd["severity"] == "error"


# =========================================================================
# ValidationStats Tests
# =========================================================================

class TestValidationStats:

    def test_default(self):
        s = ValidationStats()
        assert s.total == 0

    def test_to_dict(self):
        s = ValidationStats(total=10, passed=8, failed=2)
        d = s.to_dict()
        assert d["total"] == 10
        assert d["passed"] == 8


# =========================================================================
# ConstraintValidationResult Tests
# =========================================================================

class TestConstraintValidationResult:

    def test_valid_result(self):
        r = ConstraintValidationResult(valid=True)
        assert r.valid is True
        assert r.retry_reason == RetryReason.NONE

    def test_from_results_all_pass(self):
        results = [
            ConstraintResult(constraint_id="c1", passed=True),
            ConstraintResult(constraint_id="c2", passed=True),
        ]
        cr = ConstraintValidationResult.from_results(results, trace=["c1:PASS", "c2:PASS"])
        assert cr.valid is True
        assert cr.stats.total == 2
        assert cr.stats.passed == 2

    def test_from_results_one_fail(self):
        results = [
            ConstraintResult(constraint_id="c1", passed=True),
            ConstraintResult(
                constraint_id="c2", passed=False,
                severity=Severity.ERROR,
                retry_reason=RetryReason.ZERO_DENOMINATOR,
                message="Zero denominator",
            ),
        ]
        cr = ConstraintValidationResult.from_results(results)
        assert cr.valid is False
        assert cr.stats.failed == 1
        assert cr.retry_reason == RetryReason.ZERO_DENOMINATOR

    def test_from_results_warning_only(self):
        results = [
            ConstraintResult(
                constraint_id="c1", passed=False,
                severity=Severity.WARNING,
            ),
        ]
        cr = ConstraintValidationResult.from_results(results)
        assert cr.valid is True  # warnings don't fail
        assert cr.stats.warnings == 1

    def test_to_dict(self):
        r = ConstraintValidationResult(valid=True)
        d = r.to_dict()
        assert d["valid"] is True
        assert "diagnostics" in d


# =========================================================================
# ConstraintGraph Tests
# =========================================================================

class TestConstraintGraph:

    def test_empty(self):
        g = ConstraintGraph()
        assert g.node_count() == 0
        assert g.edge_count() == 0

    def test_add_node(self):
        g = ConstraintGraph()
        g.add_node("a")
        assert g.has_node("a")

    def test_add_dependency(self):
        g = ConstraintGraph()
        g.add_dependency("dependent", "dependency")
        assert g.dependencies_of("dependent") == ["dependency"]
        assert g.dependents_of("dependency") == ["dependent"]

    def test_execution_order_simple(self):
        g = ConstraintGraph()
        g.add_dependency("b", "a")
        order = g.execution_order()
        assert order.index("a") < order.index("b")

    def test_execution_order_chain(self):
        g = ConstraintGraph()
        g.add_dependency("c", "b")
        g.add_dependency("b", "a")
        order = g.execution_order()
        assert order.index("a") < order.index("b") < order.index("c")

    def test_cycle_detection(self):
        g = ConstraintGraph()
        g.add_dependency("a", "b")
        g.add_dependency("b", "a")
        assert g.has_cycle() is True

    def test_no_cycle(self):
        g = ConstraintGraph()
        g.add_dependency("a", "b")
        assert g.has_cycle() is False

    def test_execution_order_raises_on_cycle(self):
        g = ConstraintGraph()
        g.add_dependency("a", "b")
        g.add_dependency("b", "a")
        with pytest.raises(ValueError, match="cycle"):
            g.execution_order()

    def test_to_dict(self):
        g = ConstraintGraph()
        g.add_node("a")
        d = g.to_dict()
        assert "nodes" in d
        assert "edges" in d

    def test_clear(self):
        g = ConstraintGraph()
        g.add_node("a")
        g.clear()
        assert g.node_count() == 0


# =========================================================================
# ConstraintRegistry Tests
# =========================================================================

class TestConstraintRegistry:

    def test_register(self):
        r = ConstraintRegistry()
        c = NonZeroDenominator()
        assert r.register(c) is True
        assert r.count() == 1

    def test_register_duplicate(self):
        r = ConstraintRegistry()
        r.register(NonZeroDenominator())
        assert r.register(NonZeroDenominator()) is False

    def test_register_many(self):
        r = ConstraintRegistry()
        n = register_builtins(r)
        assert n == 24
        assert r.count() == 24

    def test_get(self):
        r = ConstraintRegistry()
        c = NonZeroDenominator()
        r.register(c)
        assert r.get("non_zero_denominator") is c
        assert r.get("nonexistent") is None

    def test_get_metadata(self):
        r = ConstraintRegistry()
        c = NonZeroDenominator()
        r.register(c)
        m = r.get_metadata("non_zero_denominator")
        assert m is not None
        assert m.id == "non_zero_denominator"

    def test_get_by_domain(self):
        r = ConstraintRegistry()
        register_builtins(r)
        arith = r.get_by_domain("arithmetic")
        assert len(arith) == 7
        geom = r.get_by_domain("geometry")
        assert len(geom) == 4

    def test_get_by_ids(self):
        r = ConstraintRegistry()
        register_builtins(r)
        ids = ["positive_radius", "positive_length"]
        constraints = r.get_by_ids(ids)
        assert len(constraints) == 2

    def test_get_all_domains(self):
        r = ConstraintRegistry()
        register_builtins(r)
        domains = r.get_all_domains()
        assert "arithmetic" in domains
        assert "geometry" in domains
        assert "algebra" in domains

    def test_has(self):
        r = ConstraintRegistry()
        r.register(NonZeroDenominator())
        assert r.has("non_zero_denominator") is True
        assert r.has("nonexistent") is False

    def test_get_all(self):
        r = ConstraintRegistry()
        c = NonZeroDenominator()
        r.register(c)
        assert r.get_all() == [c]

    def test_clear(self):
        r = ConstraintRegistry()
        r.register(NonZeroDenominator())
        r.clear()
        assert r.count() == 0


# =========================================================================
# Arithmetic Constraint Tests
# =========================================================================

class TestNonZeroDenominator:

    def test_passes_when_no_denominator(self):
        g = VariableGraph()
        g.add_node(make_var("c1", "c1", VariableType.CONSTANT, value=5))
        c = NonZeroDenominator()
        result = c.validate({"c1": 5}, g)
        assert result.passed is True

    def test_fails_on_zero_denominator(self):
        g = graph_with_expression()
        c = NonZeroDenominator()
        result = c.validate({"c1": 0}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.ZERO_DENOMINATOR


class TestIntegerConstraint:

    def test_passes_on_integer(self):
        c = IntegerConstraint(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        result = c.validate({"v1": 42}, g)
        assert result.passed is True

    def test_fails_on_float(self):
        c = IntegerConstraint(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        result = c.validate({"v1": 3.14}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.NON_INTEGER_SOLUTION


class TestPrimeNumber:

    def test_passes_on_prime(self):
        c = PrimeNumber(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 17}, g).passed is True
        assert c.validate({"v1": 2}, g).passed is True
        assert c.validate({"v1": 97}, g).passed is True

    def test_fails_on_composite(self):
        c = PrimeNumber(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 4}, g).passed is False
        assert c.validate({"v1": 1}, g).passed is False

    def test_fails_on_zero(self):
        c = PrimeNumber(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 0}, g).passed is False


class TestCompositeNumber:

    def test_passes_on_composite(self):
        c = CompositeNumber(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 4}, g).passed is True
        assert c.validate({"v1": 100}, g).passed is True

    def test_fails_on_prime(self):
        c = CompositeNumber(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 17}, g).passed is False

    def test_fails_on_small_numbers(self):
        c = CompositeNumber(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 2}, g).passed is False
        assert c.validate({"v1": 3}, g).passed is False


class TestPerfectSquare:

    def test_passes(self):
        c = PerfectSquare(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 0}, g).passed is True
        assert c.validate({"v1": 1}, g).passed is True
        assert c.validate({"v1": 4}, g).passed is True
        assert c.validate({"v1": 9}, g).passed is True
        assert c.validate({"v1": 144}, g).passed is True

    def test_fails(self):
        c = PerfectSquare(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 2}, g).passed is False
        assert c.validate({"v1": 10}, g).passed is False


class TestPerfectCube:

    def test_passes(self):
        c = PerfectCube(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 0}, g).passed is True
        assert c.validate({"v1": 1}, g).passed is True
        assert c.validate({"v1": 8}, g).passed is True
        assert c.validate({"v1": 27}, g).passed is True

    def test_fails(self):
        c = PerfectCube(variable_ids=("v1",))
        g = graph_with_one_var("v1", VariableType.CONSTANT)
        assert c.validate({"v1": 2}, g).passed is False
        assert c.validate({"v1": 9}, g).passed is False


# =========================================================================
# Algebra Constraint Tests
# =========================================================================

class TestUniqueRoots:

    def test_passes_on_distinct(self):
        g = VariableGraph()
        g.add_node(make_var("x1", "x1", VariableType.SYMBOL))
        g.add_node(make_var("x2", "x2", VariableType.SYMBOL))
        c = UniqueRoots()
        assert c.validate({"x1": 3, "x2": 7}, g).passed is True

    def test_fails_on_duplicate(self):
        g = VariableGraph()
        g.add_node(make_var("x1", "x1", VariableType.SYMBOL))
        g.add_node(make_var("x2", "x2", VariableType.SYMBOL))
        c = UniqueRoots()
        result = c.validate({"x1": 5, "x2": 5}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.NON_UNIQUE_ROOT


class TestIntegerSolution:

    def test_passes_on_integer(self):
        c = IntegerSolution()
        g = graph_with_one_var("x", VariableType.SYMBOL)
        assert c.validate({"x": 7}, g).passed is True

    def test_fails_on_float(self):
        c = IntegerSolution()
        g = graph_with_one_var("x", VariableType.SYMBOL)
        assert c.validate({"x": 3.5}, g).passed is False


# =========================================================================
# Geometry Constraint Tests
# =========================================================================

class TestPositiveRadius:

    def test_passes(self):
        g = graph_with_radius("r")
        c = PositiveRadius()
        assert c.validate({"r": 5}, g).passed is True

    def test_fails_zero(self):
        g = graph_with_radius("r")
        c = PositiveRadius()
        result = c.validate({"r": 0}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.NEGATIVE_RADIUS

    def test_fails_negative(self):
        g = graph_with_radius("r")
        c = PositiveRadius()
        result = c.validate({"r": -1}, g)
        assert result.passed is False


class TestPositiveLength:

    def test_passes(self):
        g = graph_with_length("l")
        c = PositiveLength()
        assert c.validate({"l": 10}, g).passed is True

    def test_fails_zero(self):
        g = graph_with_length("l")
        c = PositiveLength()
        assert c.validate({"l": 0}, g).passed is False

    def test_fails_negative(self):
        g = graph_with_length("l")
        c = PositiveLength()
        assert c.validate({"l": -5}, g).passed is False


class TestPositiveArea:

    def test_passes(self):
        g = graph_with_area("a")
        c = PositiveArea()
        assert c.validate({"a": 100}, g).passed is True

    def test_fails_zero(self):
        g = graph_with_area("a")
        c = PositiveArea()
        assert c.validate({"a": 0}, g).passed is False

    def test_fails_negative(self):
        g = graph_with_area("a")
        c = PositiveArea()
        assert c.validate({"a": -10}, g).passed is False


class TestTriangleInequality:

    def test_dependencies(self):
        c = TriangleInequality()
        assert "positive_length" in c.dependencies()

    def test_passes_valid_triangle(self):
        g = graph_with_length("a", "b", "c")
        c = TriangleInequality()
        result = c.validate({"a": 3, "b": 4, "c": 5}, g)
        assert result.passed is True

    def test_fails_invalid_triangle(self):
        g = graph_with_length("a", "b", "c")
        c = TriangleInequality()
        result = c.validate({"a": 1, "b": 2, "c": 5}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.INVALID_TRIANGLE

    def test_passes_fewer_than_three_sides(self):
        g = graph_with_length("a", "b")
        c = TriangleInequality()
        assert c.validate({"a": 1, "b": 2}, g).passed is True


# =========================================================================
# Coordinate Constraint Tests
# =========================================================================

class TestDistinctCoordinates:

    def test_passes_on_distinct(self):
        g = VariableGraph()
        g.add_node(make_var("p1", "p1", VariableType.POINT, value=(1, 2)))
        g.add_node(make_var("p2", "p2", VariableType.POINT, value=(3, 4)))
        c = DistinctCoordinates()
        result = c.validate({"p1": (1, 2), "p2": (3, 4)}, g)
        assert result.passed is True

    def test_fails_on_duplicate(self):
        g = VariableGraph()
        g.add_node(make_var("p1", "p1", VariableType.POINT, value=(1, 2)))
        g.add_node(make_var("p2", "p2", VariableType.POINT, value=(1, 2)))
        c = DistinctCoordinates()
        result = c.validate({"p1": (1, 2), "p2": (1, 2)}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.DUPLICATE_POINT


class TestCoordinateUniqueness:

    def test_dependencies(self):
        c = CoordinateUniqueness()
        assert "distinct_coordinates" in c.dependencies()

    def test_passes_unique_x(self):
        g = VariableGraph()
        g.add_node(make_var("p1", "p1", VariableType.POINT, value=(1, 2)))
        g.add_node(make_var("p2", "p2", VariableType.POINT, value=(3, 4)))
        c = CoordinateUniqueness(axis="x")
        result = c.validate({"p1": (1, 2), "p2": (3, 4)}, g)
        assert result.passed is True

    def test_fails_duplicate_x(self):
        g = VariableGraph()
        g.add_node(make_var("p1", "p1", VariableType.POINT, value=(1, 2)))
        g.add_node(make_var("p2", "p2", VariableType.POINT, value=(1, 4)))
        c = CoordinateUniqueness(axis="x")
        result = c.validate({"p1": (1, 2), "p2": (1, 4)}, g)
        assert result.passed is False


# =========================================================================
# Statistics Constraint Tests
# =========================================================================

class TestProbabilityRange:

    def test_passes_valid(self):
        g = graph_with_probability("p")
        c = ProbabilityRange()
        assert c.validate({"p": 0}, g).passed is True
        assert c.validate({"p": 0.5}, g).passed is True
        assert c.validate({"p": 1}, g).passed is True

    def test_fails_out_of_range(self):
        g = graph_with_probability("p")
        c = ProbabilityRange()
        assert c.validate({"p": -0.1}, g).passed is False
        assert c.validate({"p": 1.1}, g).passed is False

    def test_retry_reason(self):
        g = graph_with_probability("p")
        c = ProbabilityRange()
        result = c.validate({"p": 1.5}, g)
        assert result.retry_reason == RetryReason.INVALID_PROBABILITY


class TestPercentageRange:

    def test_passes_valid(self):
        g = graph_with_percentage("pct")
        c = PercentageRange()
        assert c.validate({"pct": 0}, g).passed is True
        assert c.validate({"pct": 50}, g).passed is True
        assert c.validate({"pct": 100}, g).passed is True

    def test_fails_out_of_range(self):
        g = graph_with_percentage("pct")
        c = PercentageRange()
        assert c.validate({"pct": -1}, g).passed is False
        assert c.validate({"pct": 101}, g).passed is False


# =========================================================================
# Graph Constraint Tests
# =========================================================================

class TestGraphBounds:

    def test_passes_within_bounds(self):
        g = graph_with_one_var("v", VariableType.CONSTANT)
        c = GraphBounds(min_value=0, max_value=100, variable_ids=("v",))
        assert c.validate({"v": 50}, g).passed is True

    def test_fails_below_min(self):
        g = graph_with_one_var("v", VariableType.CONSTANT)
        c = GraphBounds(min_value=0, max_value=100, variable_ids=("v",))
        result = c.validate({"v": -1}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.GRAPH_BOUNDS_EXCEEDED

    def test_fails_above_max(self):
        g = graph_with_one_var("v", VariableType.CONSTANT)
        c = GraphBounds(min_value=0, max_value=100, variable_ids=("v",))
        result = c.validate({"v": 101}, g)
        assert result.passed is False


class TestAxisLimits:

    def test_passes_valid(self):
        g = VariableGraph()
        c = AxisLimits(axis="x")
        result = c.validate({"x_axis_min": 0, "x_axis_max": 10}, g)
        assert result.passed is True

    def test_fails_invalid(self):
        g = VariableGraph()
        c = AxisLimits(axis="x")
        result = c.validate({"x_axis_min": 10, "x_axis_max": 0}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.INVALID_AXIS_LIMITS


class TestMonotonicity:

    def test_dependencies(self):
        c = Monotonicity()
        assert "graph_bounds" in c.dependencies()

    def test_passes_increasing(self):
        g = VariableGraph()
        c = Monotonicity(direction="increasing")
        result = c.validate({"a": 1, "b": 2, "c": 3, "d": 4}, g)
        assert result.passed is True

    def test_fails_non_increasing(self):
        g = VariableGraph()
        c = Monotonicity(direction="increasing")
        result = c.validate({"a": 1, "b": 3, "c": 2}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.NON_MONOTONIC

    def test_passes_decreasing(self):
        g = VariableGraph()
        c = Monotonicity(direction="decreasing")
        result = c.validate({"a": 10, "b": 7, "c": 3}, g)
        assert result.passed is True

    def test_fails_non_decreasing(self):
        g = VariableGraph()
        c = Monotonicity(direction="decreasing")
        result = c.validate({"a": 5, "b": 5, "c": 3}, g)
        assert result.passed is False

    def test_trivially_passes_single_value(self):
        g = VariableGraph()
        c = Monotonicity(direction="increasing")
        assert c.validate({"a": 42}, g).passed is True


# =========================================================================
# Domain Constraint Tests
# =========================================================================

class TestDomainRestrictions:

    def test_passes_within_domain(self):
        g = VariableGraph()
        c = DomainRestrictions(domain_map={"v1": (0, 100)})
        assert c.validate({"v1": 50}, g).passed is True

    def test_fails_below_min(self):
        g = VariableGraph()
        c = DomainRestrictions(domain_map={"v1": (0, 100)})
        result = c.validate({"v1": -5}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.DOMAIN_VIOLATION

    def test_fails_above_max(self):
        g = VariableGraph()
        c = DomainRestrictions(domain_map={"v1": (0, 100)})
        result = c.validate({"v1": 200}, g)
        assert result.passed is False


class TestRangeRestrictions:

    def test_passes(self):
        g = VariableGraph()
        c = RangeRestrictions(range_map={"v1": (0, 50)})
        assert c.validate({"v1": 25}, g).passed is True

    def test_fails(self):
        g = VariableGraph()
        c = RangeRestrictions(range_map={"v1": (0, 50)})
        result = c.validate({"v1": 100}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.RANGE_VIOLATION


class TestDuplicateVariablePrevention:

    def test_passes_distinct(self):
        g = VariableGraph()
        c = DuplicateVariablePrevention()
        assert c.validate({"a": 1, "b": 2}, g).passed is True

    def test_fails_duplicate(self):
        g = VariableGraph()
        c = DuplicateVariablePrevention()
        result = c.validate({"a": 5, "b": 5}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.DUPLICATE_VARIABLE


class TestExpressionValidity:

    def test_passes_numeric_values(self):
        g = graph_with_expression()
        c = ExpressionValidity()
        assert c.validate({"c1": 5}, g).passed is True

    def test_fails_non_numeric(self):
        g = graph_with_expression()
        c = ExpressionValidity()
        result = c.validate({"c1": "abc"}, g)
        assert result.passed is False
        assert result.retry_reason == RetryReason.INVALID_EXPRESSION


# =========================================================================
# Validator Pipeline Tests
# =========================================================================

class TestValidatorPipeline:

    def test_validate_all_pass(self):
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = graph_with_radius("r")
        result = validator.validate(
            {"r": 5}, g,
            constraint_ids=["positive_radius", "positive_length"],
        )
        assert result.valid is True
        assert result.stats.total == 2

    def test_validate_all_builtins_no_crash(self):
        """Running all 24 constraints against any data must not raise."""
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = VariableGraph()
        g.add_node(make_var("c1", "c1", VariableType.CONSTANT, value=42))
        vals = {"c1": 42}
        result = validator.validate(vals, g)
        assert isinstance(result.valid, bool)
        assert result.stats.total == registry.count()

    def test_validate_with_failure(self):
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = graph_with_radius("r")
        result = validator.validate({"r": 0}, g)
        assert result.valid is False
        assert result.stats.failed >= 1

    def test_validate_specific_constraints(self):
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = graph_with_radius("r")
        result = validator.validate(
            {"r": -1}, g,
            constraint_ids=["positive_radius"],
        )
        assert result.valid is False
        assert len(result.diagnostics) == 1

    def test_validate_no_constraints_specified(self):
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = VariableGraph()
        result = validator.validate({}, g, constraint_ids=[])
        assert result.valid is True
        assert result.stats.total == 0

    def test_empty_registry(self):
        registry = ConstraintRegistry()
        validator = ConstraintValidator(registry)

        g = VariableGraph()
        result = validator.validate({"x": 1}, g)
        assert result.valid is True
        assert result.stats.total == 0

    def test_execution_trace(self):
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = graph_with_radius("r")
        result = validator.validate({"r": 5}, g)
        assert len(result.execution_trace) > 0
        assert all(":PASS" in t or ":FAIL" in t or ":ERROR" in t for t in result.execution_trace)


# =========================================================================
# End-to-End Integration Tests
# =========================================================================

class TestEndToEnd:

    def test_full_pipeline_no_violations(self):
        """Parse → canonicalize → discover → validate (pass)."""
        from src.canonicalizer import Canonicalizer
        from src.variable_engine import VariableDiscoveryVisitor
        from src.template_engine import TemplateSignatureBuilder

        expr = "7x + 3 = 38"
        canonical = canonical_ast(expr)
        sig = TemplateSignatureBuilder().build(canonical)
        result = VariableDiscoveryVisitor(expression=expr).discover(canonical)

        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        var_values: dict[str, object] = {}
        for v in result.registry.get_all():
            if v.type == VariableType.CONSTANT:
                var_values[v.id] = v.canonical_value
            elif v.type == VariableType.SYMBOL:
                var_values[v.id] = 5
            elif v.type == VariableType.COEFFICIENT:
                var_values[v.id] = 7

        template_constraints = [
            "non_zero_denominator", "integer_constraint", "unique_roots",
            "integer_solution", "expression_validity",
            "duplicate_variable_prevention",
        ]
        validation = validator.validate(var_values, result.graph,
                                       constraint_ids=template_constraints)
        assert validation.valid is True
        assert validation.stats.total == len(template_constraints)

    def test_invalid_values_fail_validation(self):
        from src.tokenizer import Tokenizer
        from src.lexer import Lexer
        from src.parser import Parser
        from src.canonicalizer import Canonicalizer
        from src.variable_engine import VariableDiscoveryVisitor

        expr = "7x + 3 = 38"
        tokens = Tokenizer(expr).tokenize()
        Lexer().validate(tokens)
        ast = Parser(tokens).parse()
        canonical = Canonicalizer(rename_variables=False).canonicalize(ast).tree

        result = VariableDiscoveryVisitor(expression=expr).discover(canonical)

        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        var_values: dict[str, object] = {}
        for v in result.registry.get_all():
            if v.type == VariableType.CONSTANT:
                var_values[v.id] = 10
            elif v.type == VariableType.SYMBOL:
                var_values[v.id] = 5
            elif v.type == VariableType.COEFFICIENT:
                var_values[v.id] = 0

        validation = validator.validate(var_values, result.graph)
        assert validation.valid is False

    def test_regression_large_constraint_set(self):
        """Validate that running all 24 constraints performs correctly."""
        registry = ConstraintRegistry()
        register_builtins(registry)
        validator = ConstraintValidator(registry)

        g = VariableGraph()
        for i in range(10):
            g.add_node(make_var(f"v{i}", f"v{i}", VariableType.CONSTANT, value=i))
        vals = {f"v{i}": i for i in range(10)}
        result = validator.validate(vals, g)
        assert isinstance(result.valid, bool)
        assert result.stats.total == registry.count()


# =========================================================================
# Custom Plugin Tests
# =========================================================================

class TestCustomPlugin:

    def test_register_custom_constraint(self):
        class AlwaysPass(Constraint):
            _meta = ConstraintMetadata(
                id="always_pass", name="Always Pass",
                description="Always passes", domain="custom",
            )
            @property
            def metadata(self) -> ConstraintMetadata:
                return self._meta
            def validate(self, values, graph):
                return ConstraintResult(
                    constraint_id=self._meta.id, passed=True,
                    message="Always OK",
                )

        registry = ConstraintRegistry()
        assert registry.register(AlwaysPass()) is True
        assert registry.has("always_pass")
        assert registry.count() == 1

        validator = ConstraintValidator(registry)
        result = validator.validate({"x": 1}, VariableGraph())
        assert result.valid is True

    def test_custom_constraint_fails(self):
        class AlwaysFail(Constraint):
            _meta = ConstraintMetadata(
                id="always_fail", name="Always Fail",
                description="Always fails", domain="custom",
            )
            @property
            def metadata(self) -> ConstraintMetadata:
                return self._meta
            def validate(self, values, graph):
                return ConstraintResult(
                    constraint_id=self._meta.id, passed=False,
                    severity=Severity.ERROR,
                    retry_reason=RetryReason.CONSTRAINT_VIOLATION,
                    message="Always fails",
                )

        registry = ConstraintRegistry()
        registry.register(AlwaysFail())
        validator = ConstraintValidator(registry)
        result = validator.validate({"x": 1}, VariableGraph())
        assert result.valid is False
        assert result.stats.failed == 1


# =========================================================================
# RetryReason Mapping Tests
# =========================================================================

class TestRetryReasonMapping:

    def test_all_reasons_have_retry(self):
        """Every RetryReason (except NONE) is a valid retry signal."""
        reasons = [
            RetryReason.ZERO_DENOMINATOR,
            RetryReason.NEGATIVE_RADIUS,
            RetryReason.NEGATIVE_LENGTH,
            RetryReason.NEGATIVE_AREA,
            RetryReason.INVALID_TRIANGLE,
            RetryReason.NON_INTEGER_SOLUTION,
            RetryReason.OUT_OF_RANGE,
            RetryReason.DUPLICATE_POINT,
            RetryReason.INVALID_COORDINATE,
            RetryReason.INVALID_PROBABILITY,
            RetryReason.INVALID_PERCENTAGE,
            RetryReason.NOT_PRIME,
            RetryReason.NOT_COMPOSITE,
            RetryReason.NOT_PERFECT_SQUARE,
            RetryReason.NOT_PERFECT_CUBE,
            RetryReason.NOT_FACTORISABLE,
            RetryReason.NON_UNIQUE_ROOT,
            RetryReason.GRAPH_BOUNDS_EXCEEDED,
            RetryReason.INVALID_AXIS_LIMITS,
            RetryReason.NON_MONOTONIC,
            RetryReason.DOMAIN_VIOLATION,
            RetryReason.RANGE_VIOLATION,
            RetryReason.DUPLICATE_VARIABLE,
            RetryReason.INVALID_EXPRESSION,
            RetryReason.CONSTRAINT_VIOLATION,
        ]
        for r in reasons:
            assert r.value != "none"
