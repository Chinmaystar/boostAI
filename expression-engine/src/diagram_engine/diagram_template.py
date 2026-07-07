from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .diagram_graph import DiagramGraph
from .primitives import (
    Arrow, Axis, Circle, Ellipse, Grid, Line, Measurement, Point,
    Polygon, Polyline, Rectangle, TableCell, TextLabel, TickMark, Arc,
    BoundingBox, PrimitiveType, resolve_value, VariableRef,
)
from .variable_binding import VariableBindingEngine, BindingScope


# ══════════════════════════════════════════════════════════════════════════
# Supported diagram type identifiers (mirrors and extends DiagramType)
# ══════════════════════════════════════════════════════════════════════════

DIAGRAM_TYPE_TRIANGLE = "triangle"
DIAGRAM_TYPE_POLYGON = "polygon"
DIAGRAM_TYPE_CIRCLE = "circle"
DIAGRAM_TYPE_SECTOR = "sector"
DIAGRAM_TYPE_ANGLE = "angle"
DIAGRAM_TYPE_COORDINATE_GRID = "coordinate_grid"
DIAGRAM_TYPE_CARTESIAN_GRAPH = "cartesian_graph"
DIAGRAM_TYPE_LINE_GRAPH = "line_graph"
DIAGRAM_TYPE_BAR_GRAPH = "bar_graph"
DIAGRAM_TYPE_HISTOGRAM = "histogram"
DIAGRAM_TYPE_PIE_CHART = "pie_chart"
DIAGRAM_TYPE_SCATTER_PLOT = "scatter_plot"
DIAGRAM_TYPE_TABLE = "table"
DIAGRAM_TYPE_VENN = "venn"
DIAGRAM_TYPE_TREE = "tree"
DIAGRAM_TYPE_PROBABILITY = "probability"
DIAGRAM_TYPE_FLOW = "flow"
DIAGRAM_TYPE_CUSTOM = "custom"

SUPPORTED_DIAGRAM_TYPES: tuple[str, ...] = (
    DIAGRAM_TYPE_TRIANGLE, DIAGRAM_TYPE_POLYGON,
    DIAGRAM_TYPE_CIRCLE, DIAGRAM_TYPE_SECTOR,
    DIAGRAM_TYPE_ANGLE, DIAGRAM_TYPE_COORDINATE_GRID,
    DIAGRAM_TYPE_CARTESIAN_GRAPH, DIAGRAM_TYPE_LINE_GRAPH,
    DIAGRAM_TYPE_BAR_GRAPH, DIAGRAM_TYPE_HISTOGRAM,
    DIAGRAM_TYPE_PIE_CHART, DIAGRAM_TYPE_SCATTER_PLOT,
    DIAGRAM_TYPE_TABLE, DIAGRAM_TYPE_VENN,
    DIAGRAM_TYPE_TREE, DIAGRAM_TYPE_PROBABILITY,
    DIAGRAM_TYPE_FLOW, DIAGRAM_TYPE_CUSTOM,
)


# ══════════════════════════════════════════════════════════════════════════
# Template Metadata
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class TemplateMetadata:
    """Metadata attached to every ``DiagramTemplate``."""
    template_id: str
    diagram_type: str = DIAGRAM_TYPE_CUSTOM
    display_name: str = ""
    description: str = ""
    version: str = "1.0.0"
    created_at: str = ""
    updated_at: str = ""
    plugin_source: str = "builtin"
    tags: list[str] = field(default_factory=list)
    concept: str = ""
    subject: str = "Mathematics"

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = _now_iso()
        if not self.updated_at:
            self.updated_at = _now_iso()

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "diagram_type": self.diagram_type,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "plugin_source": self.plugin_source,
            "tags": list(self.tags),
            "concept": self.concept,
            "subject": self.subject,
        }


# ══════════════════════════════════════════════════════════════════════════
# DiagramTemplate
# ══════════════════════════════════════════════════════════════════════════

Primitive = (
    Point | Line | Polyline | Circle | Arc | Ellipse | Rectangle
    | Polygon | Arrow | Axis | Grid | TableCell | TextLabel
    | Measurement | TickMark
)


@dataclass
class DiagramTemplate:
    """A reusable, parameterized mathematical diagram.

    This is the primary output of the Dynamic Diagram Engine.
    A ``DiagramTemplate`` holds everything needed to render a diagram
    dynamically from structured primitives and variable bindings.

    Attributes:
        metadata: Template-level metadata (ID, type, version, etc.).
        primitives: All drawing primitives that make up the diagram.
        graph: Relationship graph between primitives.
        bindings: Variable bindings linking primitive properties
            to named variables.
        svg_template: The cached SVG output (with data attributes
            marking variable bindings). May be ``None`` before the
            first render.
        is_parameterized: ``True`` when at least one primitive property
            is bound to a variable.  ``False`` for a fully concrete diagram.
        fallback_image_path: Path to a PNG fallback image, if the
            diagram could not be parameterized.
        layout_viewbox: The SVG viewBox that encompasses all primitives.
    """
    metadata: TemplateMetadata
    primitives: list[Primitive] = field(default_factory=list)
    graph: DiagramGraph = field(default_factory=DiagramGraph)
    bindings: VariableBindingEngine = field(default_factory=VariableBindingEngine)
    svg_template: Optional[str] = None
    is_parameterized: bool = False
    fallback_image_path: Optional[str] = None
    layout_viewbox: Optional[BoundingBox] = None

    # ---- primitive access ------------------------------------------------

    def get_primitive(self, primitive_id: str) -> Optional[Primitive]:
        for p in self.primitives:
            if p.id == primitive_id:
                return p
        return None

    def get_primitives_by_type(self, ptype: PrimitiveType) -> list[Primitive]:
        return [p for p in self.primitives if p.primitive_type == ptype]

    def get_points(self) -> list[Point]:
        return [p for p in self.primitives if isinstance(p, Point)]

    def get_lines(self) -> list[Line]:
        return [p for p in self.primitives if isinstance(p, Line)]

    def get_circles(self) -> list[Circle]:
        return [p for p in self.primitives if isinstance(p, Circle)]

    def get_labels(self) -> list[TextLabel]:
        return [p for p in self.primitives if isinstance(p, TextLabel)]

    def get_measurements(self) -> list[Measurement]:
        return [p for p in self.primitives if isinstance(p, Measurement)]

    def primitive_count(self) -> int:
        return len(self.primitives)

    # ---- points dictionary (resolved) ------------------------------------

    def points_dict(
        self, variables: dict[str, Any] | None = None,
    ) -> dict[str, Point]:
        return {p.id: p for p in self.get_points()}

    # ---- viewbox calculation --------------------------------------------

    def compute_viewbox(
        self, variables: dict[str, Any] | None = None, padding: float = 20.0,
    ) -> BoundingBox:
        boxes: list[BoundingBox] = []
        points = self.points_dict(variables)
        for p in self.primitives:
            if isinstance(p, Point):
                boxes.append(p.bounding_box(variables))
            elif isinstance(p, Circle):
                boxes.append(p.bounding_box(variables, points))
            elif isinstance(p, Line):
                boxes.append(p.bounding_box(variables, points))
            elif isinstance(p, TextLabel):
                boxes.append(p.bounding_box(variables))
            elif isinstance(p, Rectangle):
                w = resolve_value(p.width, variables)
                h = resolve_value(p.height, variables)
                x = resolve_value(p.x, variables)
                y = resolve_value(p.y, variables)
                boxes.append(BoundingBox(float(x), float(y), float(w), float(h)))
            elif isinstance(p, Ellipse):
                rxv = resolve_value(p.rx, variables)
                ryv = resolve_value(p.ry, variables)
                pt = points.get(p.center)
                if pt:
                    cx = pt.resolved_x(variables)
                    cy = pt.resolved_y(variables)
                    boxes.append(BoundingBox(
                        cx - float(rxv), cy - float(ryv),
                        2.0 * float(rxv), 2.0 * float(ryv),
                    ))
            elif isinstance(p, Polygon):
                verts = [points.get(v) for v in p.vertices if points.get(v)]
                if verts:
                    xs = [v.resolved_x(variables) for v in verts]
                    ys = [v.resolved_y(variables) for v in verts]
                    xmin, xmax = min(xs), max(xs)
                    ymin, ymax = min(ys), max(ys)
                    boxes.append(BoundingBox(xmin, ymin, xmax - xmin, ymax - ymin))
            elif isinstance(p, TableCell):
                boxes.append(p.bounding_box())
            elif isinstance(p, Arc):
                pt = points.get(p.center)
                if pt:
                    cx = pt.resolved_x(variables)
                    cy = pt.resolved_y(variables)
                    r = float(resolve_value(p.radius, variables))
                    boxes.append(BoundingBox(cx - r, cy - r, 2.0 * r, 2.0 * r))
        result = BoundingBox.union(boxes) if boxes else BoundingBox(0, 0, 500, 400)
        return result.expanded(padding)

    # ---- serialization ---------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "metadata": self.metadata.to_dict(),
            "primitives": [p.to_dict() for p in self.primitives],
            "graph": self.graph.to_dict(),
            "bindings": self.bindings.to_dict(),
            "is_parameterized": self.is_parameterized,
            "fallback_image_path": self.fallback_image_path,
            "layout_viewbox": self.layout_viewbox.to_dict() if self.layout_viewbox else None,
        }


# ══════════════════════════════════════════════════════════════════════════
# Builder
# ══════════════════════════════════════════════════════════════════════════

class DiagramTemplateBuilder:
    """Fluent builder for constructing ``DiagramTemplate`` instances.

    Usage::

        template = (
            DiagramTemplateBuilder("tri_001", "triangle")
            .with_display_name("Right Triangle")
            .add_point(Point(id="A", x=0, y=0, label="A"))
            .add_point(Point(id="B", x=100, y=0, label="B"))
            .add_point(Point(id="C", x=0, y=80, label="C"))
            .add_line(Line(id="AB", start="A", end="B"))
            .add_line(Line(id="BC", start="B", end="C"))
            .add_line(Line(id="CA", start="C", end="A"))
            .add_polygon(Polygon(id="tri", vertices=["A", "B", "C"]))
            .add_graph_edge("A", "AB", "belongs_to")
            .add_graph_edge("B", "AB", "belongs_to")
            .add_binding("AB", "length", "a", BindingScope.GEOMETRY)
            .build()
        )
    """

    def __init__(
        self,
        template_id: str,
        diagram_type: str = DIAGRAM_TYPE_CUSTOM,
    ) -> None:
        self._metadata = TemplateMetadata(
            template_id=template_id,
            diagram_type=diagram_type,
        )
        self._primitives: list[Primitive] = []
        self._graph = DiagramGraph()
        self._bindings = VariableBindingEngine()

    # ---- metadata setters ------------------------------------------------

    def with_display_name(self, name: str) -> DiagramTemplateBuilder:
        self._metadata.display_name = name
        return self

    def with_description(self, desc: str) -> DiagramTemplateBuilder:
        self._metadata.description = desc
        return self

    def with_version(self, version: str) -> DiagramTemplateBuilder:
        self._metadata.version = version
        return self

    def with_plugin_source(self, source: str) -> DiagramTemplateBuilder:
        self._metadata.plugin_source = source
        return self

    def with_tags(self, *tags: str) -> DiagramTemplateBuilder:
        self._metadata.tags.extend(tags)
        return self

    def with_concept(self, concept: str) -> DiagramTemplateBuilder:
        self._metadata.concept = concept
        return self

    def with_subject(self, subject: str) -> DiagramTemplateBuilder:
        self._metadata.subject = subject
        return self

    def with_metadata(
        self, **kwargs: Any,
    ) -> DiagramTemplateBuilder:
        for k, v in kwargs.items():
            if hasattr(self._metadata, k):
                setattr(self._metadata, k, v)
        return self

    # ---- primitive adders ------------------------------------------------

    def add_primitive(self, primitive: Primitive) -> DiagramTemplateBuilder:
        self._primitives.append(primitive)
        return self

    def add_point(
        self, point: Point,
    ) -> DiagramTemplateBuilder:
        return self.add_primitive(point)

    def add_line(self, line: Line) -> DiagramTemplateBuilder:
        return self.add_primitive(line)

    def add_polyline(self, polyline: Polyline) -> DiagramTemplateBuilder:
        return self.add_primitive(polyline)

    def add_circle(self, circle: Circle) -> DiagramTemplateBuilder:
        return self.add_primitive(circle)

    def add_arc(self, arc: Arc) -> DiagramTemplateBuilder:
        return self.add_primitive(arc)

    def add_ellipse(self, ellipse: Ellipse) -> DiagramTemplateBuilder:
        return self.add_primitive(ellipse)

    def add_rectangle(self, rect: Rectangle) -> DiagramTemplateBuilder:
        return self.add_primitive(rect)

    def add_polygon(self, polygon: Polygon) -> DiagramTemplateBuilder:
        return self.add_primitive(polygon)

    def add_arrow(self, arrow: Arrow) -> DiagramTemplateBuilder:
        return self.add_primitive(arrow)

    def add_axis(self, axis: Axis) -> DiagramTemplateBuilder:
        return self.add_primitive(axis)

    def add_grid(self, grid: Grid) -> DiagramTemplateBuilder:
        return self.add_primitive(grid)

    def add_table_cell(self, cell: TableCell) -> DiagramTemplateBuilder:
        return self.add_primitive(cell)

    def add_text_label(self, label: TextLabel) -> DiagramTemplateBuilder:
        return self.add_primitive(label)

    def add_measurement(self, measurement: Measurement) -> DiagramTemplateBuilder:
        return self.add_primitive(measurement)

    def add_tick_mark(self, tick: TickMark) -> DiagramTemplateBuilder:
        return self.add_primitive(tick)

    # ---- graph edges -----------------------------------------------------

    def add_graph_edge(
        self, source_id: str, target_id: str, relation: str,
        metadata: dict[str, Any] | None = None,
    ) -> DiagramTemplateBuilder:
        self._graph.add_edge_str(source_id, target_id, relation, metadata)
        return self

    # ---- bindings --------------------------------------------------------

    def add_binding(
        self,
        primitive_id: str,
        property_name: str,
        variable_name: str,
        scope: BindingScope = BindingScope.CUSTOM,
        default_value: Any = None,
        description: str = "",
    ) -> DiagramTemplateBuilder:
        self._bindings.bind(
            primitive_id=primitive_id,
            property_name=property_name,
            variable_name=variable_name,
            scope=scope,
            default_value=default_value,
            description=description,
        )
        return self

    # ---- build -----------------------------------------------------------

    def build(self) -> DiagramTemplate:
        is_parameterized = self._bindings.binding_count() > 0
        return DiagramTemplate(
            metadata=self._metadata,
            primitives=list(self._primitives),
            graph=self._graph,
            bindings=self._bindings,
            is_parameterized=is_parameterized,
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
