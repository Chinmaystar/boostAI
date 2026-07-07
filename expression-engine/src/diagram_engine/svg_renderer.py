from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

from .diagram_template import DiagramTemplate, Primitive
from .primitives import (
    AnchorPosition, Arc, Arrow, Axis, BoundingBox, Circle, Ellipse,
    FillStyle, FontStyle, Grid, Line, Measurement, Point, PointStyle,
    Polygon, Polyline, Rectangle, StrokeStyle, TableCell, TextLabel,
    TickMark, VariableRef, resolve_value,
)


@dataclass
class SVGTheme:
    """Styling constants for the SVG output."""
    background_color: str = "#ffffff"
    default_stroke: str = "#000000"
    default_stroke_width: float = 1.5
    default_font_family: str = "Arial, sans-serif"
    default_font_size: float = 12.0
    default_font_color: str = "#000000"
    grid_color: str = "#e0e0e0"
    grid_stroke_width: float = 0.5
    axis_color: str = "#333333"
    axis_stroke_width: float = 1.5
    measurement_color: str = "#555555"
    measurement_font_size: float = 10.0
    angle_arc_color: str = "#888888"
    point_fill: str = "#000000"
    point_radius: float = 3.0
    arrow_head_size: float = 8.0
    padding: float = 20.0

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class RenderOptions:
    """Options that control SVG rendering behaviour."""
    width: Optional[str] = None
    height: Optional[str] = None
    responsive: bool = True
    inline_styles: bool = True
    include_data_attributes: bool = True
    extract_text: bool = True
    layer_separators: bool = True
    compact: bool = False
    theme: SVGTheme = field(default_factory=SVGTheme)

    def viewbox_width(self, bounds: BoundingBox) -> str:
        if self.width:
            return self.width
        if self.responsive:
            return "100%"
        return str(bounds.width)

    def viewbox_height(self, bounds: BoundingBox) -> str:
        if self.height:
            return self.height
        if self.responsive:
            return "100%"
        return str(bounds.height)


class SVGRenderer:
    """Generates clean, deterministic SVG from diagram primitives.

    The renderer is purely a view — it never modifies primitives or
    template state.  It accepts a ``DiagramTemplate`` (with optional
    concrete variable assignments) and returns SVG as a string.
    """

    def __init__(self, options: RenderOptions | None = None) -> None:
        self.options = options or RenderOptions()

    # ══════════════════════════════════════════════════════════════════════
    # Public API
    # ══════════════════════════════════════════════════════════════════════

    def render(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None = None,
    ) -> str:
        bounds = template.compute_viewbox(variables, self.options.theme.padding)
        return self._build_svg(template, variables, bounds)

    def render_to_string(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None = None,
        pretty: bool = True,
    ) -> str:
        svg = self.render(template, variables)
        if pretty:
            svg = self._prettify(svg)
        return svg

    # ══════════════════════════════════════════════════════════════════════
    # SVG Builder
    # ══════════════════════════════════════════════════════════════════════

    def _build_svg(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        bounds: BoundingBox,
    ) -> str:
        w = self.options.viewbox_width(bounds)
        h = self.options.viewbox_height(bounds)
        vb = f"{bounds.xmin} {bounds.ymin} {bounds.width} {bounds.height}"

        lines: list[str] = []
        indent = "  "

        lines.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{vb}" width="{w}" height="{h}" '
            f'data-diagram-id="{template.metadata.template_id}" '
            f'data-diagram-type="{template.metadata.diagram_type}"'
        )

        if self.options.inline_styles:
            lines.append(f' style="background:{self.options.theme.background_color};overflow:hidden;"')

        lines.append(">")

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Background -->")
        lines.append(f"{indent}<rect width=\"100%\" height=\"100%\" "
                     f'fill="{self.options.theme.background_color}" '
                     f'data-layer="background"/>')

        points = template.points_dict(variables)

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Grids -->")
        lines.extend(self._render_grids(template, variables, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Axes -->")
        lines.extend(self._render_axes(template, variables, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Fills (Polygons, Circles, Rectangles) -->")
        lines.extend(self._render_fills(template, variables, points, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Strokes (Lines, Arcs, Polylines) -->")
        lines.extend(self._render_strokes(template, variables, points, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Points -->")
        lines.extend(self._render_points(template, variables, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Measurements -->")
        lines.extend(self._render_measurements(template, variables, points, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Labels -->")
        lines.extend(self._render_labels(template, variables, indent))

        if self.options.layer_separators:
            lines.append(f"{indent}<!-- Layer: Tick Marks -->")
        lines.extend(self._render_ticks(template, variables, indent))

        lines.append("</svg>")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════════
    # Layer Renderers
    # ══════════════════════════════════════════════════════════════════════

    def _render_grids(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        lines: list[str] = []
        points = template.points_dict(variables)
        theme = self.options.theme

        for prim in template.primitives:
            if not isinstance(prim, Grid):
                continue
            style = prim.style or StrokeStyle(
                color=theme.grid_color,
                width=theme.grid_stroke_width,
            )
            for x in prim.x_lines:
                lines.append(
                    f'{indent}<line x1="{x}" y1="0" x2="{x}" y2="100%" '
                    f'{style.to_svg_attrs()} data-layer="grid"/>'
                )
            for y in prim.y_lines:
                lines.append(
                    f'{indent}<line x1="0" y1="{y}" x2="100%" y2="{y}" '
                    f'{style.to_svg_attrs()} data-layer="grid"/>'
                )
        return lines

    def _render_axes(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        lines: list[str] = []
        points = template.points_dict(variables)
        theme = self.options.theme

        for prim in template.primitives:
            if not isinstance(prim, Axis):
                continue
            p1 = points.get(prim.start)
            p2 = points.get(prim.end)
            if p1 is None or p2 is None:
                continue
            x1 = p1.resolved_x(variables)
            y1 = p1.resolved_y(variables)
            x2 = p2.resolved_x(variables)
            y2 = p2.resolved_y(variables)
            style = prim.style or StrokeStyle(
                color=theme.axis_color,
                width=theme.axis_stroke_width,
            )
            lines.append(
                f'{indent}<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'{style.to_svg_attrs()} data-layer="axis"/>'
            )
            if prim.label:
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                off = 20 if prim.orientation == "horizontal" else -20
                lines.append(
                    f'{indent}<text x="{mx}" y="{my + off}" '
                    f'font-family="{theme.default_font_family}" '
                    f'font-size="{theme.default_font_size}" '
                    f'fill="{theme.default_font_color}" '
                    f'text-anchor="middle" data-layer="axis-label">'
                    f'{self._escape(prim.label)}</text>'
                )
        return lines

    def _render_fills(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        lines: list[str] = []

        for prim in template.primitives:
            if isinstance(prim, Polygon):
                lines.extend(self._render_polygon_fill(prim, variables, points, indent))
            elif isinstance(prim, Circle):
                lines.extend(self._render_circle_fill(prim, variables, points, indent))
            elif isinstance(prim, Rectangle):
                lines.extend(self._render_rectangle_fill(prim, variables, indent))
            elif isinstance(prim, Ellipse):
                lines.extend(self._render_ellipse_fill(prim, variables, points, indent))

        return lines

    def _render_polygon_fill(
        self,
        prim: Polygon,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        if prim.fill is None or prim.fill.color == "none":
            return []
        pt_str = self._points_string(prim.vertices, variables, points)
        if not pt_str:
            return []
        fill_attrs = prim.fill.to_svg_attrs()
        stroke_attrs = (prim.stroke or StrokeStyle()).to_svg_attrs()
        return [
            f'{indent}<polygon points="{pt_str}" '
            f'{fill_attrs} {stroke_attrs} '
            f'data-layer="fill" data-primitive-id="{prim.id}"/>'
        ]

    def _render_circle_fill(
        self,
        prim: Circle,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        if prim.fill is None or prim.fill.color == "none":
            return []
        center = points.get(prim.center)
        if center is None:
            return []
        cx = center.resolved_x(variables)
        cy = center.resolved_y(variables)
        r = prim.resolved_radius(variables)
        fill_attrs = prim.fill.to_svg_attrs()
        stroke_attrs = (prim.stroke or StrokeStyle()).to_svg_attrs()
        return [
            f'{indent}<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'{fill_attrs} {stroke_attrs} '
            f'data-layer="fill" data-primitive-id="{prim.id}"/>'
        ]

    def _render_rectangle_fill(
        self,
        prim: Rectangle,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        if prim.fill is None or prim.fill.color == "none":
            return []
        x = prim.resolved_x(variables)
        y = prim.resolved_y(variables)
        w = prim.resolved_width(variables)
        h = prim.resolved_height(variables)
        fill_attrs = prim.fill.to_svg_attrs()
        stroke_attrs = (prim.stroke or StrokeStyle()).to_svg_attrs()
        rx = f' rx="{prim.rx}"' if prim.rx is not None else ""
        return [
            f'{indent}<rect x="{x}" y="{y}" width="{w}" height="{h}"{rx} '
            f'{fill_attrs} {stroke_attrs} '
            f'data-layer="fill" data-primitive-id="{prim.id}"/>'
        ]

    def _render_ellipse_fill(
        self,
        prim: Ellipse,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        if prim.fill is None or prim.fill.color == "none":
            return []
        center = points.get(prim.center)
        if center is None:
            return []
        cx = center.resolved_x(variables)
        cy = center.resolved_y(variables)
        rx = resolve_value(prim.rx, variables)
        ry = resolve_value(prim.ry, variables)
        fill_attrs = prim.fill.to_svg_attrs()
        stroke_attrs = (prim.stroke or StrokeStyle()).to_svg_attrs()
        return [
            f'{indent}<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
            f'{fill_attrs} {stroke_attrs} '
            f'data-layer="fill" data-primitive-id="{prim.id}"/>'
        ]

    def _render_strokes(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        lines: list[str] = []

        for prim in template.primitives:
            if isinstance(prim, Line):
                lines.extend(self._render_line(template, prim, variables, points, indent))
            elif isinstance(prim, Polyline):
                lines.extend(self._render_polyline(prim, variables, points, indent))
            elif isinstance(prim, Arc):
                lines.extend(self._render_arc(prim, variables, points, indent))
            elif isinstance(prim, Arrow):
                lines.extend(self._render_arrow(prim, variables, points, indent))
            elif isinstance(prim, Polygon) and (prim.stroke is not None or prim.fill is None):
                lines.extend(self._render_polygon_stroke(prim, variables, points, indent))
            elif isinstance(prim, Circle):
                lines.extend(self._render_circle_stroke(prim, variables, points, indent))
            elif isinstance(prim, Rectangle):
                lines.extend(self._render_rectangle_stroke(prim, variables, indent))
            elif isinstance(prim, Ellipse):
                lines.extend(self._render_ellipse_stroke(prim, variables, points, indent))

        return lines

    def _render_line(
        self,
        template: DiagramTemplate,
        prim: Line,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        p1 = points.get(prim.start)
        p2 = points.get(prim.end)
        if p1 is None or p2 is None:
            return []
        x1 = p1.resolved_x(variables)
        y1 = p1.resolved_y(variables)
        x2 = p2.resolved_x(variables)
        y2 = p2.resolved_y(variables)

        extra_attrs = self._variable_data_attrs(template, prim.id)

        return [
            f'{indent}<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'{prim.stroke().to_svg_attrs()} '
            f'data-layer="stroke" data-primitive-id="{prim.id}"{extra_attrs}/>'
        ]

    def _render_polyline(
        self,
        prim: Polyline,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        pt_str = self._points_string(prim.points, variables, points)
        if not pt_str:
            return []
        return [
            f'{indent}<polyline points="{pt_str}" '
            f'{(prim.style or StrokeStyle()).to_svg_attrs()} '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>'
        ]

    def _render_arc(
        self,
        prim: Arc,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        center = points.get(prim.center)
        if center is None:
            return []
        cx = center.resolved_x(variables)
        cy = center.resolved_y(variables)
        r = prim.resolved_radius(variables)

        sa = math.radians(prim.start_angle)
        ea = math.radians(prim.end_angle)
        x1 = cx + r * math.cos(sa)
        y1 = cy + r * math.sin(sa)
        x2 = cx + r * math.cos(ea)
        y2 = cy + r * math.sin(ea)

        large_arc = 1 if abs(prim.end_angle - prim.start_angle) > 180 else 0
        sweep = 1 if prim.end_angle > prim.start_angle else 0

        d = (
            f"M{x1},{y1} A{r},{r} 0 {large_arc},{sweep} {x2},{y2}"
        )

        return [
            f'{indent}<path d="{d}" '
            f'{(prim.style or StrokeStyle()).to_svg_attrs()} '
            f'fill="none" '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>'
        ]

    def _render_arrow(
        self,
        prim: Arrow,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        p1 = points.get(prim.start)
        p2 = points.get(prim.end)
        if p1 is None or p2 is None:
            return []
        x1 = p1.resolved_x(variables)
        y1 = p1.resolved_y(variables)
        x2 = p2.resolved_x(variables)
        y2 = p2.resolved_y(variables)

        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        hs = prim.head_size

        ax1 = x2 - hs * math.cos(angle - math.pi / 6)
        ay1 = y2 - hs * math.sin(angle - math.pi / 6)
        ax2 = x2 - hs * math.cos(angle + math.pi / 6)
        ay2 = y2 - hs * math.sin(angle + math.pi / 6)

        style = prim.style or StrokeStyle()
        head_style = StrokeStyle(
            color=style.color, width=style.width,
            opacity=style.opacity,
        )

        return [
            f'{indent}<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'{style.to_svg_attrs()} '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>',
            f'{indent}<polygon points="{x2},{y2} {ax1},{ay1} {ax2},{ay2}" '
            f'{head_style.to_svg_attrs()} fill="{style.color}" '
            f'data-layer="stroke" data-primitive-id="{prim.id}-head"/>',
        ]

    def _render_polygon_stroke(
        self,
        prim: Polygon,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        pt_str = self._points_string(prim.vertices, variables, points)
        if not pt_str:
            return []
        style = prim.stroke or StrokeStyle()
        fill = prim.fill or FillStyle(color="none")
        return [
            f'{indent}<polygon points="{pt_str}" '
            f'{style.to_svg_attrs()} {fill.to_svg_attrs()} '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>'
        ]

    def _render_circle_stroke(
        self,
        prim: Circle,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        center = points.get(prim.center)
        if center is None:
            return []
        cx = center.resolved_x(variables)
        cy = center.resolved_y(variables)
        r = prim.resolved_radius(variables)
        return [
            f'{indent}<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'{(prim.stroke or StrokeStyle()).to_svg_attrs()} '
            f'fill="none" '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>'
        ]

    def _render_rectangle_stroke(
        self,
        prim: Rectangle,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        x = prim.resolved_x(variables)
        y = prim.resolved_y(variables)
        w = prim.resolved_width(variables)
        h = prim.resolved_height(variables)
        style = prim.stroke or StrokeStyle()
        fill = prim.fill or FillStyle(color="none")
        rx = f' rx="{prim.rx}"' if prim.rx is not None else ""
        return [
            f'{indent}<rect x="{x}" y="{y}" width="{w}" height="{h}"{rx} '
            f'{style.to_svg_attrs()} {fill.to_svg_attrs()} '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>'
        ]

    def _render_ellipse_stroke(
        self,
        prim: Ellipse,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        center = points.get(prim.center)
        if center is None:
            return []
        cx = center.resolved_x(variables)
        cy = center.resolved_y(variables)
        rx = resolve_value(prim.rx, variables)
        ry = resolve_value(prim.ry, variables)
        return [
            f'{indent}<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
            f'{(prim.stroke or StrokeStyle()).to_svg_attrs()} '
            f'fill="none" '
            f'data-layer="stroke" data-primitive-id="{prim.id}"/>'
        ]

    def _render_points(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        lines: list[str] = []
        theme = self.options.theme

        for prim in template.primitives:
            if not isinstance(prim, Point):
                continue
            x = prim.resolved_x(variables)
            y = prim.resolved_y(variables)
            style = prim.style or PointStyle(
                radius=theme.point_radius,
                fill=theme.point_fill,
            )
            lines.append(
                f'{indent}<circle cx="{x}" cy="{y}" {style.to_svg_attrs()} '
                f'data-layer="point" data-primitive-id="{prim.id}"/>'
            )
            if prim.label:
                lines.append(
                    f'{indent}<text x="{x}" y="{y - 10}" '
                    f'font-family="{theme.default_font_family}" '
                    f'font-size="{theme.default_font_size}" '
                    f'fill="{theme.default_font_color}" '
                    f'text-anchor="middle" dominant-baseline="central" '
                    f'data-layer="point-label" data-primitive-id="{prim.id}">'
                    f'{self._escape(prim.label)}</text>'
                )
        return lines

    def _render_measurements(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        points: dict[str, Point],
        indent: str,
    ) -> list[str]:
        lines: list[str] = []
        theme = self.options.theme

        for prim in template.primitives:
            if not isinstance(prim, Measurement):
                continue
            target = template.get_primitive(prim.primitive_ref)
            if target is None or not isinstance(target, Line):
                continue
            p1 = points.get(target.start)
            p2 = points.get(target.end)
            if p1 is None or p2 is None:
                continue
            x1 = p1.resolved_x(variables)
            y1 = p1.resolved_y(variables)
            x2 = p2.resolved_x(variables)
            y2 = p2.resolved_y(variables)

            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                nx = -dy / length * prim.offset
                ny = dx / length * prim.offset
            else:
                nx = 0
                ny = -prim.offset

            lx = mx + nx
            ly = my + ny

            label_text = prim.label
            val = prim.resolved_value(variables)
            if val is not None:
                label_text = f"{label_text} = {val}"

            if prim.show_ticks:
                tick_off = 5.0
                tx1 = mx + nx * tick_off / (prim.offset or 1)
                ty1 = my + ny * tick_off / (prim.offset or 1)
                lines.append(
                    f'{indent}<line x1="{mx}" y1="{my}" x2="{tx1}" y2="{ty1}" '
                    f'stroke="{theme.measurement_color}" stroke-width="1" '
                    f'data-layer="measurement-tick"/>'
                )

            lines.append(
                f'{indent}<text x="{lx}" y="{ly}" '
                f'font-family="{theme.default_font_family}" '
                f'font-size="{theme.measurement_font_size}" '
                f'fill="{theme.measurement_color}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'data-layer="measurement" data-primitive-id="{prim.id}">'
                f'{self._escape(label_text)}</text>'
            )
        return lines

    def _render_labels(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        lines: list[str] = []
        theme = self.options.theme

        for prim in template.primitives:
            if not isinstance(prim, TextLabel):
                continue
            x = prim.resolved_x(variables)
            y = prim.resolved_y(variables)
            font = prim.font or FontStyle(
                family=theme.default_font_family,
                size=theme.default_font_size,
                color=theme.default_font_color,
            )
            rot = f' transform="rotate({prim.rotation},{x},{y})"' if prim.rotation else ""
            lines.append(
                f'{indent}<text x="{x}" y="{y}" {font.to_svg_attrs()}{rot} '
                f'data-layer="label" data-primitive-id="{prim.id}">'
                f'{self._escape(prim.text)}</text>'
            )
        return lines

    def _render_ticks(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
        indent: str,
    ) -> list[str]:
        lines: list[str] = []
        points = template.points_dict(variables)
        theme = self.options.theme

        for prim in template.primitives:
            if not isinstance(prim, TickMark):
                continue
            axis_prim = template.get_primitive(prim.axis_ref)
            if axis_prim is None or not isinstance(axis_prim, Axis):
                continue
            p1 = points.get(axis_prim.start)
            p2 = points.get(axis_prim.end)
            if p1 is None or p2 is None:
                continue
            x1 = p1.resolved_x(variables)
            y1 = p1.resolved_y(variables)
            x2 = p2.resolved_x(variables)
            y2 = p2.resolved_y(variables)

            t = prim.position
            tx = x1 + (x2 - x1) * t
            ty = y1 + (y2 - y1) * t

            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                nx = -dy / length * prim.length
                ny = dx / length * prim.length
            else:
                nx = 0
                ny = -prim.length

            lx = tx + nx
            ly = ty + ny

            style = prim.style or StrokeStyle(color=theme.axis_color, width=1)
            lines.append(
                f'{indent}<line x1="{tx}" y1="{ty}" x2="{lx}" y2="{ly}" '
                f'{style.to_svg_attrs()} '
                f'data-layer="tick" data-primitive-id="{prim.id}"/>'
            )

            if prim.label:
                label_offset = 8.0
                lx2 = tx + nx + (nx / (prim.length or 1)) * label_offset
                ly2 = ty + ny + (ny / (prim.length or 1)) * label_offset
                lines.append(
                    f'{indent}<text x="{lx2}" y="{ly2}" '
                    f'font-family="{theme.default_font_family}" '
                    f'font-size="{theme.default_font_size - 2}" '
                    f'fill="{theme.default_font_color}" '
                    f'text-anchor="middle" dominant-baseline="central" '
                    f'data-layer="tick-label">'
                    f'{self._escape(prim.label)}</text>'
                )
        return lines

    # ══════════════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════════════

    def _points_string(
        self,
        point_ids: list[str],
        variables: dict[str, Any] | None,
        points: dict[str, Point],
    ) -> str:
        coords: list[str] = []
        for pid in point_ids:
            pt = points.get(pid)
            if pt is None:
                return ""
            x = pt.resolved_x(variables)
            y = pt.resolved_y(variables)
            coords.append(f"{x},{y}")
        return " ".join(coords)

    def _variable_data_attrs(
        self,
        template: DiagramTemplate | None,
        primitive_id: str,
    ) -> str:
        if not self.options.include_data_attributes or template is None:
            return ""
        bindings = template.bindings.get_bindings_for_primitive(primitive_id)
        if not bindings:
            return ""
        parts: list[str] = []
        for b in bindings:
            attr_name = f"data-var-{b.property_name.replace('_', '-')}"
            parts.append(f'{attr_name}="{b.variable_name}"')
        if parts:
            return " " + " ".join(parts)
        return ""

    def _escape(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _prettify(self, svg: str) -> str:
        lines = svg.split("\n")
        result: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                result.append(line)
        return "\n".join(result)



