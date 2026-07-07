from __future__ import annotations

from abc import ABC, abstractmethod
from .expression import SymbolicExpr, ExprType


class SymbolicVisitor(ABC):
    """Base visitor for symbolic expression trees."""

    def visit(self, expr: SymbolicExpr):
        method_name = f"visit_{expr.type.name.lower()}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(expr)

    def generic_visit(self, expr: SymbolicExpr):
        raise NotImplementedError(f"No visitor for {expr.type}")


class ToStringVisitor(SymbolicVisitor):
    """Converts a SymbolicExpr to its string representation."""

    def visit_number(self, expr: SymbolicExpr) -> str:
        v = expr.value
        return str(int(v)) if v == int(v) else str(v)

    def visit_symbol(self, expr: SymbolicExpr) -> str:
        return str(expr.value)

    def visit_add(self, expr: SymbolicExpr) -> str:
        return f"({self.visit(expr.children[0])} + {self.visit(expr.children[1])})"

    def visit_sub(self, expr: SymbolicExpr) -> str:
        return f"({self.visit(expr.children[0])} - {self.visit(expr.children[1])})"

    def visit_mul(self, expr: SymbolicExpr) -> str:
        return f"({self.visit(expr.children[0])} * {self.visit(expr.children[1])})"

    def visit_div(self, expr: SymbolicExpr) -> str:
        return f"({self.visit(expr.children[0])} / {self.visit(expr.children[1])})"

    def visit_pow(self, expr: SymbolicExpr) -> str:
        return f"({self.visit(expr.children[0])} ** {self.visit(expr.children[1])})"

    def visit_neg(self, expr: SymbolicExpr) -> str:
        return f"(-{self.visit(expr.children[0])})"

    def visit_sqrt(self, expr: SymbolicExpr) -> str:
        return f"sqrt({self.visit(expr.children[0])})"

    def visit_abs(self, expr: SymbolicExpr) -> str:
        return f"|{self.visit(expr.children[0])}|"

    def visit_sin(self, expr: SymbolicExpr) -> str:
        return f"sin({self.visit(expr.children[0])})"

    def visit_cos(self, expr: SymbolicExpr) -> str:
        return f"cos({self.visit(expr.children[0])})"

    def visit_tan(self, expr: SymbolicExpr) -> str:
        return f"tan({self.visit(expr.children[0])})"

    def visit_arcsin(self, expr: SymbolicExpr) -> str:
        return f"arcsin({self.visit(expr.children[0])})"

    def visit_arccos(self, expr: SymbolicExpr) -> str:
        return f"arccos({self.visit(expr.children[0])})"

    def visit_arctan(self, expr: SymbolicExpr) -> str:
        return f"arctan({self.visit(expr.children[0])})"

    def visit_equal(self, expr: SymbolicExpr) -> str:
        return f"({self.visit(expr.children[0])} = {self.visit(expr.children[1])})"

    def visit_fraction(self, expr: SymbolicExpr) -> str:
        n, d = expr.value
        return f"{n}/{d}"

    def generic_visit(self, expr: SymbolicExpr) -> str:
        return f"<?{expr.type.name}>"


class CountNodesVisitor(SymbolicVisitor):
    """Counts total nodes in a symbolic expression."""

    def generic_visit(self, expr: SymbolicExpr) -> int:
        total = 1
        for c in expr.children:
            total += self.visit(c)
        return total


class CollectSymbolsVisitor(SymbolicVisitor):
    """Collects all symbol names in an expression."""

    def __init__(self) -> None:
        self.symbols: set[str] = set()

    def visit_symbol(self, expr: SymbolicExpr) -> None:
        self.symbols.add(expr.value)

    def generic_visit(self, expr: SymbolicExpr) -> None:
        for c in expr.children:
            self.visit(c)
