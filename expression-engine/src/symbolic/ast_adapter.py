from __future__ import annotations

from src.ast import (
    ASTNode, ASTVisitor, ConstantNode, VariableNode,
    BinaryOpNode, UnaryOpNode, EquationNode,
)
from .expression import SymbolicExpr, ExprType


class ASTExprAdapter(ASTVisitor):
    """Converts an ``ASTNode`` tree into a ``SymbolicExpr`` tree.

    This is the bridge between Milestones 1-5 (which operate on
    ``ASTNode``) and Milestone 6 (which operates on ``SymbolicExpr``).
    Every engine in the pipeline can now pass its output to the
    Symbolic Mathematics Layer.

    Usage::

        adapter = ASTExprAdapter()
        symbolic_expr = adapter.convert(ast_node)
    """

    def convert(self, node: ASTNode) -> SymbolicExpr:
        return node.accept(self)

    def visit_constant(self, node: ConstantNode, **kwargs: object
                       ) -> SymbolicExpr:
        return SymbolicExpr.number(node.value)

    def visit_variable(self, node: VariableNode, **kwargs: object
                       ) -> SymbolicExpr:
        return SymbolicExpr.symbol(node.name)

    def visit_binary_op(self, node: BinaryOpNode, **kwargs: object
                        ) -> SymbolicExpr:
        left = node.left.accept(self)
        right = node.right.accept(self)
        op_map = {
            "+": SymbolicExpr.add,
            "-": SymbolicExpr.sub,
            "*": SymbolicExpr.mul,
            "/": SymbolicExpr.div,
            "^": SymbolicExpr.pow,
            "**": SymbolicExpr.pow,
        }
        maker = op_map.get(node.operator)
        if maker is None:
            raise ValueError(f"Unsupported operator: '{node.operator}'")
        return maker(left, right)

    def visit_unary_op(self, node: UnaryOpNode, **kwargs: object
                       ) -> SymbolicExpr:
        operand = node.operand.accept(self)
        if node.operator == "-":
            return SymbolicExpr.neg(operand)
        raise ValueError(f"Unsupported unary operator: '{node.operator}'")

    def visit_equation(self, node: EquationNode, **kwargs: object
                       ) -> SymbolicExpr:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return SymbolicExpr.equal(left, right)
