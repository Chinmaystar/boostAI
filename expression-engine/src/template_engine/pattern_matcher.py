from __future__ import annotations

from dataclasses import dataclass, field

from src.ast import (
    ASTNode, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
)
from .structural_hasher import StructuralHasher
from .template_signature import TemplateSignature


@dataclass
class MatchResult:
    """Result of matching an AST against a template.

    Attributes:
        matched: Whether the AST matches the template's structural shape.
        slot_values: Mapping from slot name (``"a"``, ``"b"``, …) to the
            concrete integer value found in the AST.
        variable_bindings: Mapping from generic variable name (``"x"``,
            ``"y"``, …) to the concrete variable name found in the AST.
    """
    matched: bool
    slot_values: dict[str, int] = field(default_factory=dict)
    variable_bindings: dict[str, str] = field(default_factory=dict)


class PatternMatcher:
    """Matches an AST against known template patterns.

    Matching is based on structural equivalence (abstract tree shape).
    When a match is found the concrete values of constants and variable
    names are extracted as slot bindings.
    """

    @staticmethod
    def matches(ast: ASTNode, signature: TemplateSignature) -> bool:
        """Check whether an AST matches a template's structural shape.

        Args:
            ast: The canonicalised AST to check.
            signature: The template to match against.

        Returns:
            ``True`` if the AST is structurally equivalent to the
            template's defining shape.
        """
        return StructuralHasher.hash(ast) == signature.structural_hash

    @staticmethod
    def match(ast: ASTNode, signature: TemplateSignature) -> MatchResult:
        """Match an AST against a template and extract slot bindings.

        Args:
            ast: The canonicalised AST to check.
            signature: The template to match against.

        Returns:
            A ``MatchResult`` with extracted slot values and variable
            bindings.
        """
        if not PatternMatcher.matches(ast, signature):
            return MatchResult(matched=False)

        slots = _extract_slots(ast)
        variables = _extract_variables(ast)
        return MatchResult(
            matched=True,
            slot_values=slots,
            variable_bindings=variables,
        )

    @staticmethod
    def find_matching_templates(
        ast: ASTNode,
        registry: "TemplateRegistry",  # noqa: F821
    ) -> list[TemplateSignature]:
        """Find all templates in a registry that match the given AST.

        Args:
            ast: The canonicalised AST to check.
            registry: A ``TemplateRegistry`` instance.

        Returns:
            A list of matching ``TemplateSignature`` objects.
        """
        h = StructuralHasher.hash(ast)
        sig = registry.lookup_by_hash(h)
        if sig is not None:
            return [sig]
        return []


def _extract_slots(node: ASTNode) -> dict[str, int]:
    """Walk the AST left-to-right, assigning slot names ``a, b, c, …``
    to ``ConstantNode`` instances in encounter order."""
    slots: dict[str, int] = {}
    counter = 0

    def walk(n: ASTNode) -> None:
        nonlocal counter
        if isinstance(n, ConstantNode):
            name = chr(ord("a") + counter)
            slots[name] = n.value
            counter += 1
        elif isinstance(n, UnaryOpNode):
            walk(n.operand)
        elif isinstance(n, (BinaryOpNode, EquationNode)):
            walk(n.left)
            walk(n.right)

    walk(node)
    return slots


def _extract_variables(node: ASTNode) -> dict[str, str]:
    """Walk the AST left-to-right, assigning generic names ``x, y, z, …``
    to ``VariableNode`` instances in encounter order."""
    variables: dict[str, str] = {}
    counter = 0

    def walk(n: ASTNode) -> None:
        nonlocal counter
        if isinstance(n, VariableNode):
            name = chr(ord("x") + counter)
            variables[name] = n.name
            counter += 1
        elif isinstance(n, UnaryOpNode):
            walk(n.operand)
        elif isinstance(n, (BinaryOpNode, EquationNode)):
            walk(n.left)
            walk(n.right)

    walk(node)
    return variables
