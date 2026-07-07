from __future__ import annotations

from typing import Any, Optional

from ..diagram_template import (
    DIAGRAM_TYPE_COORDINATE_GRID, DIAGRAM_TYPE_CARTESIAN_GRAPH,
    DiagramTemplate, DiagramTemplateBuilder,
)
from ..plugin_base import DiagramPlugin
from ..primitives import (
    Axis, FillStyle, FontStyle, Grid, Line, Point, StrokeStyle, TextLabel,
    TickMark,
)
from ..variable_binding import BindingScope


class GraphsPlugin(DiagramPlugin):
    """Plugin for graph and coordinate diagrams: coordinate grids,
    Cartesian graphs, and general graph theory diagrams.
    """

    @property
    def plugin_name(self) -> str:
        return "graphs"

    @property
    def supported_diagram_types(self) -> list[str]:
        return [
            DIAGRAM_TYPE_COORDINATE_GRID,
            DIAGRAM_TYPE_CARTESIAN_GRAPH,
        ]

    def can_handle_input(self, input_data: dict[str, Any]) -> bool:
        ftype = input_data.get("figure_type", "").lower()
        return ftype in (
            "coordinate_grid", "cartesian_graph",
            "coordinate_plane", "graph", "grid",
        )

    def build_template(
        self,
        input_data: dict[str, Any],
        template_id: str | None = None,
    ) -> DiagramTemplate:
        tid = template_id or input_data.get("id", "graph_diagram")
        figure_type = input_data.get("figure_type", "coordinate_grid").lower()

        builder = DiagramTemplateBuilder(tid, figure_type)
        builder.with_plugin_source("graphs_plugin")
        builder.with_tags("graphs", figure_type)

        grid_config = input_data.get("grid", {})
        x_min = float(grid_config.get("x_min", -10))
        x_max = float(grid_config.get("x_max", 10))
        y_min = float(grid_config.get("y_min", -10))
        y_max = float(grid_config.get("y_max", 10))
        origin_x = float(grid_config.get("origin_x", 250))
        origin_y = float(grid_config.get("origin_y", 250))
        scale = float(grid_config.get("scale", 20))

        lines_data = input_data.get("lines", [])
        points_data = input_data.get("points", [])
        functions_data = input_data.get("functions", [])
        labels_data = input_data.get("labels", [])

        self._add_coordinate_system(
            builder, x_min, x_max, y_min, y_max,
            origin_x, origin_y, scale,
        )

        for ld in lines_data:
            self._add_line(builder, ld, origin_x, origin_y, scale)

        for pd in points_data:
            self._add_point(builder, pd, origin_x, origin_y, scale)

        for fd in functions_data:
            self._add_function_points(
                builder, fd, x_min, x_max,
                origin_x, origin_y, scale,
            )

        for ld in labels_data:
            builder.add_text_label(TextLabel(
                id=ld.get("id", f"label_{len(labels_data)}"),
                text=ld.get("text", ""),
                x=float(ld.get("x", 0)) * scale + origin_x,
                y=origin_y - float(ld.get("y", 0)) * scale,
                font=FontStyle(size=12),
            ))

        return builder.build()

    def _add_coordinate_system(
        self,
        builder: DiagramTemplateBuilder,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        ox: float, oy: float,
        scale: float,
    ) -> None:
        left = ox + x_min * scale
        right = ox + x_max * scale
        top = oy - y_max * scale
        bottom = oy - y_min * scale

        builder.add_point(Point(id="coord_origin", x=ox, y=oy))
        builder.add_point(Point(id="coord_x_end", x=right, y=oy))
        builder.add_point(Point(id="coord_y_end", x=ox, y=top))
        builder.add_point(Point(id="coord_x_start", x=left, y=oy))
        builder.add_point(Point(id="coord_y_start", x=ox, y=bottom))

        builder.add_axis(Axis(
            id="coord_x_axis", start="coord_x_start",
            end="coord_x_end", label="x",
            orientation="horizontal",
            style=StrokeStyle(color="#333333", width=1.5),
        ))
        builder.add_axis(Axis(
            id="coord_y_axis", start="coord_y_start",
            end="coord_y_end", label="y",
            orientation="vertical",
            style=StrokeStyle(color="#333333", width=1.5),
        ))

        grid_x = [ox + i * scale for i in range(int(x_min), int(x_max) + 1) if i != 0]
        grid_y = [oy - i * scale for i in range(int(y_min), int(y_max) + 1) if i != 0]
        builder.add_grid(Grid(
            id="coord_grid",
            x_lines=grid_x, y_lines=grid_y,
            style=StrokeStyle(color="#e0e0e0", width=0.5),
        ))

        for i in range(int(x_min), int(x_max) + 1):
            if i == 0:
                continue
            t = (i - x_min) / (x_max - x_min)
            label_text = str(i)
            builder.add_tick_mark(TickMark(
                id=f"cx_tick_{i}", axis_ref="coord_x_axis",
                position=t, label=label_text,
                length=5,
            ))

        for i in range(int(y_min), int(y_max) + 1):
            if i == 0:
                continue
            t = (i - y_min) / (y_max - y_min)
            label_text = str(i)
            builder.add_tick_mark(TickMark(
                id=f"cy_tick_{i}", axis_ref="coord_y_axis",
                position=t, label=label_text,
                length=5,
            ))

    def _add_line(
        self,
        builder: DiagramTemplateBuilder,
        line_data: dict[str, Any],
        ox: float, oy: float, scale: float,
    ) -> None:
        x1 = float(line_data.get("x1", 0)) * scale + ox
        y1 = oy - float(line_data.get("y1", 0)) * scale
        x2 = float(line_data.get("x2", 10)) * scale + ox
        y2 = oy - float(line_data.get("y2", 10)) * scale

        start_id = f"gl_start_{line_data.get('id', 'l')}"
        end_id = f"gl_end_{line_data.get('id', 'l')}"

        builder.add_point(Point(id=start_id, x=x1, y=y1))
        builder.add_point(Point(id=end_id, x=x2, y=y2))

        lid = line_data.get("id", f"gl_line")
        builder.add_line(Line(
            id=lid, start=start_id, end=end_id,
            style=StrokeStyle(
                color=line_data.get("color", "#E74C3C"),
                width=float(line_data.get("width", 2)),
            ),
        ))

        slope_var = line_data.get("variable_slope")
        if slope_var:
            builder.add_binding(
                lid, "slope", slope_var,
                scope=BindingScope.GEOMETRY,
                default_value=line_data.get("default_slope"),
            )

    def _add_point(
        self,
        builder: DiagramTemplateBuilder,
        point_data: dict[str, Any],
        ox: float, oy: float, scale: float,
    ) -> None:
        x = float(point_data.get("x", 0)) * scale + ox
        y = oy - float(point_data.get("y", 0)) * scale
        label = point_data.get("label", "")
        pid = point_data.get("id", f"gp_{x}_{y}")

        builder.add_point(Point(id=pid, x=x, y=y))

        if label:
            builder.add_text_label(TextLabel(
                id=f"{pid}_label", text=label,
                x=x, y=y - 12,
                font=FontStyle(size=11),
            ))

    def _add_function_points(
        self,
        builder: DiagramTemplateBuilder,
        func_data: dict[str, Any],
        x_min: float, x_max: float,
        ox: float, oy: float, scale: float,
    ) -> None:
        expression = func_data.get("expression", "")
        n_points = int(func_data.get("resolution", 50))
        step = (x_max - x_min) / n_points

        point_ids: list[str] = []
        for i in range(n_points + 1):
            x_val = x_min + i * step
            y_val = func_data.get("values", {}).get(x_val, 0)
            px = ox + x_val * scale
            py = oy - y_val * scale
            pid = f"func_{func_data.get('id', 'f')}_{i}"
            builder.add_point(Point(id=pid, x=px, y=py))
            point_ids.append(pid)

        if len(point_ids) > 1:
            from ..primitives import Polyline
            builder.add_polyline(Polyline(
                id=f"func_{func_data.get('id', 'f')}_line",
                points=point_ids,
                style=StrokeStyle(
                    color=func_data.get("color", "#2ECC71"),
                    width=2,
                ),
            ))
