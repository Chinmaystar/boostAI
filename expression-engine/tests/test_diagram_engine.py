from __future__ import annotations

import math

import pytest

from src.diagram_engine import (
    AnchorPosition, Arc, Arrow, Axis, BoundingBox, Circle, DiagramEdge,
    DiagramGraph, DiagramRegistry, DiagramTemplate, DiagramTemplateBuilder,
    Ellipse, FallbackDiagram, FallbackHandler, FallbackReason, FillStyle,
    FontStyle, Grid, LayoutConfig, LayoutEngine, Line, Measurement,
    Point, PointStyle, Polygon, Polyline, Rectangle, RegistryLookup,
    RelationType, RenderOptions, SVGTheme, SVGRenderer, StrokeStyle,
    TableCell, TextLabel, TickMark, VariableBinding, VariableBindingEngine,
    BindingScope, VariableRef,
)
from src.diagram_engine.diagram_template import (
    DIAGRAM_TYPE_TRIANGLE, DIAGRAM_TYPE_CIRCLE, DIAGRAM_TYPE_BAR_GRAPH,
    DIAGRAM_TYPE_VENN, DIAGRAM_TYPE_COORDINATE_GRID, DIAGRAM_TYPE_PIE_CHART,
)
from src.diagram_engine.plugin_base import (
    DiagramPlugin, DiagramPluginRegistry, PluginRegistrationError,
)
from src.diagram_engine.plugins import (
    GeometryPlugin, StatisticsPlugin, GraphsPlugin, ProbabilityPlugin,
)


# ══════════════════════════════════════════════════════════════════════════
# Primitive Creation Tests
# ══════════════════════════════════════════════════════════════════════════

class TestPrimitives:
    def test_create_point(self):
        p = Point(id="A", x=10.0, y=20.0, label="A")
        assert p.id == "A"
        assert p.x == 10.0
        assert p.y == 20.0
        assert p.label == "A"
        assert p.primitive_type.value == "point"

    def test_create_point_with_variable_ref(self):
        p = Point(id="P", x=VariableRef("a", 5), y=VariableRef("b", 10))
        assert isinstance(p.x, VariableRef)
        assert p.x.resolve({"a": 15}) == 15
        assert p.x.resolve({}) == 5

    def test_create_line(self):
        l = Line(id="AB", start="A", end="B")
        assert l.id == "AB"
        assert l.start == "A"
        assert l.end == "B"

    def test_create_circle(self):
        c = Circle(id="O", center="C", radius=50.0)
        assert c.center == "C"
        assert c.resolved_radius() == 50.0

    def test_create_circle_with_variable_radius(self):
        c = Circle(id="O", center="C", radius=VariableRef("r", 10))
        assert c.resolved_radius({"r": 25}) == 25
        assert c.resolved_radius({}) == 10

    def test_create_arc(self):
        arc = Arc(id="arc1", center="O", radius=30, start_angle=0, end_angle=90)
        assert arc.start_angle == 0
        assert arc.end_angle == 90

    def test_create_ellipse(self):
        e = Ellipse(id="el", center="C", rx=40, ry=20)
        assert e.rx == 40
        assert e.ry == 20

    def test_create_rectangle(self):
        r = Rectangle(id="rect", x=0, y=0, width=100, height=50)
        assert r.resolved_x() == 0
        assert r.resolved_width() == 100

    def test_create_polygon(self):
        poly = Polygon(id="tri", vertices=["A", "B", "C"])
        assert poly.vertices == ["A", "B", "C"]

    def test_create_arrow(self):
        a = Arrow(id="arr", start="A", end="B")
        assert a.head_size == 8.0

    def test_create_axis(self):
        ax = Axis(id="x_axis", start="O", end="X", orientation="horizontal")
        assert ax.orientation == "horizontal"

    def test_create_grid(self):
        g = Grid(id="grid", x_lines=[100, 200], y_lines=[150, 250])
        assert len(g.x_lines) == 2

    def test_create_table_cell(self):
        tc = TableCell(id="tc1", row=1, col=2, content="42")
        assert tc.content == "42"
        assert tc.row == 1
        assert tc.col == 2

    def test_create_text_label(self):
        tl = TextLabel(id="label1", x=50, y=50, text="Hello")
        assert tl.text == "Hello"
        assert tl.resolved_x() == 50

    def test_create_text_label_with_variable_position(self):
        tl = TextLabel(
            id="label1",
            x=VariableRef("px", 10),
            y=VariableRef("py", 20),
            text="Variable",
        )
        assert tl.resolved_x({"px": 100}) == 100
        assert tl.resolved_y({}) == 20

    def test_create_measurement(self):
        m = Measurement(id="m1", primitive_ref="AB", label="a")
        assert m.label == "a"
        assert m.offset == 15.0

    def test_create_tick_mark(self):
        t = TickMark(id="t1", axis_ref="x_axis", position=0.5, label="5")
        assert t.position == 0.5

    def test_stroke_style_serialization(self):
        s = StrokeStyle(color="red", width=2, dasharray="5,3")
        attrs = s.to_svg_attrs()
        assert 'stroke="red"' in attrs
        assert 'stroke-width="2"' in attrs
        assert 'stroke-dasharray="5,3"' in attrs

    def test_fill_style_serialization(self):
        f = FillStyle(color="#4A90D9", opacity=0.5)
        attrs = f.to_svg_attrs()
        assert 'fill="#4A90D9"' in attrs
        assert 'fill-opacity="0.5"' in attrs

    def test_font_style_serialization(self):
        f = FontStyle(family="Times", size=14, bold=True)
        attrs = f.to_svg_attrs()
        assert 'font-family="Times' in attrs
        assert 'font-size="14"' in attrs
        assert 'font-weight="bold"' in attrs

    def test_point_boundary_box(self):
        p = Point(id="A", x=100, y=100, style=PointStyle(radius=5))
        bb = p.bounding_box()
        assert bb.xmin == 95
        assert bb.ymin == 95
        assert bb.xmax == 105
        assert bb.ymax == 105

    def test_point_translate(self):
        p = Point(id="A", x=10, y=20)
        p.translate(5, -5)
        assert p.x == 15
        assert p.y == 15

    def test_point_translate_variable_ref_unchanged(self):
        p = Point(id="A", x=VariableRef("a"), y=VariableRef("b"))
        p.translate(10, 10)
        assert isinstance(p.x, VariableRef)

    def test_to_dict_roundtrip(self):
        p = Point(id="P1", x=10, y=20, label="P")
        d = p.to_dict()
        assert d["primitive_type"] == "point"
        assert d["id"] == "P1"
        assert d["x"] == 10
        assert d["y"] == 20

    def test_variable_ref_in_to_dict(self):
        p = Point(id="P", x=VariableRef("a"), y=10)
        d = p.to_dict()
        assert d["x"] == "a"


# ══════════════════════════════════════════════════════════════════════════
# BoundingBox Tests
# ══════════════════════════════════════════════════════════════════════════

class TestBoundingBox:
    def test_contains(self):
        bb = BoundingBox(0, 0, 100, 100)
        assert bb.contains(50, 50)
        assert not bb.contains(150, 150)
        assert bb.contains(0, 0)
        assert bb.contains(100, 100)

    def test_overlaps(self):
        bb1 = BoundingBox(0, 0, 50, 50)
        bb2 = BoundingBox(25, 25, 50, 50)
        bb3 = BoundingBox(100, 100, 50, 50)
        assert bb1.overlaps(bb2)
        assert bb2.overlaps(bb1)
        assert not bb1.overlaps(bb3)

    def test_expanded(self):
        bb = BoundingBox(10, 10, 80, 80)
        e = bb.expanded(5)
        assert e.xmin == 5
        assert e.ymin == 5
        assert e.width == 90
        assert e.height == 90

    def test_union(self):
        b1 = BoundingBox(0, 0, 10, 10)
        b2 = BoundingBox(20, 20, 10, 10)
        u = BoundingBox.union([b1, b2])
        assert u.xmin == 0
        assert u.ymin == 0
        assert u.xmax == 30
        assert u.ymax == 30

    def test_union_empty(self):
        u = BoundingBox.union([])
        assert u.width == 0
        assert u.height == 0

    def test_translate(self):
        bb = BoundingBox(10, 20, 50, 30)
        t = bb.translate(5, -5)
        assert t.xmin == 15
        assert t.ymin == 15

    def test_properties(self):
        bb = BoundingBox(10, 20, 80, 40)
        assert bb.cx == 50
        assert bb.cy == 40
        assert bb.xmax == 90
        assert bb.ymax == 60


# ══════════════════════════════════════════════════════════════════════════
# Diagram Graph Tests
# ══════════════════════════════════════════════════════════════════════════

class TestDiagramGraph:
    def test_add_edge(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        assert g.edge_count() == 1

    def test_add_edge_str(self):
        g = DiagramGraph()
        g.add_edge_str("A", "B", "connects")
        assert g.edge_count() == 1

    def test_get_outgoing(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        g.add_edge("A", "C", RelationType.BELONGS_TO)
        outgoing = g.get_outgoing("A")
        assert len(outgoing) == 2

    def test_get_incoming(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        g.add_edge("C", "B", RelationType.BELONGS_TO)
        incoming = g.get_incoming("B")
        assert len(incoming) == 2

    def test_get_relations(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        g.add_edge("A", "C", RelationType.BELONGS_TO)
        rels = g.get_relations("A", RelationType.CONNECTS)
        assert len(rels) == 1
        assert rels[0].target_id == "B"

    def test_get_related(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        related = g.get_related("A", RelationType.CONNECTS)
        assert related == ["B"]

    def test_get_related_by_any(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        related = g.get_related_by_any("B")
        assert len(related) >= 1

    def test_has_path(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        g.add_edge("B", "C", RelationType.CONNECTS)
        assert g.has_path("A", "C")
        assert not g.has_path("A", "D")

    def test_node_metadata(self):
        g = DiagramGraph()
        g.set_metadata("A", color="red", weight=5)
        assert g.get_metadata("A")["color"] == "red"
        assert g.get_metadata("A")["weight"] == 5

    def test_roots(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        g.add_edge("B", "C", RelationType.CONNECTS)
        assert "A" in g.roots()
        assert "B" not in g.roots()

    def test_all_nodes(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        assert g.all_nodes() == {"A", "B"}

    def test_clear(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        g.clear()
        assert g.edge_count() == 0

    def test_edge_metadata(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS, metadata={"label": "AB"})
        edges = g.get_edges()
        assert edges[0].metadata == {"label": "AB"}

    def test_to_dict(self):
        g = DiagramGraph()
        g.add_edge("A", "B", RelationType.CONNECTS)
        d = g.to_dict()
        assert "edges" in d
        assert "roots" in d

    def test_belongs_to_relation(self):
        g = DiagramGraph()
        g.add_edge("A", "tri", RelationType.BELONGS_TO)
        g.add_edge("B", "tri", RelationType.BELONGS_TO)
        assert len(g.get_relations("A", RelationType.BELONGS_TO)) == 1


# ══════════════════════════════════════════════════════════════════════════
# Variable Binding Engine Tests
# ══════════════════════════════════════════════════════════════════════════

class TestVariableBindingEngine:
    def test_bind_and_get(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a", BindingScope.GEOMETRY)
        b = eng.get_binding("AB", "length")
        assert b is not None
        assert b.variable_name == "a"
        assert b.scope == BindingScope.GEOMETRY

    def test_bind_returns_binding(self):
        eng = VariableBindingEngine()
        b = eng.bind("O", "radius", "r", BindingScope.RADIUS)
        assert b.binding_key() == "O.radius"

    def test_unbind(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        eng.unbind("AB", "length")
        assert eng.get_binding("AB", "length") is None

    def test_unbind_all_for_primitive(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        eng.bind("AB", "angle", "theta")
        eng.unbind_all_for_primitive("AB")
        assert eng.binding_count() == 0

    def test_get_bindings_for_primitive(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        eng.bind("BC", "length", "b")
        assert len(eng.get_bindings_for_primitive("AB")) == 1

    def test_get_bindings_by_scope(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a", BindingScope.GEOMETRY)
        eng.bind("O", "radius", "r", BindingScope.RADIUS)
        geo = eng.get_bindings_by_scope(BindingScope.GEOMETRY)
        rad = eng.get_bindings_by_scope(BindingScope.RADIUS)
        assert len(geo) == 1
        assert len(rad) == 1

    def test_resolve_with_variables(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a", default_value=5)
        assert eng.resolve("AB", "length", {"a": 10}) == 10

    def test_resolve_default(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a", default_value=5)
        assert eng.resolve("AB", "length") == 5

    def test_resolve_nonexistent(self):
        eng = VariableBindingEngine()
        assert eng.resolve("NONEXISTENT", "prop") is None

    def test_has_binding(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        assert eng.has_binding("AB", "length")
        assert not eng.has_binding("AB", "width")

    def test_get_all_bindings(self):
        eng = VariableBindingEngine()
        eng.bind("A", "x", "ax")
        eng.bind("A", "y", "ay")
        assert len(eng.get_all_bindings()) == 2

    def test_get_variable_names(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        eng.bind("BC", "length", "b")
        eng.bind("AB", "angle", "theta")
        names = eng.get_variable_names()
        assert "a" in names
        assert "b" in names
        assert "theta" in names

    def test_resolve_all(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a", default_value=5)
        eng.bind("BC", "length", "b", default_value=10)
        r = eng.resolve_all({"a": 7})
        assert r["AB.length"] == 7
        assert r["BC.length"] == 10

    def test_clear(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        eng.clear()
        assert eng.binding_count() == 0

    def test_to_dict(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a")
        d = eng.to_dict()
        assert "bindings" in d
        assert "variable_names" in d


# ══════════════════════════════════════════════════════════════════════════
# DiagramTemplate & Builder Tests
# ══════════════════════════════════════════════════════════════════════════

class TestDiagramTemplateBuilder:
    def test_build_empty_template(self):
        builder = DiagramTemplateBuilder("test_001", "triangle")
        template = builder.build()
        assert template.metadata.template_id == "test_001"
        assert template.metadata.diagram_type == "triangle"
        assert not template.is_parameterized

    def test_build_with_points_and_lines(self):
        builder = DiagramTemplateBuilder("tri_001", "triangle")
        builder.add_point(Point(id="A", x=0, y=0, label="A"))
        builder.add_point(Point(id="B", x=100, y=0, label="B"))
        builder.add_point(Point(id="C", x=50, y=80, label="C"))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_line(Line(id="BC", start="B", end="C"))
        builder.add_line(Line(id="CA", start="C", end="A"))
        template = builder.build()
        assert template.primitive_count() == 6
        assert len(template.get_points()) == 3
        assert len(template.get_lines()) == 3

    def test_build_with_variable_binding(self):
        builder = DiagramTemplateBuilder("tri_bind", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_binding("AB", "length", "a", BindingScope.GEOMETRY)
        template = builder.build()
        assert template.is_parameterized
        assert template.bindings.binding_count() == 1

    def test_build_with_graph_edges(self):
        builder = DiagramTemplateBuilder("graph_test", "polygon")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_graph_edge("A", "AB", "belongs_to")
        builder.add_graph_edge("B", "AB", "belongs_to")
        template = builder.build()
        assert template.graph.edge_count() == 2

    def test_get_primitive(self):
        builder = DiagramTemplateBuilder("test", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        template = builder.build()
        p = template.get_primitive("A")
        assert p is not None
        assert p.id == "A"

    def test_get_primitive_not_found(self):
        builder = DiagramTemplateBuilder("test", "triangle")
        template = builder.build()
        assert template.get_primitive("NONEXISTENT") is None

    def test_get_primitives_by_type(self):
        from src.diagram_engine.primitives import PrimitiveType
        builder = DiagramTemplateBuilder("test", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_line(Line(id="AB", start="A", end="B"))
        template = builder.build()
        pts = template.get_primitives_by_type(PrimitiveType.POINT)
        assert len(pts) == 1

    def test_metadata_defaults(self):
        builder = DiagramTemplateBuilder("t1", "circle")
        builder.with_display_name("Test Circle")
        builder.with_description("A circle diagram")
        builder.with_tags("circle", "geometry")
        builder.with_concept("Circle Properties")
        template = builder.build()
        assert template.metadata.display_name == "Test Circle"
        assert template.metadata.diagram_type == "circle"
        assert "circle" in template.metadata.tags

    def test_compute_viewbox(self):
        builder = DiagramTemplateBuilder("vb", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_point(Point(id="C", x=50, y=80))
        template = builder.build()
        vb = template.compute_viewbox()
        assert vb.xmin <= 0
        assert vb.ymin <= 0
        assert vb.xmax >= 100
        assert vb.ymax >= 80

    def test_polygon_primitive(self):
        from src.diagram_engine.primitives import PrimitiveType
        builder = DiagramTemplateBuilder("poly", "polygon")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_point(Point(id="C", x=50, y=80))
        builder.add_polygon(Polygon(id="tri", vertices=["A", "B", "C"]))
        template = builder.build()
        assert len(template.get_primitives_by_type(PrimitiveType.POLYGON)) >= 1

    def test_fluent_interface(self):
        builder = (
            DiagramTemplateBuilder("fluent", "triangle")
            .with_display_name("Right Triangle")
            .with_tags("geometry", "right-angle")
            .add_point(Point(id="A", x=0, y=0))
            .add_point(Point(id="B", x=100, y=0))
            .add_point(Point(id="C", x=0, y=80))
            .add_line(Line(id="AB", start="A", end="B"))
            .add_line(Line(id="BC", start="B", end="C"))
            .add_line(Line(id="CA", start="C", end="A"))
        )
        template = builder.build()
        assert template.primitive_count() == 6

    def test_to_dict(self):
        builder = DiagramTemplateBuilder("d", "circle")
        builder.add_point(Point(id="O", x=0, y=0))
        template = builder.build()
        d = template.to_dict()
        assert d["metadata"]["template_id"] == "d"
        assert "primitives" in d

    def test_points_dict(self):
        builder = DiagramTemplateBuilder("pd", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        template = builder.build()
        pts = template.points_dict()
        assert "A" in pts


# ══════════════════════════════════════════════════════════════════════════
# SVG Renderer Tests
# ══════════════════════════════════════════════════════════════════════════

class TestSVGRenderer:
    def test_render_empty_template(self):
        template = DiagramTemplateBuilder("empty", "custom").build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'data-diagram-id="empty"' in svg

    def test_render_triangle(self):
        builder = DiagramTemplateBuilder("tri_svg", "triangle")
        builder.add_point(Point(id="A", x=0, y=0, label="A"))
        builder.add_point(Point(id="B", x=100, y=0, label="B"))
        builder.add_point(Point(id="C", x=50, y=80, label="C"))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_line(Line(id="BC", start="B", end="C"))
        builder.add_line(Line(id="CA", start="C", end="A"))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'x1="0.0"' in svg
        assert 'x2="100.0"' in svg or 'x2="100"' in svg
        assert "data-primitive-id=\"A\"" in svg
        assert "data-primitive-id=\"AB\"" in svg

    def test_render_circle(self):
        builder = DiagramTemplateBuilder("circle_svg", "circle")
        builder.add_point(Point(id="O", x=100, y=100))
        builder.add_circle(Circle(
            id="C1", center="O", radius=50,
            stroke=StrokeStyle(),
        ))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'cx="100.0"' in svg
        assert 'cy="100.0"' in svg
        assert 'r="50.0"' in svg or 'r="50"' in svg

    def test_render_rectangle(self):
        builder = DiagramTemplateBuilder("rect_svg", "custom")
        builder.add_rectangle(Rectangle(
            id="R1", x=10, y=20, width=200, height=100,
            fill=FillStyle(color="#4A90D9"),
        ))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'x="10.0"' in svg
        assert 'y="20.0"' in svg
        assert 'width="200.0"' in svg
        assert 'height="100.0"' in svg

    def test_render_text_label(self):
        builder = DiagramTemplateBuilder("label_svg", "custom")
        builder.add_text_label(TextLabel(id="T1", x=50, y=50, text="Hello"))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert "Hello" in svg

    def test_render_arrow(self):
        builder = DiagramTemplateBuilder("arrow_svg", "custom")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_arrow(Arrow(id="Ar1", start="A", end="B"))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert "polygon" in svg

    def test_render_with_variable_data_attributes(self):
        builder = DiagramTemplateBuilder("var_svg", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_binding("AB", "length", "a", BindingScope.GEOMETRY)
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'data-var-length="a"' in svg

    def test_deterministic_output(self):
        builder = DiagramTemplateBuilder("det", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_line(Line(id="AB", start="A", end="B"))
        template = builder.build()
        renderer = SVGRenderer()
        svg1 = renderer.render(template)
        svg2 = renderer.render(template)
        assert svg1 == svg2

    def test_responsive_viewbox(self):
        template = DiagramTemplateBuilder("resp", "custom").build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'viewBox="' in svg
        assert 'width="100%"' in svg

    def test_layered_output(self):
        builder = DiagramTemplateBuilder("layered", "custom")
        builder.add_point(Point(id="A", x=0, y=0))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert "data-layer=\"background\"" in svg
        assert "data-layer=\"point\"" in svg

    def test_custom_theme(self):
        theme = SVGTheme(background_color="#f0f0f0")
        options = RenderOptions(theme=theme)
        template = DiagramTemplateBuilder("theme", "custom").build()
        renderer = SVGRenderer(options)
        svg = renderer.render(template)
        assert 'background:#f0f0f0' in svg

    def test_render_ellipse(self):
        builder = DiagramTemplateBuilder("ellipse_svg", "custom")
        builder.add_point(Point(id="C", x=100, y=100))
        builder.add_ellipse(Ellipse(
            id="E1", center="C", rx=60, ry=30,
            stroke=StrokeStyle(),
        ))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'rx="60"' in svg or 'rx="60.0"' in svg
        assert 'ry="30"' in svg or 'ry="30.0"' in svg

    def test_render_grid(self):
        builder = DiagramTemplateBuilder("grid_svg", "custom")
        builder.add_point(Point(id="O", x=0, y=0))
        builder.add_grid(Grid(id="G1", x_lines=[50, 100], y_lines=[50, 100]))
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert 'x1="50"' in svg
        assert 'y1="50"' in svg


# ══════════════════════════════════════════════════════════════════════════
# Layout Engine Tests
# ══════════════════════════════════════════════════════════════════════════

class TestLayoutEngine:
    def test_layout_no_labels(self):
        builder = DiagramTemplateBuilder("no_labels", "custom")
        builder.add_point(Point(id="A", x=0, y=0))
        template = builder.build()
        engine = LayoutEngine()
        result = engine.layout(template)
        assert result.converged
        assert result.total_overlaps_resolved == 0

    def test_layout_with_labels(self):
        builder = DiagramTemplateBuilder("with_labels", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_text_label(TextLabel(id="L1", x=10, y=10, text="Label A"))
        builder.add_text_label(TextLabel(id="L2", x=15, y=15, text="Label B"))
        template = builder.build()
        engine = LayoutEngine(config=LayoutConfig(max_iterations=5))
        result = engine.layout(template)
        assert result.total_overlaps_resolved >= 0

    def test_non_overlapping_labels(self):
        builder = DiagramTemplateBuilder("non_overlap", "custom")
        builder.add_text_label(TextLabel(id="L1", x=0, y=0, text="Left"))
        builder.add_text_label(TextLabel(id="L2", x=200, y=200, text="Right"))
        template = builder.build()
        engine = LayoutEngine()
        result = engine.layout(template)
        assert result.converged

    def test_config_defaults(self):
        config = LayoutConfig()
        assert config.max_iterations == 20
        assert config.repulsion_strength == 2.0
        assert config.min_distance == 8.0

    def test_point_labels_included(self):
        builder = DiagramTemplateBuilder("pt_labels", "triangle")
        builder.add_point(Point(id="A", x=100, y=100, label="A"))
        template = builder.build()
        engine = LayoutEngine()
        result = engine.layout(template)
        assert result.converged


# ══════════════════════════════════════════════════════════════════════════
# Diagram Registry Tests
# ══════════════════════════════════════════════════════════════════════════

class TestDiagramRegistry:
    def test_register_and_get(self):
        registry = DiagramRegistry()
        template = DiagramTemplateBuilder("reg_001", "triangle").build()
        tid = registry.register(template)
        assert tid == "reg_001"
        assert registry.get("reg_001") is not None

    def test_register_duplicate_raises(self):
        registry = DiagramRegistry()
        registry.register(DiagramTemplateBuilder("dup", "circle").build())
        with pytest.raises(ValueError):
            registry.register(DiagramTemplateBuilder("dup", "circle").build())

    def test_register_with_tags(self):
        registry = DiagramRegistry()
        template = DiagramTemplateBuilder("tagged", "triangle").build()
        registry.register(template, tags=["geometry", "triangle"], concept="Triangles")
        entry = registry.get_entry("tagged")
        assert entry is not None
        assert "geometry" in entry.tags
        assert entry.concept == "Triangles"

    def test_unregister(self):
        registry = DiagramRegistry()
        registry.register(DiagramTemplateBuilder("del", "circle").build())
        registry.unregister("del")
        assert registry.get("del") is None

    def test_unregister_not_found_raises(self):
        registry = DiagramRegistry()
        with pytest.raises(KeyError):
            registry.unregister("nonexistent")

    def test_find_by_type(self):
        registry = DiagramRegistry()
        registry.register(
            DiagramTemplateBuilder("t1", "triangle").build(),
            tags=["triangle"],
        )
        registry.register(
            DiagramTemplateBuilder("c1", "circle").build(),
            tags=["circle"],
        )
        triangles = registry.find_by_type("triangle")
        assert len(triangles) == 1
        circles = registry.find_by_type("circle")
        assert len(circles) == 1

    def test_find_by_concept(self):
        registry = DiagramRegistry()
        registry.register(
            DiagramTemplateBuilder("t1", "triangle").build(),
            concept="Triangles",
        )
        registry.register(
            DiagramTemplateBuilder("c1", "circle").build(),
            concept="Circles",
        )
        found = registry.find_by_concept("triangle")
        assert len(found) >= 1

    def test_find_by_tag(self):
        registry = DiagramRegistry()
        registry.register(
            DiagramTemplateBuilder("t1", "triangle").build(),
            tags=["geometry", "triangle"],
        )
        found = registry.find_by_tag("geometry")
        assert len(found) == 1
        assert registry.find_by_tag("nonexistent") == []

    def test_find_with_lookup(self):
        registry = DiagramRegistry()
        registry.register(
            DiagramTemplateBuilder("t1", "triangle").build(),
            tags=["geometry"],
            concept="Triangles",
        )
        query = RegistryLookup(diagram_type="triangle")
        results = registry.find(query)
        assert len(results) == 1

    def test_list_ids(self):
        registry = DiagramRegistry()
        registry.register(DiagramTemplateBuilder("a", "triangle").build())
        registry.register(DiagramTemplateBuilder("b", "circle").build())
        ids = registry.list_ids()
        assert len(ids) == 2

    def test_list_types(self):
        registry = DiagramRegistry()
        registry.register(
            DiagramTemplateBuilder("t1", "triangle").build(),
        )
        registry.register(
            DiagramTemplateBuilder("c1", "circle").build(),
        )
        types = registry.list_types()
        assert "triangle" in types
        assert "circle" in types

    def test_count(self):
        registry = DiagramRegistry()
        assert registry.count() == 0
        registry.register(DiagramTemplateBuilder("a", "triangle").build())
        assert registry.count() == 1

    def test_to_dict(self):
        registry = DiagramRegistry()
        registry.register(DiagramTemplateBuilder("a", "triangle").build())
        d = registry.to_dict()
        assert d["count"] == 1
        assert "triangle" in d["types"]

    def test_clear(self):
        registry = DiagramRegistry()
        registry.register(DiagramTemplateBuilder("a", "triangle").build())
        registry.clear()
        assert registry.count() == 0

    def test_allow_overwrite(self):
        registry = DiagramRegistry()
        registry.register(DiagramTemplateBuilder("a", "triangle").build())
        registry.register(
            DiagramTemplateBuilder("a", "circle").build(),
            allow_overwrite=True,
        )
        t = registry.get("a")
        assert t is not None
        assert t.metadata.diagram_type == "circle"


# ══════════════════════════════════════════════════════════════════════════
# Plugin System Tests
# ══════════════════════════════════════════════════════════════════════════

class TestDiagramPlugin:
    def test_geometry_plugin_properties(self):
        plugin = GeometryPlugin()
        assert plugin.plugin_name == "geometry"
        assert "triangle" in plugin.supported_diagram_types

    def test_statistics_plugin_properties(self):
        plugin = StatisticsPlugin()
        assert plugin.plugin_name == "statistics"

    def test_probability_plugin_properties(self):
        plugin = ProbabilityPlugin()
        assert plugin.plugin_name == "probability"

    def test_graphs_plugin_properties(self):
        plugin = GraphsPlugin()
        assert plugin.plugin_name == "graphs"

    def test_geometry_can_handle(self):
        plugin = GeometryPlugin()
        assert plugin.can_handle_input({"figure_type": "triangle"})
        assert plugin.can_handle_input({"figure_type": "circle"})
        assert plugin.can_handle_input({"figure_type": "polygon"})
        assert not plugin.can_handle_input({"figure_type": "bar_chart"})

    def test_statistics_can_handle(self):
        plugin = StatisticsPlugin()
        assert plugin.can_handle_input({"figure_type": "bar_chart"})
        assert plugin.can_handle_input({"figure_type": "pie_chart"})
        assert plugin.can_handle_input({"figure_type": "histogram"})
        assert not plugin.can_handle_input({"figure_type": "triangle"})

    def test_probability_can_handle(self):
        plugin = ProbabilityPlugin()
        assert plugin.can_handle_input({"figure_type": "venn"})
        assert plugin.can_handle_input({"figure_type": "tree"})

    def test_graphs_can_handle(self):
        plugin = GraphsPlugin()
        assert plugin.can_handle_input({"figure_type": "coordinate_grid"})
        assert plugin.can_handle_input({"figure_type": "cartesian_graph"})


class TestDiagramPluginRegistry:
    def test_register_plugin(self):
        registry = DiagramPluginRegistry()
        plugin = GeometryPlugin()
        registry.register(plugin)
        assert registry.has("geometry")

    def test_register_duplicate(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        with pytest.raises(PluginRegistrationError):
            registry.register(GeometryPlugin())

    def test_get_plugin(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        p = registry.get("geometry")
        assert p is not None
        assert p.plugin_name == "geometry"

    def test_get_nonexistent(self):
        registry = DiagramPluginRegistry()
        assert registry.get("nonexistent") is None

    def test_get_for_input(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        registry.register(StatisticsPlugin())
        p = registry.get_for_input({"figure_type": "triangle"})
        assert p is not None
        assert p.plugin_name == "geometry"
        p2 = registry.get_for_input({"figure_type": "bar_chart"})
        assert p2 is not None
        assert p2.plugin_name == "statistics"

    def test_get_for_type(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        p = registry.get_for_type("triangle")
        assert p is not None

    def test_get_for_type_not_found(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        assert registry.get_for_type("unknown_type") is None

    def test_unregister(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        registry.unregister("geometry")
        assert not registry.has("geometry")

    def test_list_plugins(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        registry.register(StatisticsPlugin())
        names = registry.list_plugins()
        assert "geometry" in names
        assert "statistics" in names

    def test_clear(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        registry.clear()
        assert registry.count == 0

    def test_count_property(self):
        registry = DiagramPluginRegistry()
        assert registry.count == 0
        registry.register(GeometryPlugin())
        assert registry.count == 1


# ══════════════════════════════════════════════════════════════════════════
# Fallback Behaviour Tests
# ══════════════════════════════════════════════════════════════════════════

class TestFallbackHandler:
    def test_create_fallback_template(self):
        handler = FallbackHandler()
        template = handler.create_fallback_template(
            template_id="fallback_001",
            reason=FallbackReason.NO_VECTOR_DATA,
            message="No vector primitives found",
            image_path="diagrams/fallback_001.png",
        )
        assert not template.is_parameterized
        assert template.fallback_image_path == "diagrams/fallback_001.png"
        assert template.metadata.template_id == "fallback_001"

    def test_get_fallback(self):
        handler = FallbackHandler()
        handler.create_fallback_template(
            "fb1", FallbackReason.UNSUPPORTED_DIAGRAM_TYPE,
            "Unsupported type",
        )
        fb = handler.get_fallback("fb1")
        assert fb is not None
        assert fb.reason == FallbackReason.UNSUPPORTED_DIAGRAM_TYPE

    def test_get_nonexistent_fallback(self):
        handler = FallbackHandler()
        assert handler.get_fallback("nonexistent") is None

    def test_list_fallbacks(self):
        handler = FallbackHandler()
        handler.create_fallback_template(
            "fb1", FallbackReason.NO_VECTOR_DATA, "No data",
        )
        handler.create_fallback_template(
            "fb2", FallbackReason.CORRUPTED_DATA, "Corrupted",
        )
        assert len(handler.list_fallbacks()) == 2

    def test_fallback_reason_values(self):
        assert FallbackReason.NO_VECTOR_DATA.value == "no_vector_data"
        assert FallbackReason.UNSUPPORTED_DIAGRAM_TYPE.value == "unsupported_diagram_type"

    def test_fallback_reason_plugin_not_found(self):
        handler = FallbackHandler()
        template = handler.create_fallback_template(
            "no_plugin", FallbackReason.PLUGIN_NOT_FOUND,
            "No plugin available",
        )
        assert template.metadata.plugin_source == "fallback_handler"

    def test_clear_fallbacks(self):
        handler = FallbackHandler()
        handler.create_fallback_template("fb1", FallbackReason.UNKNOWN, "?")
        handler.clear()
        assert len(handler.list_fallbacks()) == 0


# ══════════════════════════════════════════════════════════════════════════
# Built-in Plugin Template Building Tests
# ══════════════════════════════════════════════════════════════════════════

class TestGeometryPluginBuild:
    def test_build_triangle_template(self):
        plugin = GeometryPlugin()
        template = plugin.build_template({
            "id": "tri_test",
            "figure_type": "triangle",
            "points": [
                {"id": "A", "x": 0, "y": 0, "name": "A", "label": "A"},
                {"id": "B", "x": 100, "y": 0, "name": "B", "label": "B"},
                {"id": "C", "x": 50, "y": 80, "name": "C", "label": "C"},
            ],
            "lines": [
                {"id": "AB", "start": "A", "end": "B"},
                {"id": "BC", "start": "B", "end": "C"},
                {"id": "CA", "start": "C", "end": "A"},
            ],
        })
        assert template.metadata.template_id == "tri_test"
        assert template.primitive_count() >= 6

    def test_build_with_variable_bindings(self):
        plugin = GeometryPlugin()
        template = plugin.build_template({
            "id": "tri_var",
            "figure_type": "triangle",
            "points": [
                {"id": "A", "x": 0, "y": 0, "name": "A"},
                {"id": "B", "x": 100, "y": 0, "name": "B"},
            ],
            "lines": [
                {"id": "AB", "start": "A", "end": "B",
                 "variable": "a", "default_value": 5},
            ],
        })
        assert template.is_parameterized
        assert template.bindings.has_binding("AB", "length")

    def test_build_circle_template(self):
        plugin = GeometryPlugin()
        template = plugin.build_template({
            "id": "circle_test",
            "figure_type": "circle",
            "points": [{"id": "O", "x": 100, "y": 100, "name": "O"}],
            "circles": [{"id": "C1", "center": "O", "radius": 50}],
        })
        circles = [c for c in template.primitives if hasattr(c, 'center') and hasattr(c, 'radius')]
        assert len(circles) >= 1


class TestStatisticsPluginBuild:
    def test_build_bar_graph(self):
        plugin = StatisticsPlugin()
        template = plugin.build_template({
            "id": "bar_test",
            "figure_type": "bar_chart",
            "categories": ["A", "B", "C"],
            "data_points": [
                {"label": "A", "value": 30},
                {"label": "B", "value": 50},
                {"label": "C", "value": 20},
            ],
        })
        assert template.primitive_count() >= 3
        assert template.metadata.template_id == "bar_test"

    def test_build_pie_chart(self):
        plugin = StatisticsPlugin()
        template = plugin.build_template({
            "id": "pie_test",
            "figure_type": "pie_chart",
            "data_points": [
                {"label": "A", "value": 30},
                {"label": "B", "value": 50},
                {"label": "C", "value": 20},
            ],
        })
        assert template.primitive_count() > 0


class TestProbabilityPluginBuild:
    def test_build_venn_diagram(self):
        plugin = ProbabilityPlugin()
        template = plugin.build_template({
            "id": "venn_test",
            "figure_type": "venn",
            "sets": [
                {"label": "A"},
                {"label": "B"},
            ],
        })
        circles = [p for p in template.primitives if hasattr(p, 'radius')]
        assert len(circles) == 2

    def test_build_tree_diagram(self):
        plugin = ProbabilityPlugin()
        template = plugin.build_template({
            "id": "tree_test",
            "figure_type": "tree",
            "nodes": [
                {"id": "root", "x": 200, "y": 50, "label": "Start"},
                {"id": "a", "x": 100, "y": 150, "label": "A", "probability": 0.5},
                {"id": "b", "x": 300, "y": 150, "label": "B", "probability": 0.5},
            ],
            "edges": [
                {"source": "root", "target": "a", "label": "0.5"},
                {"source": "root", "target": "b", "label": "0.5"},
            ],
        })
        assert template.primitive_count() > 0


class TestGraphsPluginBuild:
    def test_build_coordinate_grid(self):
        plugin = GraphsPlugin()
        template = plugin.build_template({
            "id": "grid_test",
            "figure_type": "coordinate_grid",
            "grid": {
                "x_min": -10, "x_max": 10,
                "y_min": -10, "y_max": 10,
                "origin_x": 250, "origin_y": 250,
                "scale": 20,
            },
        })
        assert template.primitive_count() > 0

    def test_build_with_points_and_lines(self):
        plugin = GraphsPlugin()
        template = plugin.build_template({
            "id": "graph_test",
            "figure_type": "coordinate_grid",
            "grid": {
                "x_min": 0, "x_max": 10,
                "y_min": 0, "y_max": 10,
                "origin_x": 50, "origin_y": 300,
                "scale": 25,
            },
            "lines": [
                {"id": "line1", "x1": 0, "y1": 0, "x2": 10, "y2": 10},
            ],
            "points": [
                {"id": "p1", "x": 5, "y": 5, "label": "(5,5)"},
            ],
        })
        assert template.primitive_count() > 0


# ══════════════════════════════════════════════════════════════════════════
# Edge Cases
# ══════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_empty_template(self):
        template = DiagramTemplateBuilder("empty", "custom").build()
        assert template.primitive_count() == 0
        assert not template.is_parameterized

    def test_missing_point_references(self):
        builder = DiagramTemplateBuilder("missing", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_line(Line(id="AB", start="A", end="B"))  # B doesn't exist
        template = builder.build()
        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert svg is not None

    def test_zero_values(self):
        p = Point(id="Z", x=0, y=0)
        assert p.resolved_x() == 0
        assert p.resolved_y() == 0

    def test_negative_coordinates(self):
        p = Point(id="N", x=-50, y=-50)
        bb = p.bounding_box()
        assert bb.xmin == -53
        assert bb.ymin == -53

    def test_large_values(self):
        p = Point(id="L", x=10000, y=10000)
        renderer = SVGRenderer()
        builder = DiagramTemplateBuilder("large", "custom")
        builder.add_point(p)
        template = builder.build()
        svg = renderer.render(template)
        assert "10000" in svg

    def test_special_characters_in_labels(self):
        tl = TextLabel(id="sp", x=0, y=0, text="x < y & z > 1")
        renderer = SVGRenderer()
        builder = DiagramTemplateBuilder("special", "custom")
        builder.add_text_label(tl)
        template = builder.build()
        svg = renderer.render(template)
        assert "&lt;" in svg
        assert "&gt;" in svg
        assert "&amp;" in svg

    def test_multiple_primitive_types(self):
        builder = DiagramTemplateBuilder("multi", "custom")
        builder.add_point(Point(id="P", x=0, y=0))
        builder.add_line(Line(id="L", start="P", end="Q"))
        builder.add_circle(Circle(id="C", center="P", radius=10))
        builder.add_rectangle(Rectangle(id="R", x=0, y=0, width=10, height=10))
        builder.add_text_label(TextLabel(id="T", x=5, y=5, text="Test"))
        template = builder.build()
        assert template.primitive_count() == 5

    def test_variable_ref_default_none(self):
        vr = VariableRef("x")
        assert vr.resolve({}) is None
        assert vr.resolve({"x": 42}) == 42

    def test_binding_with_empty_variable_dict(self):
        eng = VariableBindingEngine()
        eng.bind("AB", "length", "a", default_value=5)
        assert eng.resolve("AB", "length", {}) == 5
        assert eng.resolve("AB", "length", {"a": 10}) == 10

    def test_registry_lookup_empty_result(self):
        registry = DiagramRegistry()
        query = RegistryLookup(diagram_type="nonexistent")
        assert registry.find(query) == []


# ══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ══════════════════════════════════════════════════════════════════════════

class TestIntegration:
    def test_build_render_roundtrip(self):
        builder = DiagramTemplateBuilder("roundtrip", "triangle")
        builder.add_point(Point(id="A", x=0, y=0, label="A"))
        builder.add_point(Point(id="B", x=100, y=0, label="B"))
        builder.add_point(Point(id="C", x=50, y=80, label="C"))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_line(Line(id="BC", start="B", end="C"))
        builder.add_line(Line(id="CA", start="C", end="A"))
        builder.add_binding("AB", "length", "a")
        template = builder.build()

        renderer = SVGRenderer()
        svg = renderer.render(template)
        assert svg is not None
        assert "data-var-length" in svg
        assert template.is_parameterized

    def test_plugin_detection_and_build(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        registry.register(StatisticsPlugin())

        input_data = {"figure_type": "triangle", "id": "detect_test"}
        plugin = registry.get_for_input(input_data)
        assert plugin is not None

        template = plugin.build_template(input_data)
        assert template.metadata.template_id == "detect_test"

    def test_full_pipeline_with_registry(self):
        diagram_registry = DiagramRegistry()

        builder = DiagramTemplateBuilder("pipeline_test", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=100, y=0))
        builder.add_point(Point(id="C", x=50, y=80))
        builder.add_line(Line(id="AB", start="A", end="B"))
        builder.add_polygon(Polygon(id="tri", vertices=["A", "B", "C"]))

        template = builder.build()
        diagram_registry.register(
            template,
            tags=["geometry", "triangle"],
            concept="Triangles",
        )

        found = diagram_registry.find_by_tag("geometry")
        assert len(found) == 1

        renderer = SVGRenderer()
        svg = renderer.render(found[0])
        assert "data-primitive-id" in svg

    def test_parameterized_render_with_variables(self):
        builder = DiagramTemplateBuilder("param_render", "triangle")
        builder.add_point(Point(id="A", x=0, y=0))
        builder.add_point(Point(id="B", x=VariableRef("base", 100), y=0))
        builder.add_point(Point(id="C", x=50, y=VariableRef("height", 80)))
        builder.add_line(Line(id="AB", start="A", end="B"))
        template = builder.build()

        renderer = SVGRenderer()
        svg_default = renderer.render(template)
        svg_custom = renderer.render(template, {"base": 200, "height": 160})

        assert svg_default != svg_custom
        assert 'x2="200.0"' in svg_custom
        assert 'cy="160.0"' in svg_custom

    def test_multiple_plugins_in_registry(self):
        registry = DiagramPluginRegistry()
        registry.register(GeometryPlugin())
        registry.register(StatisticsPlugin())
        registry.register(ProbabilityPlugin())
        registry.register(GraphsPlugin())
        assert registry.count == 4

        for input_type in ["triangle", "bar_chart", "venn", "coordinate_grid"]:
            plugin = registry.get_for_input({"figure_type": input_type})
            assert plugin is not None, f"No plugin for {input_type}"
