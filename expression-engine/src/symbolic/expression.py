from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional


class ExprType(Enum):
    NUMBER = auto()
    SYMBOL = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    NEG = auto()
    SQRT = auto()
    ABS = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    ARCSIN = auto()
    ARCCOS = auto()
    ARCTAN = auto()
    EQUAL = auto()
    FRACTION = auto()


@dataclass(frozen=True, slots=True)
class SymbolicExpr:
    type: ExprType
    value: Any = None
    children: tuple[SymbolicExpr, ...] = ()

    # ── factory helpers ────────────────────────────────────────────

    @staticmethod
    def number(n: int | float) -> SymbolicExpr:
        return SymbolicExpr(ExprType.NUMBER, value=float(n))

    @staticmethod
    def symbol(name: str) -> SymbolicExpr:
        return SymbolicExpr(ExprType.SYMBOL, value=name)

    @staticmethod
    def add(a: SymbolicExpr, b: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.ADD, children=(a, b))

    @staticmethod
    def sub(a: SymbolicExpr, b: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.SUB, children=(a, b))

    @staticmethod
    def mul(a: SymbolicExpr, b: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.MUL, children=(a, b))

    @staticmethod
    def div(a: SymbolicExpr, b: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.DIV, children=(a, b))

    @staticmethod
    def pow(a: SymbolicExpr, b: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.POW, children=(a, b))

    @staticmethod
    def neg(a: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.NEG, children=(a,))

    @staticmethod
    def sqrt(a: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.SQRT, children=(a,))

    @staticmethod
    def abs(a: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.ABS, children=(a,))

    @staticmethod
    def sin(a: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.SIN, children=(a,))

    @staticmethod
    def cos(a: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.COS, children=(a,))

    @staticmethod
    def tan(a: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.TAN, children=(a,))

    @staticmethod
    def equal(a: SymbolicExpr, b: SymbolicExpr) -> SymbolicExpr:
        return SymbolicExpr(ExprType.EQUAL, children=(a, b))

    @staticmethod
    def fraction(numer: int | float, denom: int | float) -> SymbolicExpr:
        return SymbolicExpr(ExprType.FRACTION, value=(float(numer), float(denom)))

    # ── query helpers ──────────────────────────────────────────────

    def is_number(self) -> bool:
        return self.type is ExprType.NUMBER

    def is_symbol(self) -> bool:
        return self.type is ExprType.SYMBOL

    def is_constant(self) -> bool:
        return self.type is ExprType.NUMBER

    def is_neg(self) -> bool:
        return self.type is ExprType.NEG

    def is_add(self) -> bool:
        return self.type is ExprType.ADD

    def is_mul(self) -> bool:
        return self.type is ExprType.MUL

    def is_div(self) -> bool:
        return self.type is ExprType.DIV

    def is_pow(self) -> bool:
        return self.type is ExprType.POW

    def is_equal(self) -> bool:
        return self.type is ExprType.EQUAL

    def is_fraction(self) -> bool:
        return self.type is ExprType.FRACTION

    def numeric_value(self) -> float:
        if self.type is ExprType.NUMBER:
            return self.value
        raise TypeError(f"Expression is not a number: {self.type}")

    def symbol_name(self) -> str:
        if self.type is ExprType.SYMBOL:
            return self.value
        raise TypeError(f"Expression is not a symbol: {self.type}")

    def left(self) -> SymbolicExpr:
        return self.children[0]

    def right(self) -> SymbolicExpr:
        return self.children[1]

    def operand(self) -> SymbolicExpr:
        return self.children[0]

    def symbols(self) -> set[str]:
        result: set[str] = set()
        stack = [self]
        while stack:
            node = stack.pop()
            if node.type is ExprType.SYMBOL:
                result.add(node.value)
            stack.extend(node.children)
        return result

    def depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(c.depth() for c in self.children)

    def size(self) -> int:
        count = 1
        for c in self.children:
            count += c.size()
        return count

    def __hash__(self) -> int:
        return hash((self.type, self.value, self.children))
