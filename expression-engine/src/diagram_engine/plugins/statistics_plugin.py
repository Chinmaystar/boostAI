from __future__ import annotations

from typing import Any, Optional

from ..diagram_template import (
    DIAGRAM_TYPE_BAR_GRAPH, DIAGRAM_TYPE_HISTOGRAM,
    DIAGRAM_TYPE_PIE_CHART, DIAGRAM_TYPE_LINE_GRAPH,
    DIAGRAM_TYPE_SCATTER_PLOT,
    DiagramTemplate, DiagramTemplateBuilder,
)
from ..plugin_base import DiagramPlugin
from ..primitives import (
    Axis, FillStyle, Grid, Line, Point, Rectangle, StrokeStyle,
    TextLabel, TickMark, FontStyle,
)
from ..variable_binding import BindingScope


class StatisticsPlugin(DiagramPlugin):
    """Plugin for statistical diagrams: bar graphs, histograms, pie
    charts, line graphs, and scatter plots.
    """

    @property
    def plugin_name(self) -> str:
        return "statistics"

    @property
    def supported_diagram_types(self) -> list[str]:
        return [
            DIAGRAM_TYPE_BAR_GRAPH,
            DIAGRAM_TYPE_HISTOGRAM,
            DIAGRAM_TYPE_PIE_CHART,
            DIAGRAM_TYPE_LINE_GRAPH,
            DIAGRAM_TYPE_SCATTER_PLOT,
        ]

    def can_handle_input(self, input_data: dict[str, Any]) -> bool:
        ftype = input_data.get("figure_type", "").lower()
        return ftype in (
            "bar_graph", "bar_chart", "histogram",
            "pie_chart", "line_graph", "scatter_plot", "statistics",
        )

    def build_template(
        self,
        input_data: dict[str, Any],
        template_id: str | None = None,
    ) -> DiagramTemplate:
        tid = template_id or input_data.get("id", "stats_diagram")
        figure_type = input_data.get("figure_type", "statistics").lower()

        builder = DiagramTemplateBuilder(tid, figure_type)
        builder.with_plugin_source("statistics_plugin")
        builder.with_tags("statistics", figure_type)

        data_points = input_data.get("data_points", [])
        categories = input_data.get("categories", [])
        variables = input_data.get("variables", {})

        if figure_type == DIAGRAM_TYPE_BAR_GRAPH:
            self._build_bar_graph(builder, data_points, categories, variables)
        elif figure_type == DIAGRAM_TYPE_HISTOGRAM:
            self._build_histogram(builder, data_points, categories, variables)
        elif figure_type == DIAGRAM_TYPE_PIE_CHART:
            self._build_pie_chart(builder, data_points, categories, variables)
        elif figure_type == DIAGRAM_TYPE_SCATTER_PLOT:
            self._build_scatter_plot(builder, data_points, variables)
        else:
            self._build_line_graph(builder, data_points, variables)

        return builder.build()

    def _build_bar_graph(
        self,
        builder: DiagramTemplateBuilder,
        data_points: list[dict[str, Any]],
        categories: list[str],
        variables: dict[str, Any],
    ) -> None:
        bar_width = 30.0
        gap = 10.0
        origin_x = 50.0
        origin_y = 300.0
        max_height = 250.0

        builder.add_point(Point(id="origin", x=origin_x, y=origin_y))
        builder.add_point(Point(id="x_end", x=origin_x + len(data_points) * (bar_width + gap) + 50, y=origin_y))
        builder.add_point(Point(id="y_end", x=origin_x, y=origin_y - max_height - 30))

        builder.add_axis(Axis(
            id="x_axis", start="origin", end="x_end",
            orientation="horizontal",
            label=categories[0] if categories else "Category",
        ))
        builder.add_axis(Axis(
            id="y_axis", start="origin", end="y_end",
            orientation="vertical",
            label="Value",
        ))

        for i, dp in enumerate(data_points):
            value = float(dp.get("value", dp.get("y", 0)))
            label = dp.get("label", str(i + 1))
            x = origin_x + i * (bar_width + gap) + gap / 2
            h = (value / 100.0) * max_height if max_height > 0 else 0

            rect_id = f"bar_{i}"
            builder.add_rectangle(Rectangle(
                id=rect_id,
                x=x, y=origin_y - h,
                width=bar_width, height=h,
                fill=FillStyle(
                    color=dp.get("color", "#4A90D9"),
                    opacity=0.8,
                ),
                stroke=StrokeStyle(color="#333333", width=1),
            ))

            builder.add_text_label(TextLabel(
                id=f"bar_label_{i}",
                text=label,
                x=x + bar_width / 2,
                y=origin_y + 15,
                font=FontStyle(size=10),
            ))

            if i % 2 == 0 or i == len(data_points) - 1:
                tick_id = f"xtick_{i}"
                pos = (x + bar_width / 2 - origin_x) / (
                    len(data_points) * (bar_width + gap) + 50
                )
                builder.add_tick_mark(TickMark(
                    id=tick_id, axis_ref="x_axis",
                    position=pos, label=label,
                ))

            var_name = dp.get("variable")
            if var_name:
                builder.add_binding(
                    rect_id, "height", var_name,
                    scope=BindingScope.MEASUREMENT,
                    default_value=dp.get("default_value", value),
                )

    def _build_histogram(
        self,
        builder: DiagramTemplateBuilder,
        data_points: list[dict[str, Any]],
        categories: list[str],
        variables: dict[str, Any],
    ) -> None:
        self._build_bar_graph(builder, data_points, categories, variables)

    def _build_pie_chart(
        self,
        builder: DiagramTemplateBuilder,
        data_points: list[dict[str, Any]],
        categories: list[str],
        variables: dict[str, Any],
    ) -> None:
        cx, cy, r = 200.0, 200.0, 150.0
        builder.add_point(Point(id="pie_center", x=cx, y=cy))
        total = sum(
            float(dp.get("value", dp.get("y", 1)))
            for dp in data_points
        ) or 1.0

        current_angle = 0.0
        for i, dp in enumerate(data_points):
            value = float(dp.get("value", dp.get("y", 1)))
            slice_angle = (value / total) * 360.0
            label = dp.get("label", str(i + 1))

            from ..primitives import Arc
            end_angle = current_angle + slice_angle

            builder.add_arc(Arc(
                id=f"pie_arc_{i}",
                center="pie_center",
                radius=r,
                start_angle=current_angle,
                end_angle=end_angle,
                style=StrokeStyle(
                    color=dp.get("color", "#4A90D9"),
                    width=1,
                ),
            ))

            import math
            mid_angle = math.radians(current_angle + slice_angle / 2)
            lx = cx + (r * 0.65) * math.cos(mid_angle)
            ly = cy + (r * 0.65) * math.sin(mid_angle)
            builder.add_text_label(TextLabel(
                id=f"pie_label_{i}",
                text=f"{label}",
                x=lx, y=ly,
                font=FontStyle(size=11, anchor="middle"),
            ))

            current_angle = end_angle

            var_name = dp.get("variable")
            if var_name:
                builder.add_binding(
                    f"pie_arc_{i}", "end_angle", var_name,
                    scope=BindingScope.ANGLE,
                    default_value=dp.get("default_value", slice_angle),
                )

    def _build_scatter_plot(
        self,
        builder: DiagramTemplateBuilder,
        data_points: list[dict[str, Any]],
        variables: dict[str, Any],
    ) -> None:
        origin_x, origin_y = 50.0, 300.0
        plot_w, plot_h = 400.0, 250.0
        x_max = max(
            (float(dp.get("x", 0)) for dp in data_points), default=10.0
        )
        y_max = max(
            (float(dp.get("y", 0)) for dp in data_points), default=10.0
        )
        x_max = max(x_max, 1.0)
        y_max = max(y_max, 1.0)

        builder.add_point(Point(id="s_origin", x=origin_x, y=origin_y))
        builder.add_point(Point(id="s_x_end", x=origin_x + plot_w, y=origin_y))
        builder.add_point(Point(id="s_y_end", x=origin_x, y=origin_y - plot_h))

        builder.add_axis(Axis(id="s_x_axis", start="s_origin", end="s_x_end", label="x"))
        builder.add_axis(Axis(id="s_y_axis", start="s_origin", end="s_y_end", label="y"))

        builder.add_grid(Grid(
            id="s_grid",
            x_lines=[origin_x + i * plot_w / 5 for i in range(1, 6)],
            y_lines=[origin_y - i * plot_h / 5 for i in range(1, 6)],
        ))

        for i, dp in enumerate(data_points):
            x = float(dp.get("x", 0))
            y = float(dp.get("y", 0))
            px = origin_x + (x / x_max) * plot_w
            py = origin_y - (y / y_max) * plot_h

            pt_id = f"sp_{i}"
            builder.add_point(Point(
                id=pt_id, x=px, y=py,
            ))

            var_x = dp.get("variable_x")
            var_y = dp.get("variable_y")
            if var_x:
                builder.add_binding(pt_id, "x", var_x, scope=BindingScope.POSITION)
            if var_y:
                builder.add_binding(pt_id, "y", var_y, scope=BindingScope.POSITION)

        self._add_axes_ticks(
            builder, 5, origin_x, origin_y, plot_w, plot_h, x_max, y_max,
        )

    def _build_line_graph(
        self,
        builder: DiagramTemplateBuilder,
        data_points: list[dict[str, Any]],
        variables: dict[str, Any],
    ) -> None:
        origin_x, origin_y = 50.0, 300.0
        plot_w, plot_h = 400.0, 250.0
        x_max = max(
            (float(dp.get("x", 0)) for dp in data_points), default=10.0
        )
        y_max = max(
            (float(dp.get("y", 0)) for dp in data_points), default=10.0
        )
        x_max = max(x_max, 1.0)
        y_max = max(y_max, 1.0)

        builder.add_point(Point(id="lg_origin", x=origin_x, y=origin_y))
        builder.add_point(Point(id="lg_x_end", x=origin_x + plot_w, y=origin_y))
        builder.add_point(Point(id="lg_y_end", x=origin_x, y=origin_y - plot_h))

        builder.add_axis(Axis(id="lg_x_axis", start="lg_origin", end="lg_x_end", label="x"))
        builder.add_axis(Axis(id="lg_y_axis", start="lg_origin", end="lg_y_end", label="y"))

        builder.add_grid(Grid(
            id="lg_grid",
            x_lines=[origin_x + i * plot_w / 5 for i in range(1, 6)],
            y_lines=[origin_y - i * plot_h / 5 for i in range(1, 6)],
        ))

        pts: list[str] = []
        for i, dp in enumerate(data_points):
            x = float(dp.get("x", 0))
            y = float(dp.get("y", 0))
            px = origin_x + (x / x_max) * plot_w
            py = origin_y - (y / y_max) * plot_h

            pt_id = f"lgp_{i}"
            builder.add_point(Point(id=pt_id, x=px, y=py))
            pts.append(pt_id)

        if len(pts) > 1:
            polyline_id = "lg_line"
            from ..primitives import Polyline
            builder.add_polyline(Polyline(
                id=polyline_id,
                points=pts,
                style=StrokeStyle(color="#E74C3C", width=2),
            ))

        self._add_axes_ticks(
            builder, 5, origin_x, origin_y, plot_w, plot_h, x_max, y_max,
        )

    def _add_axes_ticks(
        self,
        builder: DiagramTemplateBuilder,
        n_ticks: int,
        ox: float, oy: float,
        pw: float, ph: float,
        x_max: float, y_max: float,
    ) -> None:
        for i in range(n_ticks + 1):
            t = i / n_ticks
            xt = ox + t * pw
            yt = oy - t * ph

            builder.add_tick_mark(TickMark(
                id=f"xt_{i}", axis_ref="s_x_axis",
                position=t,
                label=str(round(t * x_max, 1)) if x_max <= 100 else str(i),
            ))
            builder.add_tick_mark(TickMark(
                id=f"yt_{i}", axis_ref="s_y_axis",
                position=t,
                label=str(round(t * y_max, 1)) if y_max <= 100 else str(i),
            ))
