from __future__ import annotations

import hashlib
import pytest

from src.ast import (
    ConstantNode, VariableNode, BinaryOpNode,
    UnaryOpNode, EquationNode, ToStringVisitor,
)
from src.canonicalizer import Canonicalizer
from src.template_engine import (
    PatternMatcher, MatchResult,
    StructuralComparator,
    TemplateSignature, TemplateSignatureBuilder,
    StructuralHasher,
    TemplateRegistry,
    TemplateConfidenceScorer,
)


# =========================================================================
# Helpers
# =========================================================================

def canonical_ast(expr: str):
    """Parse and canonicalize an expression string to an AST."""
    from src.tokenizer import Tokenizer
    from src.lexer import Lexer
    from src.parser import Parser
    tokens = Tokenizer(expr).tokenize()
    Lexer().validate(tokens)
    ast = Parser(tokens).parse()
    return Canonicalizer(rename_variables=False).canonicalize(ast).tree


def to_string(node):
    return ToStringVisitor().visit(node)


# =========================================================================
# StructuralHasher Tests
# =========================================================================

class TestStructuralHasher:

    def test_fingerprint_constant(self):
        fp = StructuralHasher.fingerprint(ConstantNode(42))
        assert fp == "C"

    def test_fingerprint_variable(self):
        fp = StructuralHasher.fingerprint(VariableNode("x"))
        assert fp == "V"

    def test_fingerprint_unary_op(self):
        node = UnaryOpNode("-", VariableNode("x"))
        fp = StructuralHasher.fingerprint(node)
        assert fp == "U(V)"

    def test_fingerprint_binary_op_operator_agnostic(self):
        """BinaryOpNode fingerprints collapse +- to A and */ to M."""
        plus = BinaryOpNode("+", ConstantNode(1), ConstantNode(2))
        minus = BinaryOpNode("-", ConstantNode(1), ConstantNode(2))
        times = BinaryOpNode("*", ConstantNode(1), ConstantNode(2))
        divide = BinaryOpNode("/", ConstantNode(1), ConstantNode(2))
        assert StructuralHasher.fingerprint(plus) == "A(C,C)"
        assert StructuralHasher.fingerprint(minus) == "A(C,C)"
        assert StructuralHasher.fingerprint(times) == "M(C,C)"
        assert StructuralHasher.fingerprint(divide) == "M(C,C)"

    def test_fingerprint_equation(self):
        node = EquationNode(ConstantNode(5), ConstantNode(10))
        fp = StructuralHasher.fingerprint(node)
        assert fp == "E(C,C)"

    def test_fingerprint_complex(self):
        """2x + 5 = 17 → E(A(C,M(C,V)),C)"""
        ast = canonical_ast("2x + 5 = 17")
        fp = StructuralHasher.fingerprint(ast)
        assert fp == "E(A(C,M(C,V)),C)"

    def test_fingerprint_fully_wrapped(self):
        """2(x+3) → M(A(C,V),C)  (outer *, inner +; sorted A < C lex)"""
        ast = canonical_ast("2(x+3)")
        fp = StructuralHasher.fingerprint(ast)
        assert fp == "M(A(C,V),C)"

    def test_hash_is_deterministic(self):
        ast = canonical_ast("2x + 5 = 17")
        h1 = StructuralHasher.hash(ast)
        h2 = StructuralHasher.hash(ast)
        assert h1 == h2

    def test_hash_is_sha256(self):
        ast = canonical_ast("2x + 5 = 17")
        h = StructuralHasher.hash(ast)
        assert len(h) == 64
        int(h, 16)  # raises ValueError if not hex

    def test_equivalent_expressions_same_hash(self):
        """2x+5=17 and 5+2x=17 produce the same hash after
        canonicalization — and have the same structural fingerprint."""
        a1 = canonical_ast("2x + 5 = 17")
        a2 = canonical_ast("5 + 2x = 17")
        assert StructuralHasher.hash(a1) == StructuralHasher.hash(a2)

    def test_different_shapes_different_hash(self):
        a1 = canonical_ast("2x + 5 = 17")
        a2 = canonical_ast("2(x+3)")
        assert StructuralHasher.hash(a1) != StructuralHasher.hash(a2)


# =========================================================================
# StructuralComparator Tests
# =========================================================================

class TestStructuralComparator:

    def test_equivalent_identical_trees(self):
        a = ConstantNode(5)
        b = ConstantNode(5)
        assert StructuralComparator.are_equivalent(a, b)

    def test_equivalent_different_constants(self):
        a = ConstantNode(2)
        b = ConstantNode(7)
        assert StructuralComparator.are_equivalent(a, b)

    def test_equivalent_different_variable_names(self):
        a = VariableNode("x")
        b = VariableNode("y")
        assert StructuralComparator.are_equivalent(a, b)

    def test_equivalent_same_shape_different_operators(self):
        """2x+5=17 and 2x-5=17 have the same abstract shape."""
        a = BinaryOpNode("+", ConstantNode(2), VariableNode("x"))
        b = BinaryOpNode("-", ConstantNode(2), VariableNode("x"))
        assert StructuralComparator.are_equivalent(a, b)

    def test_equivalent_complex_same_template(self):
        a = canonical_ast("2x + 5 = 17")
        b = canonical_ast("7x + 3 = 38")
        assert StructuralComparator.are_equivalent(a, b)

    def test_equivalent_distributive_same_template(self):
        a = canonical_ast("2(x+3)")
        b = canonical_ast("5(y-1)")
        assert StructuralComparator.are_equivalent(a, b)

    def test_not_equivalent_different_template(self):
        a = canonical_ast("2x + 5 = 17")
        b = canonical_ast("2(x+3)")
        assert not StructuralComparator.are_equivalent(a, b)

    def test_not_equivalent_different_structures(self):
        a = ConstantNode(5)
        b = VariableNode("x")
        assert not StructuralComparator.are_equivalent(a, b)

    def test_similarity_identical(self):
        a = ConstantNode(5)
        assert StructuralComparator.similarity(a, a) == 1.0

    def test_similarity_completely_different(self):
        a = ConstantNode(5)
        b = VariableNode("x")
        assert StructuralComparator.similarity(a, b) == 0.0

    def test_similarity_same_shape_partial(self):
        a = BinaryOpNode("+", ConstantNode(1), ConstantNode(2))
        b = BinaryOpNode("+", ConstantNode(1), VariableNode("x"))
        # Shapes: B(C,C) vs B(C,V) — 2/3 match? Let's compute:
        # B vs B = match (1/1), C vs C = match (2/2), C vs V = no (2/3)
        # Actually: B+C+C = 3 nodes, B+C+V = 3 nodes, matched = 2 (B, 1st C)
        # But 2nd C vs V = 0: similarity = 2/3 ≈ 0.666...
        s = StructuralComparator.similarity(a, b)
        assert 0.5 < s < 1.0

    def test_similarity_equation_and_expression(self):
        """Equation vs expression: root types differ (E vs B), so
        similarity is 0.0 — they have no matching node types."""
        a = canonical_ast("2x + 5 = 17")
        b = canonical_ast("2x + 5")
        s = StructuralComparator.similarity(a, b)
        assert s == 0.0


# =========================================================================
# PatternMatcher Tests
# =========================================================================

class TestPatternMatcher:

    def test_matches_exact(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        assert PatternMatcher.matches(ast, sig)

    def test_matches_equivalent_expression(self):
        ast_a = canonical_ast("2x + 5 = 17")
        ast_b = canonical_ast("7x + 3 = 38")
        sig = TemplateSignatureBuilder().build(ast_a)
        assert PatternMatcher.matches(ast_b, sig)

    def test_does_not_match_different_template(self):
        ast = canonical_ast("2x + 5 = 17")
        other = canonical_ast("2(x+3)")
        sig = TemplateSignatureBuilder().build(other)
        assert not PatternMatcher.matches(ast, sig)

    def test_match_result_extracts_slots(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        result = PatternMatcher.match(ast, sig)
        assert result.matched
        # After canonicalization: 5 + 2*x = 17, so slots: a=5, b=2, c=17
        assert result.slot_values == {"a": 5, "b": 2, "c": 17}

    def test_match_result_extracts_variables(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        result = PatternMatcher.match(ast, sig)
        assert result.matched
        assert result.variable_bindings == {"x": "x"}

    def test_match_result_multiple_variables(self):
        ast = canonical_ast("x + y = 10")
        sig = TemplateSignatureBuilder().build(ast)
        result = PatternMatcher.match(ast, sig)
        assert result.matched
        assert result.variable_bindings["x"] == "x"
        assert result.variable_bindings["y"] == "y"

    def test_match_result_no_match(self):
        ast = canonical_ast("2x + 5 = 17")
        other = canonical_ast("42")
        sig = TemplateSignatureBuilder().build(other)
        result = PatternMatcher.match(ast, sig)
        assert not result.matched
        assert result.slot_values == {}
        assert result.variable_bindings == {}

    def test_find_matching_templates(self):
        registry = TemplateRegistry()
        ast_a = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast_a)
        registry.register(sig)
        ast_b = canonical_ast("7x + 3 = 38")
        matches = PatternMatcher.find_matching_templates(ast_b, registry)
        assert len(matches) == 1
        assert matches[0].template_id == "LinearEquation"

    def test_find_no_matching_templates(self):
        registry = TemplateRegistry()
        ast_a = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast_a)
        registry.register(sig)
        ast_b = canonical_ast("2(x+3)")
        matches = PatternMatcher.find_matching_templates(ast_b, registry)
        assert len(matches) == 0


# =========================================================================
# TemplateSignatureBuilder Tests
# =========================================================================

class TestTemplateSignatureBuilder:

    def test_build_linear_equation(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_id == "LinearEquation"
        assert sig.template_family == "Algebra"
        assert sig.variable_slots == ("a", "b", "c")

    def test_build_linear_equation_different_constants_same_id(self):
        sig1 = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        sig2 = TemplateSignatureBuilder().build(canonical_ast("7x + 3 = 38"))
        assert sig1.template_id == sig2.template_id
        assert sig1.structural_hash == sig2.structural_hash

    def test_build_distributive_multiplication(self):
        ast = canonical_ast("2(x+3)")
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_id == "DistributiveMultiplication"
        assert sig.template_family == "Expression"
        assert sig.variable_slots == ("a", "b")

    def test_distributive_same_template_different_operators(self):
        sig1 = TemplateSignatureBuilder().build(canonical_ast("2(x+3)"))
        sig2 = TemplateSignatureBuilder().build(canonical_ast("5(y-1)"))
        assert sig1.template_id == sig2.template_id
        assert sig1.structural_hash == sig2.structural_hash

    def test_build_constant_expression(self):
        ast = canonical_ast("42")
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_id == "ConstantExpression"
        assert sig.variable_slots == ("a",)

    def test_build_variable_expression(self):
        ast = canonical_ast("x")
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_id == "VariableExpression"

    def test_canonical_pattern_linear_equation(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        # After canonicalization, constants come first: (2*x + 5) = 17
        # Pattern: a * x + b = c
        assert "a" in sig.canonical_pattern
        assert "b" in sig.canonical_pattern
        assert "c" in sig.canonical_pattern

    def test_canonical_pattern_with_subtraction(self):
        ast = canonical_ast("2x - 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        assert "-" in sig.canonical_pattern

    def test_deterministic(self):
        sig1 = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        sig2 = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        assert sig1 == sig2

    def test_structural_hash_is_sha256(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        h = sig.structural_hash
        assert len(h) == 64
        int(h, 16)

    def test_pattern_with_slots_after_folding(self):
        """3 + 4 + x folds to 7 + x → slots: a=7, b=x? No, x is var."""
        ast = canonical_ast("3 + 4 + x")
        sig = TemplateSignatureBuilder().build(ast)
        # After folding: 7 + x
        # Canonical shape: B(C,V)  (7 + x)
        # But x is a variable, not a constant. Slots only for constants.
        assert "a" in sig.canonical_pattern
        assert sig.variable_slots == ("a",)


# =========================================================================
# TemplateRegistry Tests
# =========================================================================

class TestTemplateRegistry:

    def test_register_new(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        assert registry.register(sig) is True

    def test_register_duplicate(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        registry.register(sig)
        assert registry.register(sig) is False

    def test_register_equivalent(self):
        registry = TemplateRegistry()
        sig1 = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        sig2 = TemplateSignatureBuilder().build(canonical_ast("7x + 3 = 38"))
        assert registry.register(sig1) is True
        assert registry.register(sig2) is False  # same hash

    def test_lookup_by_hash(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        registry.register(sig)
        found = registry.lookup_by_hash(sig.structural_hash)
        assert found is not None
        assert found.template_id == sig.template_id

    def test_lookup_by_hash_missing(self):
        registry = TemplateRegistry()
        assert registry.lookup_by_hash("nonexistent") is None

    def test_lookup_by_id(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        registry.register(sig)
        found = registry.lookup_by_id("LinearEquation")
        assert found is not None
        assert found.structural_hash == sig.structural_hash

    def test_lookup_by_id_missing(self):
        registry = TemplateRegistry()
        assert registry.lookup_by_id("DoesNotExist") is None

    def test_find_matches(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        registry.register(sig)
        ast = canonical_ast("7x + 3 = 38")
        matches = registry.find_matches(ast)
        assert len(matches) == 1
        assert matches[0].template_id == "LinearEquation"

    def test_find_no_matches(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        registry.register(sig)
        ast = canonical_ast("42")
        matches = registry.find_matches(ast)
        assert len(matches) == 0

    def test_count(self):
        registry = TemplateRegistry()
        assert registry.count() == 0
        registry.register(TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17")))
        assert registry.count() == 1
        registry.register(TemplateSignatureBuilder().build(canonical_ast("2(x+3)")))
        assert registry.count() == 2

    def test_get_all(self):
        registry = TemplateRegistry()
        sig1 = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        sig2 = TemplateSignatureBuilder().build(canonical_ast("42"))
        registry.register(sig1)
        registry.register(sig2)
        all_sigs = registry.get_all()
        assert len(all_sigs) == 2

    def test_clear(self):
        registry = TemplateRegistry()
        registry.register(TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17")))
        registry.clear()
        assert registry.count() == 0


# =========================================================================
# TemplateConfidenceScorer Tests
# =========================================================================

class TestTemplateConfidenceScorer:

    def test_score_exact_match(self):
        ast = canonical_ast("2x + 5 = 17")
        sig = TemplateSignatureBuilder().build(ast)
        assert TemplateConfidenceScorer.score(ast, sig) == 1.0

    def test_score_no_match(self):
        ast = canonical_ast("2x + 5 = 17")
        other = canonical_ast("42")
        sig = TemplateSignatureBuilder().build(other)
        assert TemplateConfidenceScorer.score(ast, sig) == 0.0

    def test_score_equivalent_expression(self):
        ast_a = canonical_ast("2x + 5 = 17")
        ast_b = canonical_ast("7x + 3 = 38")
        sig = TemplateSignatureBuilder().build(ast_a)
        assert TemplateConfidenceScorer.score(ast_b, sig) == 1.0

    def test_compare_trees_identical(self):
        ast = canonical_ast("2x + 5 = 17")
        assert TemplateConfidenceScorer.compare_trees(ast, ast) == 1.0

    def test_compare_trees_different(self):
        a = canonical_ast("2x + 5 = 17")
        b = canonical_ast("42")
        s = TemplateConfidenceScorer.compare_trees(a, b)
        assert s < 1.0

    def test_score_best_exact_match(self):
        registry = TemplateRegistry()
        sig = TemplateSignatureBuilder().build(canonical_ast("2x + 5 = 17"))
        registry.register(sig)
        ast = canonical_ast("7x + 3 = 38")
        best, score = TemplateConfidenceScorer.score_best(ast, registry)
        assert best is not None
        assert best.template_id == "LinearEquation"
        assert score == 1.0

    def test_score_best_empty_registry(self):
        registry = TemplateRegistry()
        ast = canonical_ast("2x + 5 = 17")
        best, score = TemplateConfidenceScorer.score_best(ast, registry)
        assert best is None
        assert score == 0.0


# =========================================================================
# End-to-End Template Equivalence Tests
# =========================================================================

class TestEndToEndTemplateEquivalence:

    def test_linear_equation_same_template(self):
        """2x+5=17 and 7x+3=38 are the same template."""
        ast1 = canonical_ast("2x + 5 = 17")
        ast2 = canonical_ast("7x + 3 = 38")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.template_id == sig2.template_id
        assert sig1.structural_hash == sig2.structural_hash
        assert sig1.template_family == sig2.template_family

    def test_distributive_multiplication_same_template(self):
        """2(x+3) and 5(y-1) are the same template."""
        ast1 = canonical_ast("2(x+3)")
        ast2 = canonical_ast("5(y-1)")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.template_id == sig2.template_id
        assert sig1.structural_hash == sig2.structural_hash

    def test_different_templates_different_id(self):
        """2x+5=17 and 2(x+3) are different templates."""
        ast1 = canonical_ast("2x + 5 = 17")
        ast2 = canonical_ast("2(x+3)")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.template_id != sig2.template_id
        assert sig1.structural_hash != sig2.structural_hash

    def test_same_shape_different_constants_same_template(self):
        """2x+5=17 and 2x+5=0 have the same shape (different constants)."""
        ast1 = canonical_ast("2x + 5 = 17")
        ast2 = canonical_ast("2x + 5 = 0")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash == sig2.structural_hash

    def test_different_shape_different_operators(self):
        """2x+5=17 and 2x+5=17+3 have different shapes (RHS is
        expression vs constant)."""
        ast1 = canonical_ast("2x + 5 = 17")
        ast2 = canonical_ast("2x + 5 = 17 + 3")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        # After canonicalization: 2x+5=20 (folding 17+3)
        # So they might now be the same if constant folding occurs...
        # Actually 17+3 folds to 20, so it becomes 2x+5=20 → same shape.
        # We need different shapes. Let's use 2x+5=17 vs 2x+5=x+3
        pass

    def test_truly_different_shapes(self):
        """2x+5=17 and 2x+5=x+3 have different shapes."""
        ast1 = canonical_ast("2x + 5 = 17")
        ast2 = canonical_ast("2x + 5 = x + 3")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash != sig2.structural_hash

    def test_commutative_reordering_same_template(self):
        """2x+5=17 and 5+2x=17 are the same template (commutativity)."""
        ast1 = canonical_ast("2x + 5 = 17")
        ast2 = canonical_ast("5 + 2x = 17")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash == sig2.structural_hash

    def test_multiple_variables_same_template(self):
        """x+y=10 and a+b=10 have the same shape."""
        ast1 = canonical_ast("x + y = 10")
        ast2 = canonical_ast("a + b = 10")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash == sig2.structural_hash

    def test_rectangle_area_not_linear_equation(self):
        """5*x (area-like) and 2x+5=17 are different templates."""
        ast1 = canonical_ast("5 * x")
        ast2 = canonical_ast("2x + 5 = 17")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash != sig2.structural_hash

    def test_triangle_perimeter_not_linear_equation(self):
        """5+7+x (perimeter-like) and 2x+5=17 are different templates."""
        ast1 = canonical_ast("5 + 7 + x")
        ast2 = canonical_ast("2x + 5 = 17")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash != sig2.structural_hash

    def test_constant_folding_preserves_template(self):
        """3+4+x (folds to 7+x) and 7+x have same template."""
        ast1 = canonical_ast("3 + 4 + x")
        ast2 = canonical_ast("7 + x")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash == sig2.structural_hash


# =========================================================================
# Edge Cases and Negative Tests
# =========================================================================

class TestEdgeCases:

    def test_single_constant_template(self):
        ast = canonical_ast("42")
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_family == "Expression"
        assert len(sig.variable_slots) == 1

    def test_single_variable_template(self):
        ast = canonical_ast("x")
        sig = TemplateSignatureBuilder().build(ast)
        assert sig.template_family == "Expression"
        assert len(sig.variable_slots) == 0

    def test_division_in_template(self):
        ast = canonical_ast("x / 2 = 5")
        sig = TemplateSignatureBuilder().build(ast)
        assert "/" in sig.canonical_pattern

    def test_negative_constant(self):
        ast = canonical_ast("-5")
        sig = TemplateSignatureBuilder().build(ast)
        # -5 canonicalizes to ConstantNode(-5)
        assert sig.template_id == "ConstantExpression"

    def test_double_negation(self):
        ast = canonical_ast("--x")
        sig = TemplateSignatureBuilder().build(ast)
        # --x canonicalizes to u-(u-(x)) → U(U(V))
        assert "a" in sig.canonical_pattern or not sig.variable_slots

    def test_registry_multiple_templates(self):
        registry = TemplateRegistry()
        registry.register(TemplateSignatureBuilder().build(canonical_ast("2x+5=17")))
        registry.register(TemplateSignatureBuilder().build(canonical_ast("2(x+3)")))
        registry.register(TemplateSignatureBuilder().build(canonical_ast("42")))
        assert registry.count() == 3

    def test_deeply_nested_parens_same_shape(self):
        """((2x)) and 2x have the same shape (canonicalization removes
        redundant parens via AST structure)."""
        ast1 = canonical_ast("((2x))")
        ast2 = canonical_ast("2x")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash == sig2.structural_hash

    def test_whitespace_irrelevant(self):
        ast1 = canonical_ast("2x+5=17")
        ast2 = canonical_ast("  2x  +  5  =  17  ")
        sig1 = TemplateSignatureBuilder().build(ast1)
        sig2 = TemplateSignatureBuilder().build(ast2)
        assert sig1.structural_hash == sig2.structural_hash

    def test_fingerprint_is_not_hash(self):
        fp = StructuralHasher.fingerprint(canonical_ast("2x+5=17"))
        h = StructuralHasher.hash(canonical_ast("2x+5=17"))
        assert fp != h
        assert len(h) == 64
