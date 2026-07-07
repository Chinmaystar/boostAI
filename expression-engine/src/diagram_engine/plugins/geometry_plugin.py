from __future__ import annotations

from typing import Any, Optional

from ..diagram_template import (
    DIAGRAM_TYPE_TRIANGLE, DIAGRAM_TYPE_POLYGON,
    DIAGRAM_TYPE_CIRCLE, DIAGRAM_TYPE_SECTOR, DIAGRAM_TYPE_ANGLE,
    DiagramTemplate, DiagramTemplateBuilder,
)
from ..plugin_base import DiagramPlugin
from ..primitives import (
    Arc, Circle, FillStyle, Line, Measurement, Point, Polygon,
    StrokeStyle,
)
from ..variable_binding import BindingScope


class GeometryPlugin(DiagramPlugin):
    """Plugin for geometric diagrams: triangles, polygons, circles,
    sectors, and angles.
    """

    @property
    def plugin_name(self) -> str:
        return "geometry"

    @property
    def supported_diagram_types(self) -> list[str]:
        return [
            DIAGRAM_TYPE_TRIANGLE,
            DIAGRAM_TYPE_POLYGON,
            DIAGRAM_TYPE_CIRCLE,
            DIAGRAM_TYPE_SECTOR,
            DIAGRAM_TYPE_ANGLE,
        ]

    def can_handle_input(self, input_data: dict[str, Any]) -> bool:
        ftype = input_data.get("figure_type", "").lower()
        return ftype in ("triangle", "polygon", "circle", "angle", "sector", "geometry")

    def build_template(
        self,
        input_data: dict[str, Any],
        template_id: str | None = None,
    ) -> DiagramTemplate:
        tid = template_id or input_data.get("id", "geo_diagram")
        figure_type = input_data.get("figure_type", "geometry").lower()

        builder = DiagramTemplateBuilder(tid, figure_type)
        builder.with_plugin_source("geometry_plugin")
        builder.with_tags("geometry", figure_type)

        points_data = input_data.get("points", [])
        lines_data = input_data.get("lines", [])
        circles_data = input_data.get("circles", [])
        arcs_data = input_data.get("arcs", [])
        labels_data = input_data.get("labels", [])
        measurements_data = input_data.get("measurements", [])
        variables = input_data.get("variables", {})

        point_map: dict[str, str] = {}
        for pd in points_data:
            pid = pd.get("id", f"pt_{len(point_map)}")
            x = pd.get("x", 0)
            y = pd.get("y", 0)
            label = pd.get("label")
            builder.add_point(Point(id=pid, x=float(x), y=float(y), label=label))
            point_map[pd.get("name", pid)] = pid

            if label:
                from ..primitives import TextLabel, FontStyle
                builder.add_text_label(
                    TextLabel(
                        id=f"{pid}_label",
                        x=float(x),
                        y=float(y) - 14.0,
                        text=label,
                        font=FontStyle(size=13.0, bold=True),
                    )
                )

        for ld in lines_data:
            lid = ld.get("id", f"line_{len(point_map)}")
            start = ld.get("start", ld.get("from", ""))
            end = ld.get("end", ld.get("to", ""))
            s_id = point_map.get(start, start)
            e_id = point_map.get(end, end)

            line = Line(id=lid, start=s_id, end=e_id)
            builder.add_line(line)
            builder.add_graph_edge(s_id, lid, "belongs_to")
            builder.add_graph_edge(e_id, lid, "belongs_to")

            var_name = ld.get("variable")
            if var_name:
                builder.add_binding(
                    lid, "length", var_name,
                    scope=BindingScope.GEOMETRY,
                    default_value=ld.get("default_value"),
                    description=f"Length of {lid}",
                )

        for cd in circles_data:
            cid = cd.get("id", "circle_1")
            center_name = cd.get("center", "")
            center_id = point_map.get(center_name, center_name)
            radius = cd.get("radius", 50)

            circle = Circle(
                id=cid, center=center_id,
                radius=float(radius),
                stroke=StrokeStyle(),
                fill=FillStyle(color=cd.get("fill", "none")),
            )
            builder.add_circle(circle)

            var_r = cd.get("variable_radius")
            if var_r:
                builder.add_binding(
                    cid, "radius", var_r,
                    scope=BindingScope.RADIUS,
                    default_value=cd.get("default_radius"),
                )

        for ad in arcs_data:
            aid = ad.get("id", f"arc_{len(arcs_data)}")
            center_name = ad.get("center", "")
            center_id = point_map.get(center_name, center_name)
            arc = Arc(
                id=aid, center=center_id,
                radius=float(ad.get("radius", 30)),
                start_angle=float(ad.get("start_angle", 0)),
                end_angle=float(ad.get("end_angle", 90)),
                style=StrokeStyle(color="#888888", width=1),
            )
            builder.add_arc(arc)

        for md in measurements_data:
            mid = md.get("id", f"meas_{len(measurements_data)}")
            ref = md.get("primitive_ref", "")
            label = md.get("label", "")
            meas = Measurement(
                id=mid, primitive_ref=ref,
                label=label,
                offset=float(md.get("offset", 15)),
            )
            builder.add_measurement(meas)

            var_name = md.get("variable")
            if var_name:
                builder.add_binding(
                    mid, "value", var_name,
                    scope=BindingScope.MEASUREMENT,
                    default_value=md.get("default_value"),
                )

        if figure_type == DIAGRAM_TYPE_TRIANGLE:
            verts = [p.id for p in builder._primitives if isinstance(p, Point)][:3]
            if len(verts) == 3:
                builder.add_polygon(Polygon(
                    id=f"{tid}_poly",
                    vertices=list(verts),
                    stroke=StrokeStyle(width=1.5),
                    fill=FillStyle(color="none"),
                ))
                builder.add_graph_edge(verts[0], verts[1], "connects")
                builder.add_graph_edge(verts[1], verts[2], "connects")
                builder.add_graph_edge(verts[2], verts[0], "connects")

        return builder.build()
