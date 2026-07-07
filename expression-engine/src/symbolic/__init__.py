from .backend import SymbolicBackend
from .builtin_backend import BuiltinBackend
from .expression import SymbolicExpr, ExprType
from .visitor import (
    SymbolicVisitor, ToStringVisitor, CountNodesVisitor,
    CollectSymbolsVisitor,
)
from .exceptions import (
    SymbolicError, DivisionByZero, UnsimplifiableExpression,
    UnsupportedOperation, NoSolution, InfiniteSolutions,
    InvalidGeometry, DomainError, RangeError, InvalidExpression,
    ExpressionNotPolynomial, BackendNotFound, PluginRegistrationError,
)
from .expression_engine import ExpressionEngine
from .equation_engine import EquationEngine, EquationResult
from .equivalence_engine import EquivalenceEngine, EquivalenceResult
from .algebra_engine import AlgebraEngine
from .geometry_engine import GeometryEngine, Point, Line, Triangle, Circle
from .statistics_engine import (
    StatisticsEngine, FrequencyTable, GroupedFrequencyTable,
)
from .trigonometry_engine import TrigonometryEngine
from .evaluation_engine import EvaluationEngine
from .plugin import (
    SymbolicPluginRegistry, SymbolicPlugin, PluginMetadata,
)
from .ast_adapter import ASTExprAdapter

__all__ = [
    # Backend
    "SymbolicBackend",
    "BuiltinBackend",
    # Expression
    "SymbolicExpr",
    "ExprType",
    # Visitors
    "SymbolicVisitor",
    "ToStringVisitor",
    "CountNodesVisitor",
    "CollectSymbolsVisitor",
    # Exceptions
    "SymbolicError",
    "DivisionByZero",
    "UnsimplifiableExpression",
    "UnsupportedOperation",
    "NoSolution",
    "InfiniteSolutions",
    "InvalidGeometry",
    "DomainError",
    "RangeError",
    "InvalidExpression",
    "ExpressionNotPolynomial",
    "BackendNotFound",
    "PluginRegistrationError",
    # Engines
    "ExpressionEngine",
    "EquationEngine",
    "EquationResult",
    "EquivalenceEngine",
    "EquivalenceResult",
    "AlgebraEngine",
    "GeometryEngine",
    "Point",
    "Line",
    "Triangle",
    "Circle",
    "StatisticsEngine",
    "FrequencyTable",
    "GroupedFrequencyTable",
    "TrigonometryEngine",
    "EvaluationEngine",
    # Plugin
    "SymbolicPluginRegistry",
    "SymbolicPlugin",
    "PluginMetadata",
    # Adapter
    "ASTExprAdapter",
]
