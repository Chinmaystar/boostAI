from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class VariableType(Enum):
    """Every variable kind the engine can represent.

    The enum is designed for forward compatibility — new mathematics
    topics add new members without redesigning the class hierarchy.
    """
    INTEGER = "integer"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    SYMBOL = "symbol"
    COEFFICIENT = "coefficient"
    CONSTANT = "constant"
    EXPRESSION = "expression"
    EQUATION = "equation"
    COORDINATE = "coordinate"
    POINT = "point"
    LINE = "line"
    CIRCLE = "circle"
    RADIUS = "radius"
    DIAMETER = "diameter"
    LENGTH = "length"
    AREA = "area"
    VOLUME = "volume"
    ANGLE = "angle"
    RATIO = "ratio"
    PROBABILITY = "probability"
    PERCENTAGE = "percentage"
    MATRIX = "matrix"
    VECTOR = "vector"
    GRAPH_POINT = "graph_point"
    FUNCTION = "function"
    TABLE_CELL = "table_cell"
    CATEGORICAL = "categorical"
    TEXT_LABEL = "text_label"
    DIAGRAM = "diagram"


@dataclass(frozen=True)
class VariableDomain:
    """Constraints on the values a variable may take."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: tuple[Any, ...] = ()
    is_integer: bool = True
    is_positive: bool = False
    is_negative: bool = False

    def to_dict(self) -> dict:
        return {
            "min_value": self.min_value,
            "max_value": self.max_value,
            "allowed_values": list(self.allowed_values),
            "is_integer": self.is_integer,
            "is_positive": self.is_positive,
            "is_negative": self.is_negative,
        }


@dataclass(frozen=True)
class SourceLocation:
    """Where in the input a variable originated."""
    expression: str = ""
    approximate_position: Optional[int] = None
    diagram_reference: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "approximate_position": self.approximate_position,
            "diagram_reference": self.diagram_reference,
        }


@dataclass(frozen=True)
class VariableMetadata:
    """Semantic metadata attached to every variable."""
    ast_node_type: str = ""
    template_slot: Optional[str] = None
    can_randomize: bool = True
    is_derived: bool = False
    is_user_visible: bool = True
    participates_in_constraints: bool = True
    source_location: SourceLocation = field(default_factory=SourceLocation)

    def to_dict(self) -> dict:
        return {
            "ast_node_type": self.ast_node_type,
            "template_slot": self.template_slot,
            "can_randomize": self.can_randomize,
            "is_derived": self.is_derived,
            "is_user_visible": self.is_user_visible,
            "participates_in_constraints": self.participates_in_constraints,
            "source_location": self.source_location.to_dict(),
        }


@dataclass(frozen=True)
class Variable:
    """A strongly typed semantic variable extracted from an expression.

    Every variable carries its own identity, type, values, domain
    constraints, and provenance metadata.  Future mathematics topics
    add new ``VariableType`` enum members without changing this class.
    """
    id: str
    name: str
    type: VariableType
    original_value: Any
    canonical_value: Any
    domain: VariableDomain = field(default_factory=VariableDomain)
    metadata: VariableMetadata = field(default_factory=VariableMetadata)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "original_value": self.original_value,
            "canonical_value": self.canonical_value,
            "domain": self.domain.to_dict(),
            "metadata": self.metadata.to_dict(),
        }

    @staticmethod
    def new_id(prefix: str = "v") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
