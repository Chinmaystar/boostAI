from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from src.ast import (
    ASTNode, ASTVisitor, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
    ASSOCIATIVE_OPS,
)
from .structural_hasher import StructuralHasher


@dataclass(frozen=True)
class TemplateSignature:
    """A deterministic, immutable signature that identifies a template.

    Two expressions that belong to the same template will produce
    ``TemplateSignature`` objects with identical ``structural_hash``
    and ``template_id`` values, regardless of the specific constants
    or variable names used in each expression.

    Attributes:
        template_id: A human-readable identifier (e.g. ``"LinearEquation"``).
        template_family: High-level category (e.g. ``"Algebra"``).
        canonical_pattern: A string like ``"a*x+b=c"`` where constants
            are replaced by slot names and variables by generic names.
        variable_slots: Ordered tuple of slot names appearing in the
            pattern, e.g. ``("a", "b", "c")``.
        structural_hash: SHA-256 hex digest of the structural fingerprint.
        confidence: A float ``[0.0, 1.0]`` indicating confidence in the
            template assignment.
    """
    template_id: str
    template_family: str
    canonical_pattern: str
    variable_slots: tuple[str, ...]
    structural_hash: str
    confidence: float


_KNOWN_PATTERNS: dict[str, str] = {
    "E(A(C,M(C,V)),C)": "LinearEquation",
    "M(A(C,V),C)": "DistributiveMultiplication",
    "M(C,V)": "ScalarMultiplication",
    "A(C,V)": "LinearExpression",
    "C": "ConstantExpression",
    "V": "VariableExpression",
    "E(A(C,V),C)": "SimpleLinearEquation",
}


class TemplateSignatureBuilder:
    """Builds a ``TemplateSignature`` from a canonicalised AST.

    The builder is deterministic: given the same canonical AST it will
    always produce the same signature.

    Usage::

        builder = TemplateSignatureBuilder()
        signature = builder.build(canonical_ast)
    """

    def __init__(self, family: Optional[str] = None) -> None:
        self._family: Optional[str] = family

    def build(self, ast: ASTNode) -> TemplateSignature:
        """Construct a ``TemplateSignature`` from a canonical AST.

        Args:
            ast: The root of a canonicalised AST.

        Returns:
            A ``TemplateSignature`` with all fields populated.
        """
        fp = StructuralHasher.fingerprint(ast)
        struct_hash = StructuralHasher.hash(ast)
        family = self._family if self._family is not None else _detect_family(ast)
        pattern = _PatternRenderer().render(ast)
        slots = _extract_slot_names(ast)
        tid = _generate_template_id(fp, pattern)
        return TemplateSignature(
            template_id=tid,
            template_family=family,
            canonical_pattern=pattern,
            variable_slots=slots,
            structural_hash=struct_hash,
            confidence=1.0,
        )


def _detect_family(node: ASTNode) -> str:
    """Heuristically detect the template family from the AST root type."""
    if isinstance(node, EquationNode):
        return "Algebra"
    return "Expression"


def _generate_template_id(fp: str, pattern: str) -> str:
    """Generate a human-readable template ID.

    Prefers a known name from ``_KNOWN_PATTERNS``; falls back to a
    slug derived from the canonical pattern.
    """
    known = _KNOWN_PATTERNS.get(fp)
    if known is not None:
        return known

    slug = _pattern_to_slug(pattern)
    if slug:
        return slug
    h = hashlib.sha256(fp.encode("utf-8")).hexdigest()[:8]
    return f"Template-{h}"


def _pattern_to_slug(pattern: str) -> str:
    """Convert a pattern string to a PascalCase identifier.

    E.g. ``"a*(x-y)"`` → ``"ADistributedOverXMinusY"`` → but this is
    poor.  Instead we use a structural approach:
    strip non-alpha, split on boundaries, capitalise.
    """
    import re
    cleaned = re.sub(r"[^a-zA-Z]", " ", pattern)
    parts = cleaned.split()
    if not parts:
        return ""
    return "".join(p.capitalize() for p in parts)


def _extract_slot_names(node: ASTNode) -> tuple[str, ...]:
    """Return slot names in encounter order (left-to-right traversal)."""
    names: list[str] = []
    counter = 0

    def walk(n: ASTNode) -> None:
        nonlocal counter
        if isinstance(n, ConstantNode):
            names.append(chr(ord("a") + counter))
            counter += 1
        elif isinstance(n, UnaryOpNode):
            walk(n.operand)
        elif isinstance(n, (BinaryOpNode, EquationNode)):
            walk(n.left)
            walk(n.right)

    walk(node)
    return tuple(names)


class _PatternRenderer(ASTVisitor):
    """Renders an AST as a canonical pattern string.

    Constants are replaced by slot names ``a, b, c, …`` and variables
    by generic names ``x, y, z, …``, following the same left-to-right
    traversal order as ``ToStingVisitor`` but with abstract names.
    """

    def __init__(self) -> None:
        self._const_counter: int = 0
        self._var_counter: int = 0

    def render(self, node: ASTNode) -> str:
        self._const_counter = 0
        self._var_counter = 0
        return node.accept(self)

    def _next_const_slot(self) -> str:
        name = chr(ord("a") + self._const_counter)
        self._const_counter += 1
        return name

    def _next_var_slot(self) -> str:
        name = chr(ord("x") + self._var_counter)
        self._var_counter += 1
        return name

    def visit_constant(self, node: ConstantNode, **kwargs: object) -> str:
        return self._next_const_slot()

    def visit_variable(self, node: VariableNode, **kwargs: object) -> str:
        return self._next_var_slot()

    def visit_binary_op(self, node: BinaryOpNode, **kwargs: object) -> str:
        parent_prec: int = kwargs.get("parent_precedence", 0)  # type: ignore[assignment]
        side: Optional[str] = kwargs.get("side")  # type: ignore[assignment]

        left = node.left.accept(
            self,
            parent_precedence=node.precedence,
            parent_operator=node.operator,
            side="left",
        )
        right = node.right.accept(
            self,
            parent_precedence=node.precedence,
            parent_operator=node.operator,
            side="right",
        )

        inner = f"{left} {node.operator} {right}"

        needs_parens = False
        if parent_prec > node.precedence:
            needs_parens = True
        elif (
            parent_prec == node.precedence
            and node.operator not in ASSOCIATIVE_OPS
            and side == "right"
        ):
            needs_parens = True

        if needs_parens:
            return f"({inner})"
        return inner

    def visit_unary_op(self, node: UnaryOpNode, **kwargs: object) -> str:
        parent_prec: int = kwargs.get("parent_precedence", 0)  # type: ignore[assignment]
        operand_str = node.operand.accept(self)

        if isinstance(node.operand, (BinaryOpNode,)):
            inner = f"{node.operator}({operand_str})"
        else:
            inner = f"{node.operator}{operand_str}"

        if parent_prec > 4:
            return f"({inner})"
        return inner

    def visit_equation(self, node: EquationNode, **kwargs: object) -> str:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return f"{left} = {right}"
