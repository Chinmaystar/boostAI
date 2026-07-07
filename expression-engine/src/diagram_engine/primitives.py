from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ══════════════════════════════════════════════════════════════════════════
# Enums
# ══════════════════════════════════════════════════════════════════════════

class PrimitiveType(Enum):
    POINT = "point"
    LINE = "line"
    POLYLINE = "polyline"
    CIRCLE = "circle"
    ARC = "arc"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    ARROW = "arrow"
    AXIS = "axis"
    GRID = "grid"
    TABLE_CELL = "table_cell"
    TEXT_LABEL = "text_label"
    MEASUREMENT = "measurement"
    TICK_MARK = "tick_mark"


class AnchorPosition(Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    CENTER = "center"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class LineCapStyle(Enum):
    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"


class LineJoinStyle(Enum):
    MITER = "miter"
    ROUND = "round"
    BEVEL = "bevel"


# ══════════════════════════════════════════════════════════════════════════
# Value Types
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class VariableRef:
    """A reference to a named variable in the variable graph.

    Used wherever a primitive property can be parameterized.
    The ``variable_name`` must match a ``Variable.name`` in the
    ``VariableGraph`` that the diagram template is paired with.
    """
    variable_name: str
    default_value: float | str | None = None

    def resolve(self, variables: dict[str, Any] | None = None) -> Any:
        if variables and self.variable_name in variables:
            return variables[self.variable_name]
        return self.default_value


NumericValue = float | int | VariableRef


# ══════════════════════════════════════════════════════════════════════════
# Style Data Classes
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class StrokeStyle:
    color: str = "#000000"
    width: float = 1.5
    dasharray: str | None = None
    opacity: float = 1.0
    linecap: LineCapStyle = LineCapStyle.BUTT
    linejoin: LineJoinStyle = LineJoinStyle.MITER

    def to_svg_attrs(self) -> str:
        parts = [
            f'stroke="{self.color}"',
            f'stroke-width="{self.width}"',
            f'stroke-opacity="{self.opacity}"',
            f'stroke-linecap="{self.linecap.value}"',
            f'stroke-linejoin="{self.linejoin.value}"',
        ]
        if self.dasharray is not None:
            parts.append(f'stroke-dasharray="{self.dasharray}"')
        return " ".join(parts)

    def to_dict(self) -> dict:
        return {
            "color": self.color,
            "width": self.width,
            "dasharray": self.dasharray,
            "opacity": self.opacity,
            "linecap": self.linecap.value,
            "linejoin": self.linejoin.value,
        }


@dataclass
class FillStyle:
    color: str = "none"
    opacity: float = 1.0
    color_map: str | None = None

    def to_svg_attrs(self) -> str:
        if self.color_map:
            return f'fill="url(#{self.color_map})" fill-opacity="{self.opacity}"'
        return f'fill="{self.color}" fill-opacity="{self.opacity}"'

    def to_dict(self) -> dict:
        return {
            "color": self.color,
            "opacity": self.opacity,
            "color_map": self.color_map,
        }


@dataclass
class FontStyle:
    family: str = "Arial, sans-serif"
    size: float = 12.0
    color: str = "#000000"
    bold: bool = False
    italic: bool = False
    anchor: str = "middle"
    dominant_baseline: str = "central"

    def to_svg_attrs(self) -> str:
        weight = "bold" if self.bold else "normal"
        style = "italic" if self.italic else "normal"
        return (
            f'font-family="{self.family}" '
            f'font-size="{self.size}" '
            f'fill="{self.color}" '
            f'font-weight="{weight}" '
            f'font-style="{style}" '
            f'text-anchor="{self.anchor}" '
            f'dominant-baseline="{self.dominant_baseline}"'
        )

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "size": self.size,
            "color": self.color,
            "bold": self.bold,
            "italic": self.italic,
            "anchor": self.anchor,
            "dominant_baseline": self.dominant_baseline,
        }


@dataclass
class PointStyle:
    radius: float = 3.0
    color: str = "#000000"
    fill: str = "#000000"
    stroke_width: float = 1.0
    symbol: str = "circle"

    def to_svg_attrs(self) -> str:
        return (
            f'r="{self.radius}" '
            f'stroke="{self.color}" '
            f'fill="{self.fill}" '
            f'stroke-width="{self.stroke_width}"'
        )

    def to_dict(self) -> dict:
        return {
            "radius": self.radius,
            "color": self.color,
            "fill": self.fill,
            "stroke_width": self.stroke_width,
            "symbol": self.symbol,
        }


# ══════════════════════════════════════════════════════════════════════════
# Bounding Box
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    @property
    def xmin(self) -> float:
        return self.x

    @property
    def ymin(self) -> float:
        return self.y

    @property
    def xmax(self) -> float:
        return self.x + self.width

    @property
    def ymax(self) -> float:
        return self.y + self.height

    @property
    def cx(self) -> float:
        return self.x + self.width / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.height / 2.0

    def contains(self, px: float, py: float) -> bool:
        return self.xmin <= px <= self.xmax and self.ymin <= py <= self.ymax

    def overlaps(self, other: BoundingBox) -> bool:
        return (
            self.xmin < other.xmax
            and self.xmax > other.xmin
            and self.ymin < other.ymax
            and self.ymax > other.ymin
        )

    def expanded(self, padding: float) -> BoundingBox:
        return BoundingBox(
            x=self.x - padding,
            y=self.y - padding,
            width=self.width + 2.0 * padding,
            height=self.height + 2.0 * padding,
        )

    def translate(self, dx: float, dy: float) -> BoundingBox:
        return BoundingBox(
            x=self.x + dx,
            y=self.y + dy,
            width=self.width,
            height=self.height,
        )

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    @staticmethod
    def union(boxes: list[BoundingBox]) -> BoundingBox:
        if not boxes:
            return BoundingBox(0, 0, 0, 0)
        xmin = min(b.xmin for b in boxes)
        ymin = min(b.ymin for b in boxes)
        xmax = max(b.xmax for b in boxes)
        ymax = max(b.ymax for b in boxes)
        return BoundingBox(xmin, ymin, xmax - xmin, ymax - ymin)


# ══════════════════════════════════════════════════════════════════════════
# Helper: resolve numeric values
# ══════════════════════════════════════════════════════════════════════════

def resolve_value(
    value: Any, variables: dict[str, Any] | None = None,
) -> Any:
    if isinstance(value, VariableRef):
        return value.resolve(variables)
    return value


# ══════════════════════════════════════════════════════════════════════════
# Primitive Data Classes
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class Point:
    id: str
    x: NumericValue
    y: NumericValue
    label: Optional[str] = None
    style: Optional[PointStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.POINT

    def resolved_x(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.x, variables))

    def resolved_y(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.y, variables))

    def bounding_box(
        self, variables: dict[str, Any] | None = None,
    ) -> BoundingBox:
        rx = self.resolved_x(variables)
        ry = self.resolved_y(variables)
        r = self.style.radius if self.style else 3.0
        return BoundingBox(rx - r, ry - r, 2.0 * r, 2.0 * r)

    def translate(self, dx: float, dy: float) -> None:
        if not isinstance(self.x, VariableRef):
            self.x = float(self.x) + dx
        if not isinstance(self.y, VariableRef):
            self.y = float(self.y) + dy

    def to_dict(self) -> dict:
        return {
            "primitive_type": "point",
            "id": self.id,
            "x": self.x.variable_name if isinstance(self.x, VariableRef) else self.x,
            "y": self.y.variable_name if isinstance(self.y, VariableRef) else self.y,
            "label": self.label,
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class Line:
    id: str
    start: str
    end: str
    style: Optional[StrokeStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.LINE

    def stroke(self) -> StrokeStyle:
        return self.style or StrokeStyle()

    def bounding_box(
        self, variables: dict[str, Any] | None = None,
        points: dict[str, Point] | None = None,
    ) -> BoundingBox:
        if points is None:
            return BoundingBox(0, 0, 0, 0)
        p1 = points.get(self.start)
        p2 = points.get(self.end)
        if p1 is None or p2 is None:
            return BoundingBox(0, 0, 0, 0)
        x1 = p1.resolved_x(variables)
        y1 = p1.resolved_y(variables)
        x2 = p2.resolved_x(variables)
        y2 = p2.resolved_y(variables)
        xmin = min(x1, x2)
        ymin = min(y1, y2)
        return BoundingBox(xmin, ymin, abs(x2 - x1), abs(y2 - y1))

    def to_dict(self) -> dict:
        return {
            "primitive_type": "line",
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class Polyline:
    id: str
    points: list[str]
    style: Optional[StrokeStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.POLYLINE

    def to_dict(self) -> dict:
        return {
            "primitive_type": "polyline",
            "id": self.id,
            "points": list(self.points),
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class Circle:
    id: str
    center: str
    radius: NumericValue
    stroke: Optional[StrokeStyle] = None
    fill: Optional[FillStyle] = None
    label: Optional[str] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.CIRCLE

    def resolved_radius(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.radius, variables))

    def bounding_box(
        self, variables: dict[str, Any] | None = None,
        points: dict[str, Point] | None = None,
    ) -> BoundingBox:
        if points is None:
            return BoundingBox(0, 0, 0, 0)
        c = points.get(self.center)
        if c is None:
            return BoundingBox(0, 0, 0, 0)
        cx = c.resolved_x(variables)
        cy = c.resolved_y(variables)
        r = self.resolved_radius(variables)
        return BoundingBox(cx - r, cy - r, 2.0 * r, 2.0 * r)

    def to_dict(self) -> dict:
        return {
            "primitive_type": "circle",
            "id": self.id,
            "center": self.center,
            "radius": self.radius.variable_name if isinstance(self.radius, VariableRef) else self.radius,
            "stroke": self.stroke.to_dict() if self.stroke else None,
            "fill": self.fill.to_dict() if self.fill else None,
            "label": self.label,
        }


@dataclass
class Arc:
    id: str
    center: str
    radius: NumericValue
    start_angle: float
    end_angle: float
    style: Optional[StrokeStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.ARC

    def resolved_radius(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.radius, variables))

    def to_dict(self) -> dict:
        return {
            "primitive_type": "arc",
            "id": self.id,
            "center": self.center,
            "radius": self.radius.variable_name if isinstance(self.radius, VariableRef) else self.radius,
            "start_angle": self.start_angle,
            "end_angle": self.end_angle,
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class Ellipse:
    id: str
    center: str
    rx: NumericValue
    ry: NumericValue
    stroke: Optional[StrokeStyle] = None
    fill: Optional[FillStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.ELLIPSE

    def to_dict(self) -> dict:
        return {
            "primitive_type": "ellipse",
            "id": self.id,
            "center": self.center,
            "rx": self.rx.variable_name if isinstance(self.rx, VariableRef) else self.rx,
            "ry": self.ry.variable_name if isinstance(self.ry, VariableRef) else self.ry,
            "stroke": self.stroke.to_dict() if self.stroke else None,
            "fill": self.fill.to_dict() if self.fill else None,
        }


@dataclass
class Rectangle:
    id: str
    x: NumericValue
    y: NumericValue
    width: NumericValue
    height: NumericValue
    stroke: Optional[StrokeStyle] = None
    fill: Optional[FillStyle] = None
    rx: Optional[float] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.RECTANGLE

    def resolved_x(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.x, variables))

    def resolved_y(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.y, variables))

    def resolved_width(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.width, variables))

    def resolved_height(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.height, variables))

    def to_dict(self) -> dict:
        return {
            "primitive_type": "rectangle",
            "id": self.id,
            "x": self.x.variable_name if isinstance(self.x, VariableRef) else self.x,
            "y": self.y.variable_name if isinstance(self.y, VariableRef) else self.y,
            "width": self.width.variable_name if isinstance(self.width, VariableRef) else self.width,
            "height": self.height.variable_name if isinstance(self.height, VariableRef) else self.height,
            "stroke": self.stroke.to_dict() if self.stroke else None,
            "fill": self.fill.to_dict() if self.fill else None,
            "rx": self.rx,
        }


@dataclass
class Polygon:
    id: str
    vertices: list[str]
    stroke: Optional[StrokeStyle] = None
    fill: Optional[FillStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.POLYGON

    def to_dict(self) -> dict:
        return {
            "primitive_type": "polygon",
            "id": self.id,
            "vertices": list(self.vertices),
            "stroke": self.stroke.to_dict() if self.stroke else None,
            "fill": self.fill.to_dict() if self.fill else None,
        }


@dataclass
class Arrow:
    id: str
    start: str
    end: str
    head_size: float = 8.0
    style: Optional[StrokeStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.ARROW

    def to_dict(self) -> dict:
        return {
            "primitive_type": "arrow",
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "head_size": self.head_size,
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class Axis:
    id: str
    start: str
    end: str
    label: Optional[str] = None
    ticks: list[float] = field(default_factory=list)
    tick_length: float = 5.0
    orientation: str = "horizontal"
    style: Optional[StrokeStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.AXIS

    def to_dict(self) -> dict:
        return {
            "primitive_type": "axis",
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "label": self.label,
            "ticks": list(self.ticks),
            "tick_length": self.tick_length,
            "orientation": self.orientation,
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class Grid:
    id: str
    x_lines: list[float] = field(default_factory=list)
    y_lines: list[float] = field(default_factory=list)
    style: Optional[StrokeStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.GRID

    def to_dict(self) -> dict:
        return {
            "primitive_type": "grid",
            "id": self.id,
            "x_lines": list(self.x_lines),
            "y_lines": list(self.y_lines),
            "style": self.style.to_dict() if self.style else None,
        }


@dataclass
class TableCell:
    id: str
    row: int
    col: int
    content: str
    x: float = 0.0
    y: float = 0.0
    width: float = 40.0
    height: float = 20.0
    stroke: Optional[StrokeStyle] = None
    fill: Optional[FillStyle] = None
    font: Optional[FontStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.TABLE_CELL

    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.height)

    def to_dict(self) -> dict:
        return {
            "primitive_type": "table_cell",
            "id": self.id,
            "row": self.row,
            "col": self.col,
            "content": self.content,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "stroke": self.stroke.to_dict() if self.stroke else None,
            "fill": self.fill.to_dict() if self.fill else None,
            "font": self.font.to_dict() if self.font else None,
        }


@dataclass
class TextLabel:
    id: str
    x: NumericValue
    y: NumericValue
    text: str
    font: Optional[FontStyle] = None
    anchor: AnchorPosition = AnchorPosition.CENTER
    rotation: Optional[float] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.TEXT_LABEL

    def resolved_x(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.x, variables))

    def resolved_y(self, variables: dict[str, Any] | None = None) -> float:
        return float(resolve_value(self.y, variables))

    def bounding_box(
        self, variables: dict[str, Any] | None = None,
        font_size: float | None = None,
    ) -> BoundingBox:
        rx = self.resolved_x(variables)
        ry = self.resolved_y(variables)
        fs = font_size or (self.font.size if self.font else 12.0)
        text_width = len(self.text) * fs * 0.6
        text_height = fs * 1.2
        return BoundingBox(rx - text_width / 2, ry - text_height / 2, text_width, text_height)

    def to_dict(self) -> dict:
        return {
            "primitive_type": "text_label",
            "id": self.id,
            "x": self.x.variable_name if isinstance(self.x, VariableRef) else self.x,
            "y": self.y.variable_name if isinstance(self.y, VariableRef) else self.y,
            "text": self.text,
            "font": self.font.to_dict() if self.font else None,
            "anchor": self.anchor.value,
            "rotation": self.rotation,
        }


@dataclass
class Measurement:
    id: str
    primitive_ref: str
    label: str
    value: Optional[NumericValue] = None
    offset: float = 15.0
    font: Optional[FontStyle] = None
    show_ticks: bool = True

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.MEASUREMENT

    def resolved_value(self, variables: dict[str, Any] | None = None) -> Any:
        if self.value is None:
            return None
        return resolve_value(self.value, variables)

    def to_dict(self) -> dict:
        return {
            "primitive_type": "measurement",
            "id": self.id,
            "primitive_ref": self.primitive_ref,
            "label": self.label,
            "value": self.value.variable_name if isinstance(self.value, VariableRef) else self.value,
            "offset": self.offset,
            "font": self.font.to_dict() if self.font else None,
            "show_ticks": self.show_ticks,
        }


@dataclass
class TickMark:
    id: str
    axis_ref: str
    position: float
    label: Optional[str] = None
    length: float = 5.0
    style: Optional[StrokeStyle] = None
    font: Optional[FontStyle] = None

    @property
    def primitive_type(self) -> PrimitiveType:
        return PrimitiveType.TICK_MARK

    def to_dict(self) -> dict:
        return {
            "primitive_type": "tick_mark",
            "id": self.id,
            "axis_ref": self.axis_ref,
            "position": self.position,
            "label": self.label,
            "length": self.length,
            "style": self.style.to_dict() if self.style else None,
            "font": self.font.to_dict() if self.font else None,
        }
