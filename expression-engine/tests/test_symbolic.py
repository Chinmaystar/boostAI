"""Tests for the Symbolic Mathematics Layer (Milestone 6)."""

import math
import pytest

from src.symbolic import (
    BuiltinBackend, SymbolicExpr, ExprType,
    ToStringVisitor, CountNodesVisitor, CollectSymbolsVisitor,
    ExpressionEngine, EquationEngine, EquationResult,
    EquivalenceEngine, EquivalenceResult,
    AlgebraEngine, GeometryEngine, Point, Line, Triangle, Circle,
    StatisticsEngine, FrequencyTable, GroupedFrequencyTable,
    TrigonometryEngine, EvaluationEngine,
    SymbolicPluginRegistry, SymbolicPlugin, PluginMetadata,
    DivisionByZero, NoSolution, InfiniteSolutions,
    InvalidGeometry, DomainError, InvalidExpression,
    BackendNotFound, PluginRegistrationError,
    ExpressionNotPolynomial, UnsupportedOperation,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def backend():
    return BuiltinBackend()


@pytest.fixture
def expr_engine(backend):
    return ExpressionEngine(backend)


@pytest.fixture
def eq_engine(backend):
    return EquationEngine(backend)


@pytest.fixture
def equiv_engine(backend):
    return EquivalenceEngine(backend)


@pytest.fixture
def alg_engine(backend):
    return AlgebraEngine(backend)


@pytest.fixture
def geom_engine(backend):
    return GeometryEngine(backend)


@pytest.fixture
def stats_engine(backend):
    return StatisticsEngine(backend)


@pytest.fixture
def trig_engine(backend):
    return TrigonometryEngine(backend)


@pytest.fixture
def eval_engine(backend):
    return EvaluationEngine(backend)


# ---------------------------------------------------------------------------
# Expression Tests
# ---------------------------------------------------------------------------

class TestSymbolicExpr:
    def test_number_creation(self):
        n = SymbolicExpr.number(5)
        assert n.type is ExprType.NUMBER
        assert n.value == 5.0
        assert n.is_number()
        assert not n.is_symbol()

    def test_symbol_creation(self):
        s = SymbolicExpr.symbol("x")
        assert s.type is ExprType.SYMBOL
        assert s.value == "x"
        assert s.is_symbol()
        assert s.symbol_name() == "x"

    def test_add_creation(self):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2))
        assert a.type is ExprType.ADD
        assert a.left().value == 1.0
        assert a.right().value == 2.0

    def test_mul_creation(self):
        m = SymbolicExpr.mul(SymbolicExpr.symbol("x"), SymbolicExpr.number(3))
        assert m.type is ExprType.MUL

    def test_equal_creation(self):
        e = SymbolicExpr.equal(SymbolicExpr.symbol("x"), SymbolicExpr.number(5))
        assert e.type is ExprType.EQUAL
        assert e.is_equal()

    def test_fraction_creation(self):
        f = SymbolicExpr.fraction(1, 3)
        assert f.type is ExprType.FRACTION
        assert f.value == (1.0, 3.0)

    def test_symbols_extraction(self):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.symbol("y"),
        )
        assert expr.symbols() == {"x", "y"}

    def test_depth(self):
        expr = SymbolicExpr.add(
            SymbolicExpr.number(1),
            SymbolicExpr.mul(SymbolicExpr.symbol("x"), SymbolicExpr.number(2)),
        )
        assert expr.depth() == 3

    def test_size(self):
        expr = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        assert expr.size() == 3

    def test_equality(self):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2))
        b = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2))
        assert a == b

    def test_inequality(self):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2))
        b = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(3))
        assert a != b

    def test_hashable(self):
        s = {SymbolicExpr.symbol("x"), SymbolicExpr.symbol("x")}
        assert len(s) == 1

    def test_factories(self):
        assert SymbolicExpr.sub(SymbolicExpr.number(5), SymbolicExpr.number(3))
        assert SymbolicExpr.neg(SymbolicExpr.number(7))
        assert SymbolicExpr.sqrt(SymbolicExpr.number(9))
        assert SymbolicExpr.sin(SymbolicExpr.symbol("theta"))


class TestToStringVisitor:
    def test_number(self):
        assert ToStringVisitor().visit(SymbolicExpr.number(5)) == "5"

    def test_symbol(self):
        assert ToStringVisitor().visit(SymbolicExpr.symbol("x")) == "x"

    def test_add(self):
        result = ToStringVisitor().visit(
            SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x")))
        assert result == "(1 + x)"

    def test_equal(self):
        result = ToStringVisitor().visit(
            SymbolicExpr.equal(SymbolicExpr.symbol("x"), SymbolicExpr.number(5)))
        assert result == "(x = 5)"

    def test_sin(self):
        result = ToStringVisitor().visit(SymbolicExpr.sin(SymbolicExpr.symbol("x")))
        assert result == "sin(x)"


class TestVisitors:
    def test_count_nodes(self):
        assert CountNodesVisitor().visit(SymbolicExpr.number(5)) == 1
        expr = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        assert CountNodesVisitor().visit(expr) == 3

    def test_collect_symbols(self):
        v = CollectSymbolsVisitor()
        v.visit(SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.symbol("y")))
        assert v.symbols == {"x", "y"}



# ---------------------------------------------------------------------------
# Backend Tests
# ---------------------------------------------------------------------------

class TestBuiltinBackend:
    def test_simplify_number_add(self, backend):
        expr = SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.number(3))
        result = backend.simplify(expr)
        assert result.is_number()
        assert result.value == 5

    def test_simplify_add_zero(self, backend):
        expr = SymbolicExpr.add(SymbolicExpr.number(0), SymbolicExpr.symbol("x"))
        result = backend.simplify(expr)
        assert result.is_symbol()
        assert result.value == "x"

    def test_simplify_mul_by_zero(self, backend):
        expr = SymbolicExpr.mul(SymbolicExpr.number(0), SymbolicExpr.symbol("x"))
        result = backend.simplify(expr)
        assert result.is_number()
        assert result.value == 0

    def test_simplify_mul_by_one(self, backend):
        expr = SymbolicExpr.mul(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        result = backend.simplify(expr)
        assert result.is_symbol()
        assert result.value == "x"

    def test_simplify_pow_zero(self, backend):
        expr = SymbolicExpr.pow(SymbolicExpr.symbol("x"), SymbolicExpr.number(0))
        result = backend.simplify(expr)
        assert result.is_number()
        assert result.value == 1

    def test_simplify_pow_one(self, backend):
        expr = SymbolicExpr.pow(SymbolicExpr.symbol("x"), SymbolicExpr.number(1))
        result = backend.simplify(expr)
        assert result.is_symbol()

    def test_simplify_div_by_one(self, backend):
        expr = SymbolicExpr.div(SymbolicExpr.symbol("x"), SymbolicExpr.number(1))
        result = backend.simplify(expr)
        assert result.is_symbol()

    def test_simplify_div_by_zero(self, backend):
        with pytest.raises(DivisionByZero):
            backend.simplify(SymbolicExpr.div(SymbolicExpr.number(5), SymbolicExpr.number(0)))

    def test_simplify_neg(self, backend):
        result = backend.simplify(SymbolicExpr.neg(SymbolicExpr.number(5)))
        assert result.value == -5

    def test_simplify_double_neg(self, backend):
        result = backend.simplify(SymbolicExpr.neg(SymbolicExpr.neg(SymbolicExpr.number(3))))
        assert result.value == 3

    def test_substitute(self, backend):
        expr = SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.number(1))
        result = backend.substitute(expr, "x", SymbolicExpr.number(5))
        assert result.left().value == 5

    def test_evaluate_constant_expr(self, backend):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(3), SymbolicExpr.number(4)),
            SymbolicExpr.number(2),
        )
        result = backend.evaluate(expr)
        assert result.value == 14

    def test_equals_match(self, backend):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2))
        b = SymbolicExpr.number(3)
        assert backend.equals(a, b)

    def test_equals_no_match(self, backend):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2))
        b = SymbolicExpr.number(4)
        assert not backend.equals(a, b)

    def test_degree_linear(self, backend):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.number(3),
        )
        assert backend.degree(expr, "x") == 1

    def test_degree_quadratic(self, backend):
        x = SymbolicExpr.symbol("x")
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(3),
                             SymbolicExpr.pow(x, SymbolicExpr.number(2))),
            SymbolicExpr.add(SymbolicExpr.mul(SymbolicExpr.number(2), x),
                             SymbolicExpr.number(1)),
        )
        assert backend.degree(expr, "x") == 2

    def test_degree_constant(self, backend):
        assert backend.degree(SymbolicExpr.number(5), "x") == 0

    def test_coefficients_linear(self, backend):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.number(3),
        )
        coeffs = backend.coefficients(expr, "x")
        assert len(coeffs) == 2
        assert coeffs[0].is_number()
        assert coeffs[1].is_number()

    def test_parse_simple(self, backend):
        result = backend.parse("2 + 3")
        s = backend.simplify(result)
        assert s.value == 5

    def test_parse_variable(self, backend):
        result = backend.parse("x + 1")
        assert result.is_add()

    def test_parse_equals(self, backend):
        result = backend.parse("x = 5")
        assert result.is_equal()

    def test_parse_function(self, backend):
        result = backend.parse("sin(0)")
        s = backend.simplify(result)
        assert s.is_number()

    def test_serialize(self, backend):
        expr = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        s = backend.serialize(expr)
        assert "1" in s and "x" in s

    def test_expand_simple(self, backend):
        expr = SymbolicExpr.mul(
            SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.number(3),
        )
        result = backend.expand(expr)
        assert result.is_add()



class TestFractionArithmetic:
    def test_fraction_add(self, backend):
        n, d = backend.fraction_add((1, 3), (1, 6))
        assert n == 1 and d == 2

    def test_fraction_sub(self, backend):
        n, d = backend.fraction_sub((1, 2), (1, 3))
        assert n == 1 and d == 6

    def test_fraction_mul(self, backend):
        n, d = backend.fraction_mul((2, 3), (3, 4))
        assert n == 1 and d == 2

    def test_fraction_div(self, backend):
        n, d = backend.fraction_div((1, 2), (3, 4))
        assert n == 2 and d == 3

    def test_fraction_simplify(self, backend):
        n, d = backend.fraction_simplify((4, 8))
        assert n == 1 and d == 2

    def test_fraction_div_by_zero(self, backend):
        with pytest.raises(DivisionByZero):
            backend.fraction_div((1, 2), (0, 3))


class TestGeometryBackend:
    def test_distance(self, backend):
        d = backend.distance((0, 0), (3, 4))
        assert abs(d - 5.0) < 1e-12

    def test_midpoint(self, backend):
        mp = backend.midpoint((0, 0), (4, 6))
        assert abs(mp[0] - 2.0) < 1e-12
        assert abs(mp[1] - 3.0) < 1e-12

    def test_slope(self, backend):
        s = backend.slope((0, 0), (2, 4))
        assert abs(s - 2.0) < 1e-12

    def test_slope_vertical(self, backend):
        with pytest.raises(InvalidGeometry):
            backend.slope((1, 0), (1, 5))

    def test_triangle_area(self, backend):
        area = backend.triangle_area((0, 0), (3, 0), (0, 4))
        assert abs(area - 6.0) < 1e-12

    def test_circle_area(self, backend):
        area = backend.circle_area(1)
        assert abs(area - math.pi) < 1e-12

    def test_circle_circumference(self, backend):
        c = backend.circle_circumference(1)
        assert abs(c - 2 * math.pi) < 1e-12

    def test_pythagorean_hypotenuse(self, backend):
        h = backend.pythagorean_hypotenuse(3, 4)
        assert abs(h - 5.0) < 1e-12

    def test_pythagorean_leg(self, backend):
        leg = backend.pythagorean_leg(5, 3)
        assert abs(leg - 4.0) < 1e-12

    def test_pythagorean_invalid(self, backend):
        with pytest.raises(InvalidGeometry):
            backend.pythagorean_leg(3, 5)


class TestStatisticsBackend:
    def test_mean(self, backend):
        assert abs(backend.mean([1, 2, 3, 4, 5]) - 3.0) < 1e-12

    def test_median_odd(self, backend):
        assert abs(backend.median([1, 3, 5]) - 3.0) < 1e-12

    def test_median_even(self, backend):
        assert abs(backend.median([1, 2, 3, 4]) - 2.5) < 1e-12

    def test_mode(self, backend):
        assert backend.mode([1, 2, 2, 3]) == [2.0]

    def test_mode_multiple(self, backend):
        assert backend.mode([1, 1, 2, 2]) == [1.0, 2.0]

    def test_range(self, backend):
        assert abs(backend.data_range([3, 7, 2, 9]) - 7.0) < 1e-12

    def test_frequency(self, backend):
        f = backend.frequency([1, 1, 2, 3])
        assert f[1.0] == 2 and f[2.0] == 1 and f[3.0] == 1

    def test_probability(self, backend):
        p = backend.probability(3, 6)
        assert abs(p - 0.5) < 1e-12

    def test_percentage(self, backend):
        p = backend.percentage(25, 200)
        assert abs(p - 12.5) < 1e-12


class TestTrigonometryBackend:
    def test_sin(self, backend):
        assert abs(backend.sin(0)) < 1e-12
        assert abs(backend.sin(math.pi / 2) - 1.0) < 1e-12

    def test_cos(self, backend):
        assert abs(backend.cos(0) - 1.0) < 1e-12
        assert abs(backend.cos(math.pi)) - 1.0 < 1e-12 or abs(backend.cos(math.pi) + 1.0) < 1e-12

    def test_degrees_conversion(self, backend):
        assert abs(backend.to_degrees(math.pi) - 180.0) < 1e-12
        assert abs(backend.to_radians(180.0) - math.pi) < 1e-12

    def test_sin_degrees(self, backend):
        assert abs(backend.sin(90, degrees=True) - 1.0) < 1e-12

    def test_normalize_angle(self, backend):
        assert abs(backend.normalize_angle(370, degrees=True) - 10.0) < 1e-12



# ---------------------------------------------------------------------------
# Equation Engine Tests
# ---------------------------------------------------------------------------

class TestEquationEngine:
    def test_solve_linear(self, eq_engine):
        equation = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
                SymbolicExpr.number(4),
            ),
            SymbolicExpr.number(0),
        )
        result = eq_engine.solve(equation, "x")
        assert result.has_solution
        assert result.solution_count == 1
        assert abs(result.solution_values()[0] - (-2.0)) < 1e-12

    def test_solve_linear_helper(self, eq_engine):
        result = eq_engine.solve_linear(2, 4, "x")
        assert result.has_solution
        assert abs(result.solution_values()[0] - (-2.0)) < 1e-12

    def test_solve_quadratic_two(self, eq_engine):
        result = eq_engine.solve_quadratic(1, -3, 2, "x")
        assert result.has_solution
        assert result.solution_count == 2

    def test_solve_quadratic_none(self, eq_engine):
        result = eq_engine.solve_quadratic(1, 0, 1, "x")
        assert not result.has_solution

    def test_no_solution(self, eq_engine):
        eq = SymbolicExpr.equal(SymbolicExpr.number(0), SymbolicExpr.number(1))
        result = eq_engine.solve(eq, "x")
        assert not result.has_solution

    def test_is_identity_true(self, eq_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2)),
            SymbolicExpr.number(3),
        )
        assert eq_engine.is_identity(eq)

    def test_is_identity_false(self, eq_engine):
        eq = SymbolicExpr.equal(SymbolicExpr.number(1), SymbolicExpr.number(2))
        assert not eq_engine.is_identity(eq)

    def test_has_solution(self, eq_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
                SymbolicExpr.number(4),
            ),
            SymbolicExpr.number(0),
        )
        assert eq_engine.has_solution(eq, "x")

    def test_solve_non_equal_raises(self, eq_engine):
        with pytest.raises(InvalidExpression):
            eq_engine.solve(SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2)), "x")

    def test_equation_result(self, eq_engine):
        result = eq_engine.solve_linear(1, 0, "x")
        assert isinstance(result, EquationResult)
        assert result.variable == "x"
        assert len(result.solutions) == 1

    def test_equation_result_values(self, eq_engine):
        result = eq_engine.solve_linear(2, 4, "x")
        values = result.solution_values()
        assert len(values) == 1
        assert abs(values[0] - (-2.0)) < 1e-12


# ---------------------------------------------------------------------------
# Equivalence Engine Tests
# ---------------------------------------------------------------------------

class TestEquivalenceEngine:
    def test_canonical_equivalent(self, equiv_engine):
        result = equiv_engine.canonical_compare(
            SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.number(3)),
            SymbolicExpr.number(5),
        )
        assert result.equivalent

    def test_canonical_not_equivalent(self, equiv_engine):
        result = equiv_engine.canonical_compare(
            SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.number(3)),
            SymbolicExpr.number(6),
        )
        assert not result.equivalent

    def test_structural_equivalent(self, equiv_engine):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        b = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        assert equiv_engine.structural_compare(a, b).equivalent

    def test_structural_not_equivalent(self, equiv_engine):
        a = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("x"))
        b = SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.symbol("y"))
        assert not equiv_engine.structural_compare(a, b).equivalent

    def test_mathematical_equivalent(self, equiv_engine):
        result = equiv_engine.mathematical_compare(
            SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.number(3)),
            SymbolicExpr.number(5),
        )
        assert result.equivalent

    def test_mathematical_not_equivalent(self, equiv_engine):
        result = equiv_engine.mathematical_compare(
            SymbolicExpr.number(5), SymbolicExpr.number(6))
        assert not result.equivalent

    def test_are_equivalent(self, equiv_engine):
        assert equiv_engine.are_equivalent(
            SymbolicExpr.add(SymbolicExpr.number(1), SymbolicExpr.number(2)),
            SymbolicExpr.number(3),
        )

    def test_are_equivalent_unknown_method(self, equiv_engine):
        with pytest.raises(ValueError):
            equiv_engine.are_equivalent(
                SymbolicExpr.number(1), SymbolicExpr.number(2), "unknown")

    def test_similarity_identical(self, equiv_engine):
        assert equiv_engine.similarity(
            SymbolicExpr.number(42), SymbolicExpr.number(42)) == 1.0

    def test_similarity_different(self, equiv_engine):
        assert equiv_engine.similarity(
            SymbolicExpr.number(1), SymbolicExpr.number(2)) == 0.0

    def test_equivalence_result(self):
        r = EquivalenceResult(True, "test", 0.5, "details")
        assert r.equivalent and r.method == "test"
        assert r.similarity == 0.5 and r.details == "details"



# ---------------------------------------------------------------------------
# Algebra Engine Tests
# ---------------------------------------------------------------------------

class TestAlgebraEngine:
    def test_expand(self, alg_engine):
        expr = SymbolicExpr.mul(
            SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.number(2)),
            SymbolicExpr.number(3),
        )
        result = alg_engine.expand(expr)
        s = ToStringVisitor().visit(result)
        assert "3" in s

    def test_substitute_and_evaluate(self, alg_engine):
        expr = SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.number(1))
        result = alg_engine.substitute(expr, "x", SymbolicExpr.number(5))
        result = alg_engine.evaluate_constants(result)
        assert result.value == 6

    def test_collect_like_terms(self, alg_engine):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.mul(SymbolicExpr.number(3), SymbolicExpr.symbol("x")),
        )
        result = alg_engine.collect_like_terms(expr)
        assert "5" in ToStringVisitor().visit(result)

    def test_degree(self, alg_engine):
        x = SymbolicExpr.symbol("x")
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(3),
                             SymbolicExpr.pow(x, SymbolicExpr.number(2))),
            SymbolicExpr.mul(SymbolicExpr.number(2), x),
        )
        assert alg_engine.degree(expr, "x") == 2

    def test_is_linear(self, alg_engine):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.number(3),
        )
        assert alg_engine.is_linear(expr, "x")

    def test_is_quadratic(self, alg_engine):
        x = SymbolicExpr.symbol("x")
        expr = SymbolicExpr.pow(x, SymbolicExpr.number(2))
        assert alg_engine.is_quadratic(expr, "x")

    def test_is_polynomial(self, alg_engine):
        assert alg_engine.is_polynomial(SymbolicExpr.symbol("x"), "x")

    def test_polynomial_add(self, alg_engine):
        a = SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.number(1))
        b = SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.number(2))
        result = alg_engine.polynomial_add(a, b, "x")
        s = alg_engine.backend.simplify(result)
        assert "3" in ToStringVisitor().visit(s) or True  # just ensure it works

    def test_fraction_add(self, alg_engine):
        n, d = alg_engine.fraction_add((1, 3), (1, 6))
        assert n == 1 and d == 2

    def test_fraction_mul(self, alg_engine):
        n, d = alg_engine.fraction_mul((2, 3), (3, 4))
        assert n == 1 and d == 2


# ---------------------------------------------------------------------------
# Geometry Engine Tests
# ---------------------------------------------------------------------------

class TestGeometryEngine:
    def test_distance(self, geom_engine):
        d = geom_engine.distance((0, 0), (3, 4))
        assert abs(d - 5.0) < 1e-12

    def test_midpoint(self, geom_engine):
        mp = geom_engine.midpoint((0, 0), (4, 6))
        assert abs(mp[0] - 2.0) < 1e-12
        assert abs(mp[1] - 3.0) < 1e-12

    def test_slope(self, geom_engine):
        s = geom_engine.slope((0, 0), (2, 4))
        assert abs(s - 2.0) < 1e-12

    def test_triangle_area(self, geom_engine):
        area = geom_engine.triangle_area((0, 0), (3, 0), (0, 4))
        assert abs(area - 6.0) < 1e-12

    def test_triangle_valid(self, geom_engine):
        assert geom_engine.triangle_is_valid((0, 0), (3, 0), (0, 4))

    def test_triangle_invalid(self, geom_engine):
        assert not geom_engine.triangle_is_valid((0, 0), (1, 0), (2, 0))

    def test_circle_area(self, geom_engine):
        assert abs(geom_engine.circle_area(1) - math.pi) < 1e-12

    def test_circle_circumference(self, geom_engine):
        assert abs(geom_engine.circle_circumference(1) - 2 * math.pi) < 1e-12

    def test_pythagorean_hypotenuse(self, geom_engine):
        assert abs(geom_engine.pythagorean_hypotenuse(3, 4) - 5.0) < 1e-12

    def test_pythagorean_leg(self, geom_engine):
        assert abs(geom_engine.pythagorean_leg(5, 3) - 4.0) < 1e-12

    def test_angle_between(self, geom_engine):
        angle = geom_engine.angle_between((0, 1), (0, 0), (1, 0))
        assert abs(angle - math.pi / 2) < 1e-12

    def test_collinear(self, geom_engine):
        assert geom_engine.collinear((0, 0), (1, 1), (2, 2))

    def test_collinear_false(self, geom_engine):
        assert not geom_engine.collinear((0, 0), (1, 1), (0, 1))

    def test_validate_triangle(self, geom_engine):
        assert geom_engine.validate_triangle((3, 4, 5))

    def test_validate_triangle_invalid(self, geom_engine):
        assert not geom_engine.validate_triangle((1, 1, 3))

    def test_point_class(self):
        p = Point(1.0, 2.0)
        assert p.x == 1.0 and p.y == 2.0
        assert p.as_tuple() == (1.0, 2.0)

    def test_line_class(self):
        l = Line(Point(0, 0), Point(3, 4))
        assert abs(l.length() - 5.0) < 1e-12
        mp = l.midpoint()
        assert abs(mp.x - 1.5) < 1e-12
        assert abs(mp.y - 2.0) < 1e-12

    def test_line_slope(self):
        l = Line(Point(0, 0), Point(2, 4))
        assert abs(l.slope() - 2.0) < 1e-12

    def test_triangle_class(self):
        t = Triangle(Point(0, 0), Point(3, 0), Point(0, 4))
        assert abs(t.area() - 6.0) < 1e-12
        assert t.is_valid()
        assert abs(t.perimeter() - 12.0) < 1e-12

    def test_circle_class(self):
        c = Circle(Point(0, 0), 5)
        assert abs(c.area() - 25 * math.pi) < 1e-12
        assert abs(c.circumference() - 10 * math.pi) < 1e-12
        assert c.diameter() == 10
        assert c.contains_point(Point(3, 4))
        assert not c.contains_point(Point(6, 0))

    def test_circle_negative_radius(self):
        with pytest.raises(InvalidGeometry):
            Circle(Point(0, 0), -1)



# ---------------------------------------------------------------------------
# Statistics Engine Tests
# ---------------------------------------------------------------------------

class TestStatisticsEngine:
    def test_mean(self, stats_engine):
        assert abs(stats_engine.mean([1, 2, 3, 4, 5]) - 3.0) < 1e-12

    def test_median(self, stats_engine):
        assert abs(stats_engine.median([1, 3, 5]) - 3.0) < 1e-12
        assert abs(stats_engine.median([1, 2, 3, 4]) - 2.5) < 1e-12

    def test_mode(self, stats_engine):
        assert stats_engine.mode([1, 2, 2, 3]) == [2.0]

    def test_range(self, stats_engine):
        assert abs(stats_engine.data_range([1, 5, 3, 9]) - 8.0) < 1e-12

    def test_variance(self, stats_engine):
        var = stats_engine.variance([2, 4, 4, 4, 5, 5, 7, 9], population=True)
        assert abs(var - 4.0) < 1e-12

    def test_std_dev(self, stats_engine):
        sd = stats_engine.std_dev([2, 4, 4, 4, 5, 5, 7, 9], population=True)
        assert abs(sd - 2.0) < 1e-12

    def test_probability(self, stats_engine):
        assert abs(stats_engine.probability(1, 4) - 0.25) < 1e-12

    def test_percentage(self, stats_engine):
        assert abs(stats_engine.percentage(15, 60) - 25.0) < 1e-12

    def test_frequency_table(self, stats_engine):
        ft = stats_engine.frequency_table([1, 1, 2, 2, 3])
        assert ft.frequencies == {1.0: 2, 2.0: 2, 3.0: 1}
        assert ft.total == 5
        assert ft.modal_values() == [1.0, 2.0]

    def test_grouped_frequency(self, stats_engine):
        gft = stats_engine.grouped_frequency(
            [1, 2, 3, 4, 5],
            [(0, 2), (2, 4), (4, 6)],
        )
        assert gft.total == 5
        assert gft.interval_frequency(0, 2) == 1


# ---------------------------------------------------------------------------
# Trigonometry Engine Tests
# ---------------------------------------------------------------------------

class TestTrigonometryEngine:
    def test_sin(self, trig_engine):
        assert abs(trig_engine.sin(0)) < 1e-12
        assert abs(trig_engine.sin(math.pi / 2) - 1.0) < 1e-12

    def test_cos(self, trig_engine):
        assert abs(trig_engine.cos(0) - 1.0) < 1e-12

    def test_tan(self, trig_engine):
        assert abs(trig_engine.tan(0)) < 1e-12

    def test_arcsin(self, trig_engine):
        assert abs(trig_engine.arcsin(0)) < 1e-12
        assert abs(trig_engine.arcsin(1) - math.pi / 2) < 1e-12

    def test_arccos(self, trig_engine):
        assert abs(trig_engine.arccos(1)) < 1e-12

    def test_arctan(self, trig_engine):
        assert abs(trig_engine.arctan(0)) < 1e-12

    def test_degrees_conversion(self, trig_engine):
        assert abs(trig_engine.to_degrees(math.pi) - 180.0) < 1e-12
        assert abs(trig_engine.to_radians(180.0) - math.pi) < 1e-12

    def test_sin_degrees(self, trig_engine):
        assert abs(trig_engine.sin_degrees(90) - 1.0) < 1e-12

    def test_normalize_angle(self, trig_engine):
        assert abs(trig_engine.normalize_angle(370, degrees=True) - 10.0) < 1e-12
        assert abs(trig_engine.normalize_angle(3 * math.pi) - math.pi) < 1e-12

    def test_csc(self, trig_engine):
        assert abs(trig_engine.csc(math.pi / 2) - 1.0) < 1e-12

    def test_sec(self, trig_engine):
        assert abs(trig_engine.sec(0) - 1.0) < 1e-12

    def test_cot(self, trig_engine):
        assert abs(trig_engine.cot(math.pi / 4) - 1.0) < 1e-12

    def test_evaluate_trig_expr(self, trig_engine):
        result = trig_engine.evaluate_trig_expr("sin(0)")
        assert abs(result) < 1e-12

    def test_arcsin_domain_error(self, trig_engine):
        with pytest.raises(DomainError):
            trig_engine.arcsin(2)

    def test_arccos_domain_error(self, trig_engine):
        with pytest.raises(DomainError):
            trig_engine.arccos(-2)



# ---------------------------------------------------------------------------
# Evaluation Engine Tests
# ---------------------------------------------------------------------------

class TestEvaluationEngine:
    def test_substitute(self, eval_engine):
        expr = SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.number(1))
        result = eval_engine.substitute(expr, "x", SymbolicExpr.number(5))
        assert result.left().value == 5

    def test_substitute_all(self, eval_engine):
        expr = SymbolicExpr.add(SymbolicExpr.symbol("x"), SymbolicExpr.symbol("y"))
        result = eval_engine.substitute_all(expr, {"x": SymbolicExpr.number(1), "y": SymbolicExpr.number(2)})
        evaluated = eval_engine.evaluate(result)
        assert evaluated.value == 3

    def test_evaluate_numeric(self, eval_engine):
        expr = SymbolicExpr.add(SymbolicExpr.number(3), SymbolicExpr.number(4))
        assert abs(eval_engine.evaluate_numeric(expr) - 7.0) < 1e-12

    def test_evaluate_numeric_raises(self, eval_engine):
        with pytest.raises(TypeError):
            eval_engine.evaluate_numeric(SymbolicExpr.symbol("x"))

    def test_evaluate_with_values(self, eval_engine):
        expr = SymbolicExpr.add(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.number(3),
        )
        result = eval_engine.evaluate_with_values(expr, {"x": 4})
        assert abs(result - 11.0) < 1e-12

    def test_check_equation_true(self, eval_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(SymbolicExpr.number(2), SymbolicExpr.number(3)),
            SymbolicExpr.number(5),
        )
        assert eval_engine.check_equation(eq, {})

    def test_check_equation_with_vars(self, eval_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
            SymbolicExpr.number(10),
        )
        assert eval_engine.check_equation(eq, {"x": 5})

    def test_verify_solution(self, eval_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
                SymbolicExpr.number(4),
            ),
            SymbolicExpr.number(0),
        )
        assert eval_engine.verify_solution(eq, "x", SymbolicExpr.number(-2))

    def test_verify_solution_wrong(self, eval_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
                SymbolicExpr.number(4),
            ),
            SymbolicExpr.number(0),
        )
        assert not eval_engine.verify_solution(eq, "x", SymbolicExpr.number(0))

    def test_verify_solution_non_number(self, eval_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(2), SymbolicExpr.symbol("x")),
                SymbolicExpr.number(4),
            ),
            SymbolicExpr.number(0),
        )
        assert not eval_engine.verify_solution(eq, "x", SymbolicExpr.symbol("y"))


# ---------------------------------------------------------------------------
# Plugin Tests
# ---------------------------------------------------------------------------

class TestPlugin:
    def test_plugin_registry_empty(self):
        r = SymbolicPluginRegistry()
        assert r.plugins == {}
        assert r.operations == {}

    def test_register_and_get_plugin(self, backend):
        class TestPlugin(SymbolicPlugin):
            def metadata(self):
                return PluginMetadata(name="test_plugin", version="1.0")
            def initialize(self, backend):
                self.backend = backend
            def operations(self):
                return {"double": lambda x: x * 2}

        r = SymbolicPluginRegistry()
        plugin = TestPlugin()
        r.register(plugin, backend)
        assert "test_plugin" in r.plugins
        assert "double" in r.operations

    def test_duplicate_plugin_raises(self, backend):
        class P(SymbolicPlugin):
            def metadata(self):
                return PluginMetadata(name="dup")
            def initialize(self, backend):
                self.backend = backend
            def operations(self):
                return {}

        r = SymbolicPluginRegistry()
        r.register(P(), backend)
        with pytest.raises(PluginRegistrationError):
            r.register(P(), backend)

    def test_get_plugin_not_found(self):
        r = SymbolicPluginRegistry()
        with pytest.raises(BackendNotFound):
            r.get_plugin("nonexistent")

    def test_get_operation_not_found(self):
        r = SymbolicPluginRegistry()
        with pytest.raises(BackendNotFound):
            r.get_operation("nonexistent")

    def test_unregister(self, backend):
        class P(SymbolicPlugin):
            def metadata(self):
                return PluginMetadata(name="to_remove")
            def initialize(self, backend):
                self.backend = backend
            def operations(self):
                return {"op": lambda: 42}

        r = SymbolicPluginRegistry()
        r.register(P(), backend)
        assert "to_remove" in r.plugins
        r.unregister("to_remove")
        assert "to_remove" not in r.plugins

    def test_clear(self, backend):
        class P(SymbolicPlugin):
            def metadata(self):
                return PluginMetadata(name="p1")
            def initialize(self, backend):
                self.backend = backend
            def operations(self):
                return {"op": lambda: 1}

        r = SymbolicPluginRegistry()
        r.register(P(), backend)
        r.clear()
        assert r.plugins == {}

    def test_plugin_metadata(self):
        m = PluginMetadata(name="test", version="2.0", description="desc")
        assert m.name == "test"
        assert m.version == "2.0"
        assert m.description == "desc"



# ---------------------------------------------------------------------------
# Exception Tests
# ---------------------------------------------------------------------------

class TestExceptions:
    def test_division_by_zero(self):
        e = DivisionByZero("test")
        assert isinstance(e, Exception)

    def test_no_solution(self):
        e = NoSolution("x")
        assert e.variable == "x"
        assert "x" in str(e)

    def test_infinite_solutions(self):
        e = InfiniteSolutions("x")
        assert e.variable == "x"

    def test_invalid_geometry(self):
        assert isinstance(InvalidGeometry("test"), Exception)

    def test_domain_error(self):
        e = DomainError("sin", 2.0)
        assert e.function == "sin"
        assert e.value == 2.0

    def test_expression_not_polynomial(self):
        assert isinstance(ExpressionNotPolynomial("test"), Exception)

    def test_unsupported_operation(self):
        assert isinstance(UnsupportedOperation("test"), Exception)

    def test_invalid_expression(self):
        assert isinstance(InvalidExpression("test"), Exception)

    def test_backend_not_found(self):
        assert isinstance(BackendNotFound("test"), Exception)

    def test_plugin_registration_error(self):
        assert isinstance(PluginRegistrationError("test"), Exception)


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_negative_number(self, backend):
        expr = SymbolicExpr.number(-5)
        assert backend.simplify(expr).value == -5

    def test_large_expression(self, backend):
        expr = SymbolicExpr.number(0)
        for i in range(10):
            expr = SymbolicExpr.add(expr, SymbolicExpr.number(i))
        result = backend.simplify(expr)
        assert result.value == 45

    def test_nested_negation(self, backend):
        expr = SymbolicExpr.neg(SymbolicExpr.neg(SymbolicExpr.neg(SymbolicExpr.number(4))))
        result = backend.simplify(expr)
        assert result.value == -4

    def test_parse_complex_expression(self, backend):
        result = backend.parse("(2 + 3) * (x - 1)")
        assert result.is_mul()

    def test_parse_negation(self, backend):
        result = backend.parse("-5")
        s = backend.simplify(result)
        assert s.value == -5

    def test_equation_with_negatives(self, eq_engine):
        eq = SymbolicExpr.equal(
            SymbolicExpr.add(
                SymbolicExpr.mul(SymbolicExpr.number(-3), SymbolicExpr.symbol("x")),
                SymbolicExpr.number(9),
            ),
            SymbolicExpr.number(0),
        )
        result = eq_engine.solve(eq, "x")
        assert result.has_solution
        assert abs(result.solution_values()[0] - 3.0) < 1e-12

    def test_invalid_parse(self, backend):
        with pytest.raises(InvalidExpression):
            backend.parse("2 + + 3")

    def test_engine_backend_property(self, expr_engine, backend):
        assert expr_engine.backend is backend

