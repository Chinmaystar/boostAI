from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


OP_PRECEDENCE: dict[str, int] = {
    "=": 1,
    "+": 2,
    "-": 2,
    "*": 3,
    "/": 3,
}

UNARY_MINUS_PRECEDENCE = 4
PRIMARY_PRECEDENCE = 5

ASSOCIATIVE_OPS: set[str] = {"+", "*"}


class ASTNode(ABC):

    @abstractmethod
    def accept(self, visitor: ASTVisitor, **kwargs: Any) -> Any:
        ...

    @property
    @abstractmethod
    def precedence(self) -> int:
        ...


@dataclass
class ConstantNode(ASTNode):
    value: int

    def accept(self, visitor: ASTVisitor, **kwargs: Any) -> Any:
        return visitor.visit_constant(self, **kwargs)

    @property
    def precedence(self) -> int:
        return PRIMARY_PRECEDENCE

    def __repr__(self) -> str:
        return f"Constant({self.value})"


@dataclass
class VariableNode(ASTNode):
    name: str

    def accept(self, visitor: ASTVisitor, **kwargs: Any) -> Any:
        return visitor.visit_variable(self, **kwargs)

    @property
    def precedence(self) -> int:
        return PRIMARY_PRECEDENCE

    def __repr__(self) -> str:
        return f"Variable({self.name!r})"


@dataclass
class BinaryOpNode(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode

    def accept(self, visitor: ASTVisitor, **kwargs: Any) -> Any:
        return visitor.visit_binary_op(self, **kwargs)

    @property
    def precedence(self) -> int:
        return OP_PRECEDENCE.get(self.operator, 1)

    def __repr__(self) -> str:
        return f"{self.operator}({self.left!r}, {self.right!r})"


@dataclass
class UnaryOpNode(ASTNode):
    operator: str
    operand: ASTNode

    def accept(self, visitor: ASTVisitor, **kwargs: Any) -> Any:
        return visitor.visit_unary_op(self, **kwargs)

    @property
    def precedence(self) -> int:
        return UNARY_MINUS_PRECEDENCE

    def __repr__(self) -> str:
        return f"u{self.operator}({self.operand!r})"


@dataclass
class EquationNode(ASTNode):
    left: ASTNode
    right: ASTNode

    def accept(self, visitor: ASTVisitor, **kwargs: Any) -> Any:
        return visitor.visit_equation(self, **kwargs)

    @property
    def precedence(self) -> int:
        return OP_PRECEDENCE["="]

    def __repr__(self) -> str:
        return f"Equation({self.left!r}, {self.right!r})"


class ASTVisitor(ABC):

    def visit(self, node: ASTNode, **kwargs: Any) -> Any:
        return node.accept(self, **kwargs)

    @abstractmethod
    def visit_constant(self, node: ConstantNode, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def visit_variable(self, node: VariableNode, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def visit_unary_op(self, node: UnaryOpNode, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def visit_equation(self, node: EquationNode, **kwargs: Any) -> Any:
        ...


class ToStringVisitor(ASTVisitor):
    """Converts an AST to a minimal-parenthesis string representation."""

    def visit_constant(self, node: ConstantNode, **kwargs: Any) -> str:
        return str(node.value)

    def visit_variable(self, node: VariableNode, **kwargs: Any) -> str:
        return node.name

    def visit_binary_op(self, node: BinaryOpNode, **kwargs: Any) -> str:
        parent_prec: int = kwargs.get("parent_precedence", 0)
        side: Optional[str] = kwargs.get("side")

        left = node.left.accept(self, parent_precedence=node.precedence,
                                parent_operator=node.operator, side="left")
        right = node.right.accept(self, parent_precedence=node.precedence,
                                  parent_operator=node.operator, side="right")

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

    def visit_unary_op(self, node: UnaryOpNode, **kwargs: Any) -> str:
        parent_prec: int = kwargs.get("parent_precedence", 0)
        operand_str = node.operand.accept(self)

        if isinstance(node.operand, (BinaryOpNode,)):
            inner = f"{node.operator}({operand_str})"
        else:
            inner = f"{node.operator}{operand_str}"

        if parent_prec > UNARY_MINUS_PRECEDENCE:
            return f"({inner})"
        return inner

    def visit_equation(self, node: EquationNode, **kwargs: Any) -> str:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return f"{left} = {right}"
