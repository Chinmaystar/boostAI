from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.ast import (
    ASTNode, ASTVisitor, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
    OP_PRECEDENCE,
)
from src.ast.nodes import ASSOCIATIVE_OPS


@dataclass
class CanonicalResult:
    """Result of canonicalization containing the canonical tree and
    the set of original variable names encountered during the pass."""

    tree: ASTNode
    variable_names: frozenset[str]


class VariableCollector(ASTVisitor):
    """Collects all distinct variable names from an AST."""

    def __init__(self) -> None:
        self._variables: set[str] = set()

    def collect(self, node: ASTNode) -> frozenset[str]:
        self._variables = set()
        node.accept(self)
        return frozenset(self._variables)

    def visit_constant(self, node: ConstantNode, **kwargs: Any) -> None:
        pass

    def visit_variable(self, node: VariableNode, **kwargs: Any) -> None:
        self._variables.add(node.name)

    def visit_binary_op(self, node: BinaryOpNode, **kwargs: Any) -> None:
        node.left.accept(self)
        node.right.accept(self)

    def visit_unary_op(self, node: UnaryOpNode, **kwargs: Any) -> None:
        node.operand.accept(self)

    def visit_equation(self, node: EquationNode, **kwargs: Any) -> None:
        node.left.accept(self)
        node.right.accept(self)


class CanonicalizingVisitor(ASTVisitor):
    """Transforms an AST into its canonical form.

    Canonicalization rules applied in order within each node visit:

    1. **Commutative sorting**: for ``+`` and ``*``, the standard form
       orders constants first, then variables alphabetically, then
       sub-expressions by their canonical string.

    2. **Constant folding**: evaluates constant sub-expressions at
       compile time (e.g. ``2 + 3`` → ``5``).

    3. **Redundant-parenthesis removal**: handled naturally by the AST
       structure; no extra ``(`` / ``)`` nodes exist.

    4. **Multiplication ordering**: the left operand of an implicit or
       explicit multiplication is always a constant when one is present.

    The visitor **does not** rename variables — that is a separate
    transformation intended for template matching (see
    ``VariableRenamingVisitor``).
    """

    def canonicalize(self, node: ASTNode) -> CanonicalResult:
        tree = node.accept(self)
        var_collector = VariableCollector()
        var_names = var_collector.collect(tree)
        return CanonicalResult(tree=tree, variable_names=var_names)

    def visit_constant(self, node: ConstantNode, **kwargs: Any) -> ConstantNode:
        return ConstantNode(node.value)

    def visit_variable(self, node: VariableNode, **kwargs: Any) -> VariableNode:
        return VariableNode(node.name)

    def visit_binary_op(self, node: BinaryOpNode, **kwargs: Any) -> ASTNode:
        left = node.left.accept(self)
        right = node.right.accept(self)
        op = node.operator

        if op in ASSOCIATIVE_OPS:
            return self._canonicalize_commutative(op, left, right)
        if op in ("-", "/"):
            return self._canonicalize_non_commutative(op, left, right)
        return BinaryOpNode(op, left, right)

    def visit_unary_op(self, node: UnaryOpNode, **kwargs: Any) -> ASTNode:
        operand = node.operand.accept(self)
        if isinstance(operand, ConstantNode) and node.operator == "-":
            return ConstantNode(-operand.value)
        return UnaryOpNode(node.operator, operand)

    def visit_equation(self, node: EquationNode, **kwargs: Any) -> EquationNode:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return EquationNode(left, right)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _canonicalize_commutative(
        self, op: str, left: ASTNode, right: ASTNode,
    ) -> ASTNode:
        """Flatten, sort, fold constants, and rebuild an associative
        commutative operator node."""
        terms = list(self._gather_terms(op, left, right))
        folded = self._fold_constants(op, terms)
        sorted_terms = sorted(folded, key=self._term_sort_key)
        return self._rebuild_left_associative(op, sorted_terms)

    def _canonicalize_non_commutative(
        self, op: str, left: ASTNode, right: ASTNode,
    ) -> ASTNode:
        """Canonicalize a non-commutative binary operation.
        Tries constant folding; otherwise returns the canonicalized
        children wrapped in the same operator."""
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            folded = self._try_fold_constants(op, left.value, right.value)
            if folded is not None:
                return ConstantNode(folded)
        return BinaryOpNode(op, left, right)

    def _gather_terms(
        self, op: str, left: ASTNode, right: ASTNode,
    ) -> list[ASTNode]:
        """Recursively flatten a left-associative tree of the same
        operator into a list of terms."""
        terms: list[ASTNode] = []

        def walk(node: ASTNode) -> None:
            if isinstance(node, BinaryOpNode) and node.operator == op:
                walk(node.left)
                walk(node.right)
            else:
                terms.append(node)

        walk(BinaryOpNode(op, left, right))
        return terms

    def _fold_constants(self, op: str, terms: list[ASTNode]) -> list[ASTNode]:
        """Extract constant terms, fold them into a single constant,
        and return a new list with the folded constant included."""
        const_indices = [
            i for i, t in enumerate(terms)
            if isinstance(t, ConstantNode)
        ]
        if len(const_indices) < 2:
            return terms

        const_values = [terms[i].value for i in const_indices]
        result = const_values[0]
        for v in const_values[1:]:
            folded = self._try_fold_constants(op, result, v)
            if folded is None:
                return terms
            result = folded

        new_terms = [
            t for i, t in enumerate(terms) if i not in const_indices
        ]
        new_terms.append(ConstantNode(result))
        return new_terms

    def _try_fold_constants(
        self, op: str, a: int, b: int,
    ) -> Optional[int]:
        if op == "+":
            return a + b
        if op == "*":
            return a * b
        if op == "-":
            return a - b
        if op == "/":
            if b == 0:
                return None
            if a % b != 0:
                return None
            return a // b
        return None

    def _term_sort_key(self, node: ASTNode) -> tuple:
        """Recursive sort key for canonical term ordering.

        Constants first (by value), then variables (by name), then
        sub-expressions (by operator and recursive key). This ensures
        fully deterministic ordering for commutative operators.
        """
        if isinstance(node, ConstantNode):
            return (0, node.value)
        if isinstance(node, VariableNode):
            return (1, node.name)
        if isinstance(node, BinaryOpNode):
            return (2, node.operator,
                    self._term_sort_key(node.left),
                    self._term_sort_key(node.right))
        if isinstance(node, UnaryOpNode):
            return (3, node.operator,
                    self._term_sort_key(node.operand))
        return (4,)

    def _rebuild_left_associative(
        self, op: str, terms: list[ASTNode],
    ) -> ASTNode:
        if not terms:
            raise ValueError(f"Cannot rebuild {op} from empty term list")
        if len(terms) == 1:
            return terms[0]
        result: ASTNode = terms[0]
        for t in terms[1:]:
            result = BinaryOpNode(op, result, t)
        return result


class VariableRenamingVisitor(ASTVisitor):
    """Canonicalizes variable names by mapping them to a standard set
    ``(x, y, z, ...)`` based on alphabetical order.

    This is intended for **template matching** where two expressions that
    differ only in variable names should be treated as equivalent.
    For strict mathematical equivalence checking, skip this pass.
    """

    def __init__(self, rename_map: dict[str, str]) -> None:
        self._rename_map: dict[str, str] = rename_map

    @classmethod
    def build_rename_map(cls, var_names: frozenset[str]) -> dict[str, str]:
        sorted_names = sorted(var_names)
        canonical_names: list[str] = []
        for i in range(len(sorted_names)):
            if i < 24:
                canonical_names.append(chr(ord("x") + i))
            else:
                canonical_names.append(f"v{i}")
        return dict(zip(sorted_names, canonical_names))

    def rename(self, node: ASTNode) -> ASTNode:
        return node.accept(self)

    def visit_constant(self, node: ConstantNode, **kwargs: Any) -> ConstantNode:
        return node

    def visit_variable(self, node: VariableNode, **kwargs: Any) -> VariableNode:
        new_name = self._rename_map.get(node.name, node.name)
        return VariableNode(new_name)

    def visit_binary_op(self, node: BinaryOpNode, **kwargs: Any) -> BinaryOpNode:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return BinaryOpNode(node.operator, left, right)

    def visit_unary_op(self, node: UnaryOpNode, **kwargs: Any) -> UnaryOpNode:
        operand = node.operand.accept(self)
        return UnaryOpNode(node.operator, operand)

    def visit_equation(self, node: EquationNode, **kwargs: Any) -> EquationNode:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return EquationNode(left, right)


class Canonicalizer:
    """Top-level orchestrator for expression canonicalization.

    Applies the full canonicalization pipeline:
    1. Recursive canonicalization of every node (sorting, folding)
    2. Optional variable renaming (for template matching)
    """

    def __init__(self, rename_variables: bool = False) -> None:
        self._rename_variables: bool = rename_variables

    def canonicalize(self, node: ASTNode) -> CanonicalResult:
        result = CanonicalizingVisitor().canonicalize(node)

        if self._rename_variables and result.variable_names:
            rename_map = VariableRenamingVisitor.build_rename_map(
                result.variable_names
            )
            renamed = VariableRenamingVisitor(rename_map).rename(result.tree)
            var_names = VariableCollector().collect(renamed)
            result = CanonicalResult(tree=renamed, variable_names=var_names)

        return result
