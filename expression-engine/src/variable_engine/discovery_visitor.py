from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from src.ast import (
    ASTNode, ASTVisitor, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
)
from .variable import (
    Variable, VariableType, VariableDomain, VariableMetadata,
    SourceLocation,
)
from .variable_graph import VariableGraph
from .variable_registry import VariableRegistry


@dataclass
class DiscoveryResult:
    """Result of running the discovery visitor over an AST.

    Attributes:
        registry: Populated ``VariableRegistry``.
        graph: Populated ``VariableGraph``.
        root_variable_id: The ID of the top-level variable (e.g. the
            ``EquationVariable`` for an equation).
    """
    registry: VariableRegistry = field(default_factory=VariableRegistry)
    graph: VariableGraph = field(default_factory=VariableGraph)
    root_variable_id: Optional[str] = None


class VariableDiscoveryVisitor(ASTVisitor):
    """Walks a canonical AST and produces a ``DiscoveryResult``.

    Every AST node is mapped to one or more ``Variable`` instances and
    recorded in a ``VariableGraph`` with labelled relationships.

    Usage::

        visitor = VariableDiscoveryVisitor()
        result = visitor.discover(canonical_ast)
        for v in result.registry.get_all():
            print(v.name, v.type, v.canonical_value)
    """

    def __init__(self, expression: str = "") -> None:
        self._expression: str = expression
        self._registry: VariableRegistry = VariableRegistry()
        self._graph: VariableGraph = VariableGraph()

    def discover(self, node: ASTNode) -> DiscoveryResult:
        self._registry = VariableRegistry()
        self._graph = VariableGraph()
        root_id = node.accept(self)
        return DiscoveryResult(
            registry=self._registry,
            graph=self._graph,
            root_variable_id=root_id,
        )

    # ------------------------------------------------------------------
    # Per-node-type visitors
    # ------------------------------------------------------------------

    def visit_constant(
        self, node: ConstantNode, **kwargs: Any,
    ) -> str:
        parent_op: Optional[str] = kwargs.get("parent_op")
        sibling_is_var: bool = kwargs.get("sibling_is_var", False)

        if parent_op == "*" and sibling_is_var:
            var = self._build_variable(
                node=node,
                type_=VariableType.COEFFICIENT,
                value=node.value,
                ast_type="ConstantNode",
            )
        else:
            var = self._build_variable(
                node=node,
                type_=VariableType.CONSTANT,
                value=node.value,
                ast_type="ConstantNode",
            )
        self._register(var)
        return var.id

    def visit_variable(
        self, node: VariableNode, **kwargs: Any,
    ) -> str:
        existing = self._registry.lookup_by_name(node.name)
        for v in existing:
            if v.type == VariableType.SYMBOL:
                return v.id

        var = self._build_variable(
            node=node,
            type_=VariableType.SYMBOL,
            value=node.name,
            ast_type="VariableNode",
        )
        self._register(var)
        return var.id

    def visit_binary_op(
        self, node: BinaryOpNode, **kwargs: Any,
    ) -> str:
        if node.operator == "*":
            return self._handle_multiplication(node)
        if node.operator in ("+", "-"):
            return self._handle_additive(node)
        if node.operator == "/":
            return self._handle_division(node)
        return self._handle_generic_binary(node)

    def visit_unary_op(
        self, node: UnaryOpNode, **kwargs: Any,
    ) -> str:
        operand_id = node.operand.accept(self)
        var = self._build_variable(
            node=node,
            type_=VariableType.EXPRESSION,
            value=f"{node.operator}(...)",
            ast_type="UnaryOpNode",
        )
        self._register(var)
        self._graph.add_edge(var.id, operand_id, "contains")
        return var.id

    def visit_equation(
        self, node: EquationNode, **kwargs: Any,
    ) -> str:
        left_id = node.left.accept(self)
        right_id = node.right.accept(self)

        var = self._build_variable(
            node=node,
            type_=VariableType.EQUATION,
            value="equation",
            ast_type="EquationNode",
        )
        self._register(var)
        self._graph.add_edge(var.id, left_id, "left_side")
        self._graph.add_edge(var.id, right_id, "right_side")
        return var.id

    # ------------------------------------------------------------------
    # Handlers for specific binary-op patterns
    # ------------------------------------------------------------------

    def _handle_multiplication(self, node: BinaryOpNode) -> str:
        left, right = node.left, node.right
        left_is_const = isinstance(left, ConstantNode)
        right_is_const = isinstance(right, ConstantNode)
        left_is_var = isinstance(left, VariableNode)
        right_is_var = isinstance(right, VariableNode)

        # Coefficient * Variable  (or  Variable * Coefficient)
        if (left_is_const and right_is_var) or (left_is_var and right_is_const):
            const_node = left if left_is_const else right
            var_node = right if left_is_const else left

            coeff_id = const_node.accept(
                self, parent_op="*", sibling_is_var=True,
            )
            sym_id = var_node.accept(self)

            self._graph.add_edge(coeff_id, sym_id, "coefficient_of")

            expr_var = self._build_variable(
                node=node,
                type_=VariableType.EXPRESSION,
                value="product",
                ast_type="BinaryOpNode",
            )
            self._register(expr_var)
            self._graph.add_edge(expr_var.id, coeff_id, "contains")
            self._graph.add_edge(expr_var.id, sym_id, "contains")
            return expr_var.id

        # General multiplication — visit children normally
        left_id = left.accept(self)
        right_id = right.accept(self)
        expr_var = self._build_variable(
            node=node,
            type_=VariableType.EXPRESSION,
            value="product",
            ast_type="BinaryOpNode",
        )
        self._register(expr_var)
        self._graph.add_edge(expr_var.id, left_id, "contains")
        self._graph.add_edge(expr_var.id, right_id, "contains")
        return expr_var.id

    def _handle_additive(self, node: BinaryOpNode) -> str:
        left_id = node.left.accept(self)
        right_id = node.right.accept(self)

        expr_var = self._build_variable(
            node=node,
            type_=VariableType.EXPRESSION,
            value=node.operator,
            ast_type="BinaryOpNode",
        )
        self._register(expr_var)
        self._graph.add_edge(expr_var.id, left_id, "contains")
        self._graph.add_edge(expr_var.id, right_id, "contains")
        return expr_var.id

    def _handle_division(self, node: BinaryOpNode) -> str:
        left_id = node.left.accept(self)
        right_id = node.right.accept(self)

        expr_var = self._build_variable(
            node=node,
            type_=VariableType.EXPRESSION,
            value="quotient",
            ast_type="BinaryOpNode",
        )
        self._register(expr_var)
        self._graph.add_edge(expr_var.id, left_id, "contains")
        self._graph.add_edge(expr_var.id, right_id, "contains")
        return expr_var.id

    def _handle_generic_binary(self, node: BinaryOpNode) -> str:
        left_id = node.left.accept(self)
        right_id = node.right.accept(self)

        expr_var = self._build_variable(
            node=node,
            type_=VariableType.EXPRESSION,
            value=node.operator,
            ast_type="BinaryOpNode",
        )
        self._register(expr_var)
        self._graph.add_edge(expr_var.id, left_id, "contains")
        self._graph.add_edge(expr_var.id, right_id, "contains")
        return expr_var.id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_variable(
        self,
        node: ASTNode,
        type_: VariableType,
        value: Any,
        ast_type: str,
    ) -> Variable:
        prefix = type_.value
        var_id = Variable.new_id(prefix)
        name = self._default_name(type_, value)

        domain = self._infer_domain(type_, value)

        metadata = VariableMetadata(
            ast_node_type=ast_type,
            can_randomize=(type_ in (
                VariableType.CONSTANT,
                VariableType.COEFFICIENT,
                VariableType.INTEGER,
            )),
            is_derived=(type_ in (
                VariableType.EXPRESSION,
                VariableType.EQUATION,
            )),
            is_user_visible=(type_ != VariableType.EXPRESSION),
            participates_in_constraints=(type_ not in (
                VariableType.EXPRESSION,
            )),
            source_location=SourceLocation(
                expression=self._expression,
            ),
        )

        return Variable(
            id=var_id,
            name=name,
            type=type_,
            original_value=value,
            canonical_value=value,
            domain=domain,
            metadata=metadata,
        )

    def _register(self, var: Variable) -> None:
        self._registry.register(var)
        self._graph.add_node(var)

    @staticmethod
    def _default_name(type_: VariableType, value: Any) -> str:
        mapping = {
            VariableType.CONSTANT: lambda v: f"const_{v}",
            VariableType.COEFFICIENT: lambda v: f"coeff_{v}",
            VariableType.SYMBOL: lambda v: str(v),
            VariableType.EXPRESSION: lambda v: f"expr_{v}",
            VariableType.EQUATION: lambda v: "equation",
            VariableType.INTEGER: lambda v: f"int_{v}",
        }
        handler = mapping.get(type_, lambda v: f"{type_.value}_{v}")
        return handler(value)

    @staticmethod
    def _infer_domain(type_: VariableType, value: Any) -> VariableDomain:
        if type_ in (VariableType.CONSTANT, VariableType.COEFFICIENT):
            return VariableDomain(
                is_integer=isinstance(value, int),
                is_positive=isinstance(value, (int, float)) and value > 0,
                is_negative=isinstance(value, (int, float)) and value < 0,
            )
        if type_ == VariableType.SYMBOL:
            return VariableDomain(is_integer=False)
        return VariableDomain()
