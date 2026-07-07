from __future__ import annotations

from src.ast import (
    ASTNode, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
)


class StructuralComparator:
    """Compares two ASTs for structural similarity.

    Two ASTs are considered structurally equivalent when they share the
    same abstract tree shape — all ``ConstantNode`` instances collapse to
    a single ``C`` marker, all ``VariableNode`` to ``V``, and operator
    types on binary/unary nodes are ignored. This allows expressions like
    ``2x+5=17`` and ``7x+3=38`` to be recognised as the same template.

    The comparator also provides a floating-point similarity score
    for near-match detection.
    """

    @staticmethod
    def are_equivalent(a: ASTNode, b: ASTNode) -> bool:
        """Return ``True`` when both ASTs share the same abstract shape.

        Two trees are equivalent if their structural fingerprints are
        identical (see ``StructuralHasher.fingerprint``).
        """
        from .structural_hasher import _fingerprint
        return _fingerprint(a) == _fingerprint(b)

    @staticmethod
    def similarity(a: ASTNode, b: ASTNode) -> float:
        """Compute a structural similarity score in ``[0.0, 1.0]``.

        ``1.0`` means the trees are structurally equivalent (same
        abstract shape). Lower values indicate increasing divergence.

        The algorithm compares tree structure node-by-node:
        * Matching node types at the same position contribute positively.
        * ``ConstantNode`` vs ``ConstantNode`` and ``VariableNode`` vs
          ``VariableNode`` always match (concrete values ignored).
        * ``BinaryOpNode`` vs ``BinaryOpNode`` always match (operator
          ignored).
        * Mismatched node types contribute zero.
        """
        total, matched = _count_matches(a, b)
        if total == 0:
            return 1.0
        return matched / total


def _count_matches(a: ASTNode, b: ASTNode) -> tuple[int, int]:
    """Return ``(total_nodes, matching_nodes)`` for a pair of subtrees."""
    type_a = _shape_tag(a)
    type_b = _shape_tag(b)

    total = 1
    matched = 1 if type_a == type_b else 0

    children_a = _children(a)
    children_b = _children(b)

    if len(children_a) != len(children_b):
        total += sum(_node_count(c) for c in children_a)
        total += sum(_node_count(c) for c in children_b)
        return total, matched

    for ca, cb in zip(children_a, children_b):
        t, m = _count_matches(ca, cb)
        total += t
        matched += m

    return total, matched


def _shape_tag(node: ASTNode) -> str:
    if isinstance(node, ConstantNode):
        return "C"
    if isinstance(node, VariableNode):
        return "V"
    if isinstance(node, UnaryOpNode):
        return "U"
    if isinstance(node, BinaryOpNode):
        return "B"
    if isinstance(node, EquationNode):
        return "E"
    return "?"


def _children(node: ASTNode) -> list[ASTNode]:
    if isinstance(node, UnaryOpNode):
        return [node.operand]
    if isinstance(node, BinaryOpNode):
        return _sorted_children(node)
    if isinstance(node, EquationNode):
        return [node.left, node.right]
    return []


def _sorted_children(node: BinaryOpNode) -> list[ASTNode]:
    """Return children sorted by their structural fingerprint so that
    commutative reorderings are treated as equivalent."""
    from .structural_hasher import _fingerprint
    left = node.left
    right = node.right
    if _fingerprint(left) <= _fingerprint(right):
        return [left, right]
    return [right, left]


def _node_count(node: ASTNode) -> int:
    count = 1
    for child in _children(node):
        count += _node_count(child)
    return count
