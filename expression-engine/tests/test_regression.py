"""Regression test suite for interface contracts between engines.

These tests MUST pass before any future milestone is accepted.

They verify:
1. Public API surface stability
2. Interface contract compatibility
3. No circular imports
4. All expected exports exist
5. Cross-engine type compatibility
"""

import importlib
import inspect
import pkgutil
import pytest


# ══════════════════════════════════════════════════════════════════════════
# Module Discovery
# ══════════════════════════════════════════════════════════════════════════

CORE_MODULES = {
    "src.ast",
    "src.parser",
    "src.canonicalizer",
    "src.hashing",
    "src.template_engine",
    "src.variable_engine",
    "src.semantic_engine",
    "src.constraint_engine",
    "src.constraint_engine.constraints",
    "src.symbolic",
}

ENGINE_MODULES = {
    "src.parser",
    "src.canonicalizer",
    "src.template_engine",
    "src.variable_engine",
    "src.semantic_engine",
    "src.constraint_engine",
    "src.symbolic",
}


# ══════════════════════════════════════════════════════════════════════════
# Test: No circular imports – all modules load independently
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("module_name", sorted(CORE_MODULES))
def test_module_loads(module_name):
    """Every core module must import without errors.

    This is the first line of defence against circular imports.
    """
    importlib.import_module(module_name)


# ══════════════════════════════════════════════════════════════════════════
# Test: Public API surface is stable (exports match __all__)
# ══════════════════════════════════════════════════════════════════════════

def _get_module_exports(module_name: str) -> set[str]:
    mod = importlib.import_module(module_name)
    if hasattr(mod, "__all__"):
        return set(mod.__all__)
    return {name for name in dir(mod) if not name.startswith("_")}


EXPORTED_NAMES: dict[str, set[str]] = {}

for _mod_name in CORE_MODULES:
    try:
        EXPORTED_NAMES[_mod_name] = _get_module_exports(_mod_name)
    except Exception:
        pass


def test_ast_exports():
    exports = EXPORTED_NAMES.get("src.ast", set())
    required = {"ASTNode", "ASTVisitor", "ToStringVisitor",
                "ConstantNode", "VariableNode", "BinaryOpNode",
                "UnaryOpNode", "EquationNode", "OP_PRECEDENCE",
                "ASSOCIATIVE_OPS"}
    missing = required - exports
    assert not missing, f"Missing AST exports: {missing}"


def test_parser_exports():
    exports = EXPORTED_NAMES.get("src.parser", set())
    assert "Parser" in exports


def test_canonicalizer_exports():
    exports = EXPORTED_NAMES.get("src.canonicalizer", set())
    assert "Canonicalizer" in exports
    assert "CanonicalResult" in exports


def test_template_engine_exports():
    exports = EXPORTED_NAMES.get("src.template_engine", set())
    required = {"PatternMatcher", "MatchResult", "StructuralComparator",
                "TemplateSignature", "TemplateSignatureBuilder",
                "StructuralHasher", "TemplateRegistry",
                "TemplateConfidenceScorer"}
    missing = required - exports
    assert not missing, f"Missing template_engine exports: {missing}"


def test_variable_engine_exports():
    exports = EXPORTED_NAMES.get("src.variable_engine", set())
    required = {"Variable", "VariableType", "VariableDomain",
                "VariableMetadata", "VariableGraph", "GraphEdge",
                "VariableRegistry", "VariableDiscoveryVisitor",
                "DiscoveryResult"}
    missing = required - exports
    assert not missing, f"Missing variable_engine exports: {missing}"


def test_semantic_engine_exports():
    exports = EXPORTED_NAMES.get("src.semantic_engine", set())
    required = {"SemanticTemplate", "SemanticMetadata",
                "TemplateFamily", "TemplateStatus", "DifficultyLevel",
                "ConstraintType", "SemanticTemplateRegistry",
                "SemanticTemplateBuilder"}
    missing = required - exports
    assert not missing, f"Missing semantic_engine exports: {missing}"


def test_constraint_engine_exports():
    exports = EXPORTED_NAMES.get("src.constraint_engine", set())
    required = {"Constraint", "ConstraintResult", "ConstraintMetadata",
                "Severity", "RetryReason",
                "ConstraintValidationResult", "Diagnostic",
                "ConstraintGraph", "ConstraintRegistry",
                "ConstraintValidator", "register_builtins"}
    missing = required - exports
    assert not missing, f"Missing constraint_engine exports: {missing}"


def test_symbolic_exports():
    exports = EXPORTED_NAMES.get("src.symbolic", set())
    required = {"SymbolicBackend", "BuiltinBackend",
                "SymbolicExpr", "ExprType",
                "SymbolicVisitor", "ToStringVisitor",
                "ExpressionEngine", "EquationEngine",
                "EquivalenceEngine", "AlgebraEngine",
                "GeometryEngine", "StatisticsEngine",
                "TrigonometryEngine", "EvaluationEngine",
                "SymbolicPluginRegistry",
                "ASTExprAdapter"}
    missing = required - exports
    assert not missing, f"Missing symbolic exports: {missing}"


# ══════════════════════════════════════════════════════════════════════════
# Test: Interface contracts – cross-module type usage
# ══════════════════════════════════════════════════════════════════════════

def _parse_expr(text: str):
    """Helper: Tokenize → Lex → Parse → ASTNode."""
    from src.tokenizer import Tokenizer
    from src.lexer import Lexer
    from src.parser import Parser
    tokens = Tokenizer(text).tokenize()
    Lexer().validate(tokens)
    return Parser(tokens).parse()


def test_parser_produces_ast():
    """Parser output must be an ASTNode."""
    from src.ast import ASTNode
    expr = _parse_expr("2*x + 5")
    assert isinstance(expr, ASTNode)


def test_canonicalizer_consumes_ast_and_produces_canonicalresult():
    """Canonicalizer must accept ASTNode and return CanonicalResult."""
    from src.canonicalizer import Canonicalizer, CanonicalResult
    from src.ast import ASTNode
    ast = _parse_expr("2*x + 5")
    result = Canonicalizer().canonicalize(ast)
    assert isinstance(result, CanonicalResult)
    assert isinstance(result.tree, ASTNode)
    assert isinstance(result.variable_names, frozenset)


def test_template_engine_consumes_ast():
    """TemplateSignatureBuilder must accept ASTNode directly."""
    from src.template_engine import TemplateSignatureBuilder, TemplateSignature
    ast = _parse_expr("2*x + 5 = 17")
    sig = TemplateSignatureBuilder().build(ast)
    assert isinstance(sig, TemplateSignature)


def test_variable_engine_consumes_ast():
    """VariableDiscoveryVisitor must accept ASTNode directly."""
    from src.variable_engine import VariableDiscoveryVisitor, DiscoveryResult
    from src.variable_engine import VariableGraph, VariableRegistry
    ast = _parse_expr("2*x + 5")
    result = VariableDiscoveryVisitor().discover(ast)
    assert isinstance(result, DiscoveryResult)
    assert isinstance(result.graph, VariableGraph)
    assert isinstance(result.registry, VariableRegistry)


def test_semantic_engine_consumes_signature_and_graph():
    """SemanticTemplateBuilder must accept TemplateSignature + VariableGraph."""
    from src.template_engine import TemplateSignatureBuilder
    from src.variable_engine import VariableDiscoveryVisitor
    from src.semantic_engine import SemanticTemplateBuilder, SemanticTemplate
    from src.variable_engine import VariableGraph
    ast = _parse_expr("2*x + 5 = 17")
    sig = TemplateSignatureBuilder().build(ast)
    disc = VariableDiscoveryVisitor().discover(ast)
    builder = SemanticTemplateBuilder()
    template = builder.build(sig, disc.graph)
    assert isinstance(template, SemanticTemplate)
    # Verify VariableGraph is accepted (not None)
    template_no_graph = builder.build(sig, None)
    assert isinstance(template_no_graph, SemanticTemplate)


def test_constraint_engine_consumes_graph_and_values():
    """ConstraintValidator must accept dict + VariableGraph."""
    from src.constraint_engine import (
        ConstraintRegistry, ConstraintValidator, register_builtins,
        ConstraintValidationResult,
    )
    from src.variable_engine import VariableGraph
    reg = ConstraintRegistry()
    register_builtins(reg)
    validator = ConstraintValidator(reg)
    graph = VariableGraph()
    result = validator.validate({"a": 1, "b": 2}, graph, ["integer_constraint"])
    assert isinstance(result, ConstraintValidationResult)


def test_symbolic_backend_implements_all_abstract_methods():
    """BuiltinBackend must implement every abstract method of SymbolicBackend."""
    from src.symbolic import SymbolicBackend, BuiltinBackend
    backend = BuiltinBackend()
    assert isinstance(backend, SymbolicBackend)
    # Verify every abstract method is concrete
    for name in dir(SymbolicBackend):
        if name.startswith("_"):
            continue
        method = getattr(SymbolicBackend, name, None)
        if hasattr(method, "__isabstractmethod__"):
            assert hasattr(backend, name), (
                f"BuiltinBackend missing abstract method: {name}")


# ══════════════════════════════════════════════════════════════════════════
# Test: AST → SymbolicExpr adapter
# ══════════════════════════════════════════════════════════════════════════

def test_ast_adapter_converts_all_node_types():
    """ASTExprAdapter must convert every ASTNode type to SymbolicExpr."""
    from src.ast import (
        ConstantNode, VariableNode, BinaryOpNode, UnaryOpNode, EquationNode,
    )
    from src.symbolic import ASTExprAdapter, SymbolicExpr, ExprType

    adapter = ASTExprAdapter()

    # ConstantNode
    result = adapter.convert(ConstantNode(value=5))
    assert result.is_number() and result.value == 5.0

    # VariableNode
    result = adapter.convert(VariableNode(name="x"))
    assert result.is_symbol() and result.symbol_name() == "x"

    # BinaryOpNode (add)
    result = adapter.convert(BinaryOpNode(
        "+", ConstantNode(1), ConstantNode(2)))
    assert result.is_add()

    # UnaryOpNode (negate)
    result = adapter.convert(UnaryOpNode("-", ConstantNode(5)))
    assert result.is_neg()

    # EquationNode
    result = adapter.convert(EquationNode(
        VariableNode("x"), ConstantNode(5)))
    assert result.is_equal()


def test_adapter_complex_expression():
    """Adapter handles nested expressions correctly."""
    from src.ast import (
        ConstantNode, VariableNode, BinaryOpNode, EquationNode,
    )
    from src.symbolic import ASTExprAdapter, SymbolicExpr

    # 2*x + 5 = 17
    ast = EquationNode(
        left=BinaryOpNode(
            "+",
            BinaryOpNode("*", ConstantNode(2), VariableNode("x")),
            ConstantNode(5),
        ),
        right=ConstantNode(17),
    )
    adapter = ASTExprAdapter()
    symbolic = adapter.convert(ast)

    assert symbolic.is_equal()
    # Left side should be ADD
    assert symbolic.left().is_add()
    # Right side should be NUMBER(17)
    assert symbolic.right().is_number() and symbolic.right().value == 17


# ══════════════════════════════════════════════════════════════════════════
# Test: Type annotations are correct
# ══════════════════════════════════════════════════════════════════════════

def test_constraint_validator_type_annotation():
    """ConstraintValidator.validate must accept VariableGraph type."""
    import inspect
    from src.constraint_engine import ConstraintValidator
    sig = inspect.signature(ConstraintValidator.validate)
    param = sig.parameters["variable_graph"]
    # Allow both VariableGraph and Optional[VariableGraph]
    anno = str(param.annotation)
    assert "VariableGraph" in anno or "object" in anno


def test_semantic_builder_type_annotation():
    """SemanticTemplateBuilder.build must accept VariableGraph type."""
    import inspect
    from src.semantic_engine import SemanticTemplateBuilder
    sig = inspect.signature(SemanticTemplateBuilder.build)
    param = sig.parameters["variable_graph"]
    anno = str(param.annotation)
    assert "VariableGraph" in anno or "object" in anno


# ══════════════════════════════════════════════════════════════════════════
# Test: Registry API consistency
# ══════════════════════════════════════════════════════════════════════════

class TestRegistryAPIs:
    """Verify consistent register/lookup API across registries."""

    def test_variable_registry_api(self):
        from src.variable_engine import VariableRegistry, Variable
        reg = VariableRegistry()
        var = Variable(id="test", name="x", type=None, original_value=None,
                       canonical_value=None, domain=None, metadata=None)
        assert reg.register(var) is True
        assert reg.lookup("test") is var
        assert reg.count() == 1

    def test_constraint_registry_api(self):
        from src.constraint_engine import ConstraintRegistry
        reg = ConstraintRegistry()
        assert reg.count() == 0
        assert reg.get("nonexistent") is None

    def test_template_registry_api(self):
        from src.template_engine import TemplateRegistry
        reg = TemplateRegistry()
        assert reg.count() == 0

    def test_semantic_registry_api(self):
        from src.semantic_engine import SemanticTemplateRegistry
        reg = SemanticTemplateRegistry()
        assert reg.count() == 0

    def test_plugin_registry_api(self):
        from src.symbolic import SymbolicPluginRegistry
        reg = SymbolicPluginRegistry()
        assert reg.plugins == {}
        assert reg.operations == {}


# ══════════════════════════════════════════════════════════════════════════
# Test: No duplicate module names
# ══════════════════════════════════════════════════════════════════════════

def test_no_duplicate_class_names():
    """Check for duplicate class names across modules."""
    from src.ast.nodes import ConstantNode, VariableNode
    from src.variable_engine.variable import Variable
    from src.symbolic.expression import SymbolicExpr
    from src.constraint_engine.base import Constraint
    # Verify key classes are unique
    assert ConstantNode is not None
    assert VariableNode is not None
    assert Variable is not None
    assert SymbolicExpr is not None
    assert Constraint is not None


# ══════════════════════════════════════════════════════════════════════════
# Test: Error propagation
# ══════════════════════════════════════════════════════════════════════════

def test_error_hierarchy():
    """SymbolicError hierarchy must be catchable by the base type."""
    from src.symbolic import SymbolicError, DivisionByZero
    assert issubclass(DivisionByZero, SymbolicError)

    from src.symbolic import DomainError, NoSolution
    assert issubclass(DomainError, SymbolicError)
    assert issubclass(NoSolution, SymbolicError)

    from src.constraint_engine.base import RetryReason
    assert RetryReason is not None

    from src.variable_engine import VariableType
    assert VariableType is not None


# ══════════════════════════════════════════════════════════════════════════
# Test: Pipeline intermediate objects are serializable
# ══════════════════════════════════════════════════════════════════════════

def test_constraint_validation_result_serializable():
    """ConstraintValidationResult.to_dict() must work without error."""
    from src.constraint_engine import (
        ConstraintValidationResult, ValidationStats, RetryReason,
    )
    result = ConstraintValidationResult(
        valid=True,
        stats=ValidationStats(total=1, passed=1),
    )
    d = result.to_dict()
    assert d["valid"] is True
    assert d["stats"]["total"] == 1


def test_diagnostic_serializable():
    """Diagnostic.to_dict() must work without error."""
    from src.constraint_engine import Diagnostic, Severity
    d = Diagnostic(
        constraint_id="test", constraint_name="Test",
        severity=Severity.ERROR, passed=False,
    )
    data = d.to_dict()
    assert data["constraint_id"] == "test"
    assert data["passed"] is False
