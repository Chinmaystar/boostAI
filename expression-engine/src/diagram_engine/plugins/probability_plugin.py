from __future__ import annotations

from typing import Any, Optional

from ..diagram_template import (
    DIAGRAM_TYPE_VENN, DIAGRAM_TYPE_TREE, DIAGRAM_TYPE_PROBABILITY,
    DiagramTemplate, DiagramTemplateBuilder,
)
from ..plugin_base import DiagramPlugin
from ..primitives import (
    Circle, FillStyle, FontStyle, Line, Point, StrokeStyle, TextLabel,
)
from ..variable_binding import BindingScope


class ProbabilityPlugin(DiagramPlugin):
    """Plugin for probability diagrams: Venn diagrams, tree diagrams,
    and probability space diagrams.
    """

    @property
    def plugin_name(self) -> str:
        return "probability"

    @property
    def supported_diagram_types(self) -> list[str]:
        return [
            DIAGRAM_TYPE_VENN,
            DIAGRAM_TYPE_TREE,
            DIAGRAM_TYPE_PROBABILITY,
        ]

    def can_handle_input(self, input_data: dict[str, Any]) -> bool:
        ftype = input_data.get("figure_type", "").lower()
        return ftype in ("venn", "tree", "probability", "venn_diagram", "tree_diagram")

    def build_template(
        self,
        input_data: dict[str, Any],
        template_id: str | None = None,
    ) -> DiagramTemplate:
        tid = template_id or input_data.get("id", "prob_diagram")
        figure_type = input_data.get("figure_type", "probability").lower()

        builder = DiagramTemplateBuilder(tid, figure_type)
        builder.with_plugin_source("probability_plugin")
        builder.with_tags("probability", figure_type)

        if figure_type == DIAGRAM_TYPE_VENN:
            self._build_venn(builder, input_data)
        elif figure_type in (DIAGRAM_TYPE_TREE, DIAGRAM_TYPE_PROBABILITY):
            self._build_tree(builder, input_data)

        return builder.build()

    def _build_venn(
        self,
        builder: DiagramTemplateBuilder,
        data: dict[str, Any],
    ) -> None:
        sets_data = data.get("sets", [])
        labels_data = data.get("labels", [])
        variables = data.get("variables", {})

        cx1, cy1 = 150.0, 200.0
        cx2, cy2 = 250.0, 200.0
        r = 100.0

        builder.add_point(Point(id="venn_c1", x=cx1, y=cy1))
        builder.add_point(Point(id="venn_c2", x=cx2, y=cy2))

        c1 = Circle(
            id="venn_set_a",
            center="venn_c1", radius=r,
            stroke=StrokeStyle(color="#E74C3C", width=2),
            fill=FillStyle(color="rgba(231,76,60,0.2)"),
        )

        c2 = Circle(
            id="venn_set_b",
            center="venn_c2", radius=r,
            stroke=StrokeStyle(color="#3498DB", width=2),
            fill=FillStyle(color="rgba(52,152,219,0.2)"),
        )

        builder.add_circle(c1)
        builder.add_circle(c2)

        if len(sets_data) >= 1:
            builder.add_text_label(TextLabel(
                id="venn_label_a", text=sets_data[0].get("label", "A"),
                x=cx1 - r - 20, y=cy1,
                font=FontStyle(size=16, bold=True),
            ))
        if len(sets_data) >= 2:
            builder.add_text_label(TextLabel(
                id="venn_label_b", text=sets_data[1].get("label", "B"),
                x=cx2 + r + 20, y=cy2,
                font=FontStyle(size=16, bold=True),
            ))

        for ld in labels_data:
            builder.add_text_label(TextLabel(
                id=ld.get("id", f"vl_{len(labels_data)}"),
                text=ld.get("text", ""),
                x=float(ld.get("x", cx1)),
                y=float(ld.get("y", cy1)),
                font=FontStyle(size=12),
            ))

    def _build_tree(
        self,
        builder: DiagramTemplateBuilder,
        data: dict[str, Any],
    ) -> None:
        nodes_data = data.get("nodes", [])
        edges_data = data.get("edges", [])
        variables = data.get("variables", {})

        node_positions: dict[str, str] = {}
        for nd in nodes_data:
            nid = nd.get("id", f"tn_{len(node_positions)}")
            x = float(nd.get("x", 100 + len(node_positions) * 80))
            y = float(nd.get("y", 50 + len(node_positions) * 60))
            label = nd.get("label", nid)
            prob = nd.get("probability")

            pid = f"tree_pt_{nid}"
            builder.add_point(Point(id=pid, x=x, y=y))
            node_positions[nid] = pid

            label_id = f"tree_label_{nid}"
            builder.add_text_label(TextLabel(
                id=label_id, text=label,
                x=x, y=y - 20,
                font=FontStyle(size=12, bold=True),
            ))

            if prob is not None:
                builder.add_text_label(TextLabel(
                    id=f"tree_prob_{nid}", text=f"P={prob}",
                    x=x, y=y + 15,
                    font=FontStyle(size=10, color="#555555"),
                ))

        for ed in edges_data:
            source = ed.get("source", ed.get("from", ""))
            target = ed.get("target", ed.get("to", ""))
            label = ed.get("label", "")

            sp = node_positions.get(source)
            tp = node_positions.get(target)
            if sp and tp:
                lid = f"tree_edge_{source}_{target}"
                builder.add_line(Line(
                    id=lid, start=sp, end=tp,
                    style=StrokeStyle(color="#555555", width=1.5),
                ))
                builder.add_graph_edge(sp, lid, "connects")
                builder.add_graph_edge(tp, lid, "connects")

                if label:
                    pts = data.get("nodes", [])
                    sx = next((float(n.get("x", 0)) for n in nodes_data if n.get("id") == source), 0)
                    sy = next((float(n.get("y", 0)) for n in nodes_data if n.get("id") == source), 0)
                    tx = next((float(n.get("x", 0)) for n in nodes_data if n.get("id") == target), 0)
                    ty = next((float(n.get("y", 0)) for n in nodes_data if n.get("id") == target), 0)
                    mx = (sx + tx) / 2
                    my = (sy + ty) / 2
                    builder.add_text_label(TextLabel(
                        id=f"tree_edge_label_{source}_{target}",
                        text=label,
                        x=mx, y=my - 10,
                        font=FontStyle(size=10, color="#888888"),
                    ))
