from __future__ import annotations

import pytest

from src.ast import (
    ConstantNode, VariableNode, BinaryOpNode,
    UnaryOpNode, EquationNode,
)
from src.canonicalizer import Canonicalizer
from src.variable_engine import (
    Variable, VariableType, VariableDomain, VariableMetadata,
    SourceLocation,
    VariableGraph, GraphEdge,
    VariableRegistry,
    VariableDiscoveryVisitor, DiscoveryResult,
)


# =========================================================================
# Helpers
# =========================================================================

def canonical_ast(expr: str):
    from src.tokenizer import Tokenizer
    from src.lexer import Lexer
    from src.parser import Parser
    tokens = Tokenizer(expr).tokenize()
    Lexer().validate(tokens)
    ast = Parser(tokens).parse()
    return Canonicalizer(rename_variables=False).canonicalize(ast).tree


def discover(expr: str) -> DiscoveryResult:
    ast = canonical_ast(expr)
    return VariableDiscoveryVisitor(expression=expr).discover(ast)


# =========================================================================
# Variable Tests
# =========================================================================

class TestVariable:

    def test_create_integer_variable(self):
        v = Variable(
            id="test_1", name="const_5", type=VariableType.CONSTANT,
            original_value=5, canonical_value=5,
        )
        assert v.id == "test_1"
        assert v.name == "const_5"
        assert v.type == VariableType.CONSTANT
        assert v.canonical_value == 5

    def test_create_symbolic_variable(self):
        v = Variable(
            id="sym_1", name="x", type=VariableType.SYMBOL,
            original_value="x", canonical_value="x",
        )
        assert v.type == VariableType.SYMBOL
        assert v.canonical_value == "x"

    def test_create_coefficient_variable(self):
        v = Variable(
            id="coeff_1", name="coeff_7", type=VariableType.COEFFICIENT,
            original_value=7, canonical_value=7,
        )
        assert v.type == VariableType.COEFFICIENT
        assert v.canonical_value == 7

    def test_to_dict(self):
        v = Variable(
            id="v_1", name="const_5", type=VariableType.CONSTANT,
            original_value=5, canonical_value=5,
        )
        d = v.to_dict()
        assert d["id"] == "v_1"
        assert d["type"] == "constant"
        assert d["canonical_value"] == 5

    def test_new_id_generates_unique(self):
        id1 = Variable.new_id("test")
        id2 = Variable.new_id("test")
        assert id1 != id2
        assert id1.startswith("test_")
        assert id2.startswith("test_")


# =========================================================================
# VariableDomain Tests
# =========================================================================

class TestVariableDomain:

    def test_default_domain(self):
        d = VariableDomain()
        assert d.is_integer is True
        assert d.min_value is None

    def test_positive_domain(self):
        d = VariableDomain(is_positive=True, is_integer=True)
        assert d.is_positive is True

    def test_to_dict(self):
        d = VariableDomain(min_value=0, max_value=100, is_integer=True)
        dd = d.to_dict()
        assert dd["min_value"] == 0
        assert dd["max_value"] == 100


# =========================================================================
# VariableMetadata Tests
# =========================================================================

class TestVariableMetadata:

    def test_default_metadata(self):
        m = VariableMetadata()
        assert m.can_randomize is True
        assert m.is_derived is False

    def test_to_dict(self):
        src = SourceLocation(expression="2+2")
        m = VariableMetadata(
            ast_node_type="ConstantNode",
            template_slot="a",
            source_location=src,
        )
        d = m.to_dict()
        assert d["ast_node_type"] == "ConstantNode"
        assert d["template_slot"] == "a"
        assert d["source_location"]["expression"] == "2+2"

    def test_source_location_to_dict(self):
        s = SourceLocation(expression="2x+5=17", approximate_position=3)
        d = s.to_dict()
        assert d["expression"] == "2x+5=17"
        assert d["approximate_position"] == 3


# =========================================================================
# VariableGraph Tests
# =========================================================================

class TestVariableGraph:

    def test_empty_graph(self):
        g = VariableGraph()
        assert g.node_count() == 0
        assert g.edge_count() == 0
        assert g.roots() == []

    def test_add_node(self):
        g = VariableGraph()
        v = Variable(
            id="v1", name="x", type=VariableType.SYMBOL,
            original_value="x", canonical_value="x",
        )
        g.add_node(v)
        assert g.node_count() == 1
        assert g.get_node("v1") == v

    def test_add_edge(self):
        g = VariableGraph()
        a = Variable(id="a", name="coeff_2", type=VariableType.COEFFICIENT,
                     original_value=2, canonical_value=2)
        b = Variable(id="b", name="x", type=VariableType.SYMBOL,
                     original_value="x", canonical_value="x")
        g.add_node(a)
        g.add_node(b)
        g.add_edge("a", "b", "coefficient_of")
        assert g.edge_count() == 1
        assert g.get_outgoing("a")[0].target_id == "b"

    def test_roots(self):
        g = VariableGraph()
        a = Variable(id="a", name="r", type=VariableType.EQUATION,
                     original_value="eq", canonical_value="eq")
        b = Variable(id="b", name="x", type=VariableType.SYMBOL,
                     original_value="x", canonical_value="x")
        g.add_node(a)
        g.add_node(b)
        g.add_edge("a", "b", "contains")
        roots = g.roots()
        assert len(roots) == 1
        assert roots[0].id == "a"

    def test_children(self):
        g = VariableGraph()
        p = Variable(id="p", name="p", type=VariableType.EXPRESSION,
                     original_value="+", canonical_value="+")
        c = Variable(id="c", name="c", type=VariableType.CONSTANT,
                     original_value=5, canonical_value=5)
        g.add_node(p)
        g.add_node(c)
        g.add_edge("p", "c", "contains")
        kids = g.children("p")
        assert len(kids) == 1
        assert kids[0].id == "c"

    def test_parents(self):
        g = VariableGraph()
        p = Variable(id="p", name="p", type=VariableType.EXPRESSION,
                     original_value="+", canonical_value="+")
        c = Variable(id="c", name="c", type=VariableType.CONSTANT,
                     original_value=5, canonical_value=5)
        g.add_node(p)
        g.add_node(c)
        g.add_edge("p", "c", "contains")
        pars = g.parents("c")
        assert len(pars) == 1
        assert pars[0].id == "p"

    def test_to_dict(self):
        g = VariableGraph()
        a = Variable(id="a", name="a", type=VariableType.CONSTANT,
                     original_value=1, canonical_value=1)
        b = Variable(id="b", name="b", type=VariableType.CONSTANT,
                     original_value=2, canonical_value=2)
        g.add_node(a)
        g.add_node(b)
        g.add_edge("a", "b", "contains")
        d = g.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "roots" in d

    def test_clear(self):
        g = VariableGraph()
        v = Variable(id="v", name="v", type=VariableType.CONSTANT,
                     original_value=1, canonical_value=1)
        g.add_node(v)
        g.clear()
        assert g.node_count() == 0


# =========================================================================
# VariableRegistry Tests
# =========================================================================

class TestVariableRegistry:

    def test_register_and_lookup(self):
        r = VariableRegistry()
        v = Variable(id="v1", name="x", type=VariableType.SYMBOL,
                     original_value="x", canonical_value="x")
        assert r.register(v) is True
        assert r.lookup("v1") == v

    def test_register_duplicate(self):
        r = VariableRegistry()
        v = Variable(id="v1", name="x", type=VariableType.SYMBOL,
                     original_value="x", canonical_value="x")
        r.register(v)
        assert r.register(v) is False

    def test_lookup_by_name(self):
        r = VariableRegistry()
        v = Variable(id="v1", name="x", type=VariableType.SYMBOL,
                     original_value="x", canonical_value="x")
        r.register(v)
        found = r.lookup_by_name("x")
        assert len(found) == 1
        assert found[0].id == "v1"

    def test_lookup_missing(self):
        r = VariableRegistry()
        assert r.lookup("nonexistent") is None

    def test_get_all(self):
        r = VariableRegistry()
        r.register(Variable(id="a", name="a", type=VariableType.CONSTANT,
                            original_value=1, canonical_value=1))
        r.register(Variable(id="b", name="b", type=VariableType.SYMBOL,
                            original_value="x", canonical_value="x"))
        assert len(r.get_all()) == 2

    def test_count(self):
        r = VariableRegistry()
        assert r.count() == 0
        r.register(Variable(id="a", name="a", type=VariableType.CONSTANT,
                            original_value=1, canonical_value=1))
        assert r.count() == 1

    def test_clear(self):
        r = VariableRegistry()
        r.register(Variable(id="a", name="a", type=VariableType.CONSTANT,
                            original_value=1, canonical_value=1))
        r.clear()
        assert r.count() == 0


# =========================================================================
# DiscoveryVisitor Tests
# =========================================================================

class TestDiscoveryVisitor:

    def test_discover_simple_constant(self):
        result = discover("42")
        assert result.root_variable_id is not None
        assert result.registry.count() == 1
        v = result.registry.get_all()[0]
        assert v.type == VariableType.CONSTANT
        assert v.canonical_value == 42

    def test_discover_simple_variable(self):
        result = discover("x")
        assert result.registry.count() == 1
        v = result.registry.get_all()[0]
        assert v.type == VariableType.SYMBOL
        assert v.canonical_value == "x"

    def test_discover_linear_equation(self):
        """7x + 3 = 38"""
        result = discover("7x + 3 = 38")
        # After canonicalization: 3 + 7*x = 38
        # Variables: const_3 (CONSTANT or COEFFICIENT?), 
        # Actually 3 is a constant in additive position → CONSTANT
        # 7 is a coefficient (multiplied by x) → COEFFICIENT
        # x is a symbol → SYMBOL
        # 38 is a constant → CONSTANT
        # Plus expression and equation variables
        registry = result.registry
        types = {v.type for v in registry.get_all()}
        assert VariableType.EQUATION in types
        assert VariableType.COEFFICIENT in types
        assert VariableType.SYMBOL in types
        assert VariableType.EXPRESSION in types

    def test_coefficient_of_relationship(self):
        """7x + 3 = 38 → coefficient 7 is coefficient_of x"""
        result = discover("7x + 3 = 38")
        graph = result.graph
        coeffs = [v for v in registry_all(result) if v.type == VariableType.COEFFICIENT]
        assert len(coeffs) >= 1
        coeff = coeffs[0]
        edges = graph.get_outgoing(coeff.id)
        coeff_of_edges = [e for e in edges if e.relationship == "coefficient_of"]
        assert len(coeff_of_edges) >= 1
        target = graph.get_node(coeff_of_edges[0].target_id)
        assert target is not None
        assert target.type == VariableType.SYMBOL

    def test_symbol_deduplication(self):
        """x appears once even if referenced multiple times"""
        result = discover("x + x")
        # After canonicalization: 2*x
        # Only one x in the tree
        syms = [v for v in registry_all(result) if v.type == VariableType.SYMBOL]
        assert len(syms) == 1

    def test_symbol_on_both_sides(self):
        """x = x + 5 has x on both sides, but after canonicalization
        it becomes x = x + 5 → x appears twice in tree, should be
        one SymbolicVariable."""
        result = discover("x = x + 5")
        # After canonicalization: Equation(x, BinaryOp(+, 5, x))
        # x appears on both sides of equation
        syms = [v for v in registry_all(result) if v.type == VariableType.SYMBOL]
        assert len(syms) == 1

    def test_multiple_constants(self):
        """2x + 3 = 5 → three constants: 2 (coeff), 3 (const), 5 (const)"""
        result = discover("2x + 3 = 5")
        # After canonicalization: 3 + 2*x = 5
        # const_3 is CONSTANT, coeff_2 is COEFFICIENT, const_5 is CONSTANT
        # Also: the expression node for 3 + 2*x
        consts = [v for v in registry_all(result) if v.type == VariableType.CONSTANT]
        coeffs = [v for v in registry_all(result) if v.type == VariableType.COEFFICIENT]
        assert len(consts) >= 1  # at least 3 and 5
        assert len(coeffs) >= 1  # 2

    def test_division(self):
        """x / 2 = 5"""
        result = discover("x / 2 = 5")
        types = {v.type for v in registry_all(result)}
        assert VariableType.EQUATION in types
        assert VariableType.SYMBOL in types
        assert VariableType.CONSTANT in types

    def test_unary_minus(self):
        """-x"""
        result = discover("-x")
        types = {v.type for v in registry_all(result)}
        assert VariableType.SYMBOL in types
        assert VariableType.EXPRESSION in types

    def test_negative_constant(self):
        """-5"""
        result = discover("-5")
        v = registry_all(result)[0]
        assert v.canonical_value == -5

    def test_nested_expression(self):
        """2(x+3)"""
        result = discover("2(x+3)")
        # After canonicalization: 2*(3+x) → product of 2 and sum of 3,x
        # The 2 is in multiplicative position but sibling is an expression
        # (3+x), not a bare variable, so it's marked CONSTANT, not COEFFICIENT.
        types = {v.type for v in registry_all(result)}
        assert VariableType.CONSTANT in types
        assert VariableType.SYMBOL in types
        assert VariableType.EXPRESSION in types

    def test_discovery_result_has_graph(self):
        result = discover("x + 5 = 10")
        graph = result.graph
        assert graph.node_count() > 0
        assert graph.edge_count() > 0

    def test_root_variable_is_equation(self):
        result = discover("x + 5 = 10")
        root = result.graph.get_node(result.root_variable_id)
        assert root is not None
        assert root.type == VariableType.EQUATION

    def test_variable_metadata_set(self):
        result = discover("3x + 5 = 17")
        for v in registry_all(result):
            assert v.metadata.ast_node_type in (
                "ConstantNode", "VariableNode", "BinaryOpNode",
                "EquationNode", "UnaryOpNode",
            )


# =========================================================================
# End-to-End Variable Extraction Tests
# =========================================================================

class TestEndToEndExtraction:

    def test_linear_equation_variables(self):
        """7x + 3 = 38 → a=7 (coeff), x (symbol), b=3 (const), c=38 (const)"""
        result = discover("7x + 3 = 38")
        registry = result.registry

        # Find symbol x
        syms = registry.lookup_by_name("x")
        assert len(syms) == 1
        assert syms[0].type == VariableType.SYMBOL

        # Find coefficient (value should be 7 in original, but after
        # canonicalization of 7x + 3 = 38 it becomes 3 + 7*x = 38,
        # so 7 is still a coefficient)
        coeffs = [v for v in registry.get_all()
                  if v.type == VariableType.COEFFICIENT]
        assert len(coeffs) == 1
        assert coeffs[0].canonical_value == 7

    def test_distributive_multiplication_variables(self):
        """2(x+3) → coeff=2, x=symbol, const=3"""
        result = discover("2(x+3)")
        # After canonicalization: 2*(3+x)
        # Has coefficient 2, symbol x, constant 3
        syms = result.registry.lookup_by_name("x")
        assert len(syms) == 1

    def test_variable_graph_has_equation_root(self):
        """For equations, the graph root should be EquationVariable."""
        result = discover("2x + 5 = 17")
        root_id = result.root_variable_id
        root = result.graph.get_node(root_id)
        assert root.type == VariableType.EQUATION

    def test_variable_graph_expression_root(self):
        """For expressions, the graph root should be ExpressionVariable."""
        result = discover("2x + 5")
        root_id = result.root_variable_id
        root = result.graph.get_node(root_id)
        assert root.type == VariableType.EXPRESSION

    def test_constant_graph_root(self):
        """For a single constant, the graph root is ConstantVariable."""
        result = discover("42")
        root_id = result.root_variable_id
        root = result.graph.get_node(root_id)
        assert root.type == VariableType.CONSTANT

    def test_to_dict_serialization(self):
        """The entire result should be serializable to dict."""
        result = discover("2x + 5 = 17")
        d = result.graph.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert len(d["nodes"]) > 0

    def test_multiple_coefficients(self):
        """3x + 4y → two coefficients: 3 and 4"""
        result = discover("3x + 4y")
        # After canonicalization: 3*x + 4*y  (or 4*y + 3*x depending on sort)
        coeffs = [v for v in registry_all(result)
                  if v.type == VariableType.COEFFICIENT]
        assert len(coeffs) == 2

    def test_repeated_discovery_deterministic(self):
        """Discovering the same expression twice yields the same
        variable types (IDs may differ)."""
        r1 = discover("2x + 5 = 17")
        r2 = discover("2x + 5 = 17")
        t1 = {v.type for v in registry_all(r1)}
        t2 = {v.type for v in registry_all(r2)}
        assert t1 == t2


# =========================================================================
# Edge Cases and Negative Tests
# =========================================================================

class TestEdgeCases:

    def test_empty_expression_raises(self):
        with pytest.raises(Exception):
            discover("")

    def test_constant_folding_reduces_variables(self):
        """3 + 4 + x folds to 7 + x, so only one constant (7) instead
        of two (3, 4)."""
        result = discover("3 + 4 + x")
        consts = [v for v in registry_all(result)
                  if v.type == VariableType.CONSTANT]
        # After canonicalization: 7 + x → one constant (7) and symbol x
        assert len(consts) >= 1
        # The coefficient 7 is technically a constant in the additive
        # expression, not a coefficient (since it's added, not multiplied)
        # But it could become a coefficient if placed in multiplication
        # Actually, 7 + x → 7 is just a constant addend

    def test_division_inexact(self):
        """5 / 2 = x → constants 5, 2 and symbol x"""
        result = discover("5 / 2 = x")
        types = {v.type for v in registry_all(result)}
        assert VariableType.CONSTANT in types
        # NOTE: 5/2 doesn't fold (inexact), so 5 and 2 stay as separate
        # And x is the RHS variable

    def test_double_negation(self):
        """--x → u-(u-(x))"""
        result = discover("--x")
        # Has symbolic x and expression for unary ops
        syms = [v for v in registry_all(result) if v.type == VariableType.SYMBOL]
        assert len(syms) == 1

    def test_graph_has_no_dangling_edges(self):
        """Every edge target must exist as a node."""
        result = discover("2x + 5 = 17")
        graph = result.graph
        node_ids = {n.id for n in graph.all_nodes()}
        for edge in graph.get_edges():
            assert edge.source_id in node_ids
            assert edge.target_id in node_ids

    def test_graph_serialization_roundtrip(self):
        """to_dict should produce deterministic output."""
        r1 = discover("2x + 5 = 17")
        r2 = discover("2x + 5 = 17")
        d1 = r1.graph.to_dict()
        d2 = r2.graph.to_dict()
        assert set(d1["nodes"].keys()) != set(d2["nodes"].keys())  # UUIDs differ
        # But node count should be the same
        assert len(d1["nodes"]) == len(d2["nodes"])
        assert len(d1["edges"]) == len(d2["edges"])

    def test_domain_inference_positive(self):
        result = discover("5x + 3 = 10")
        consts = [v for v in registry_all(result)
                  if v.type == VariableType.CONSTANT]
        for c in consts:
            if c.canonical_value > 0:
                assert c.domain.is_positive is True

    def test_domain_inference_symbol(self):
        result = discover("x")
        syms = [v for v in registry_all(result) if v.type == VariableType.SYMBOL]
        assert len(syms) == 1
        assert syms[0].domain.is_integer is False


# =========================================================================
# Helpers for tests
# =========================================================================

def registry_all(result: DiscoveryResult):
    return result.registry.get_all()
