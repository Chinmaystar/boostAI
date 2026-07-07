from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

from .diagram_template import DiagramTemplate
from .primitives import (
    BoundingBox, FontStyle, Measurement, Point, TextLabel, resolve_value,
)


@dataclass
class LayoutConfig:
    """Configuration for the layout engine's overlap avoidance."""
    max_iterations: int = 20
    repulsion_strength: float = 2.0
    min_distance: float = 8.0
    label_padding: float = 4.0
    default_font_size: float = 12.0
    measurement_offset: float = 15.0
    angle_arc_offset: float = 12.0
    point_label_offset: float = 12.0
    auto_place_labels: bool = True
    auto_place_measurements: bool = True


@dataclass
class LayoutResult:
    """Result of running the layout engine."""
    adjustments: list[LayoutAdjustment]
    iterations_used: int
    converged: bool
    total_overlaps_resolved: int


@dataclass
class LayoutAdjustment:
    """A single label/measurement position adjustment."""
    primitive_id: str
    original_x: float
    original_y: float
    adjusted_x: float
    adjusted_y: float
    delta_x: float
    delta_y: float


class LayoutEngine:
    """Automatically positions labels, measurements, and tick marks
    to avoid overlap.

    Uses a simple iterative repulsion algorithm:
    1. Place each label at its ideal position.
    2. Detect overlapping bounding boxes.
    3. Push overlapping labels apart.
    4. Repeat until convergence or max iterations.
    """

    def __init__(self, config: LayoutConfig | None = None) -> None:
        self.config = config or LayoutConfig()

    def layout(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None = None,
    ) -> LayoutResult:
        adjustments: list[LayoutAdjustment] = []
        labels = self._collect_labels(template, variables)

        if not labels:
            return LayoutResult(adjustments, 0, True, 0)

        resolved = 0
        for iteration in range(self.config.max_iterations):
            overlaps = self._find_overlaps(labels)
            if not overlaps:
                return LayoutResult(adjustments, iteration + 1, True, resolved)

            for i, j in overlaps:
                lab_i = labels[i]
                lab_j = labels[j]
                dx = lab_j.cx - lab_i.cx
                dy = lab_j.cy - lab_i.cy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 0.001:
                    dx, dy = 1.0, 1.0
                    dist = math.sqrt(2.0)

                overlap_x = (
                    min(lab_i.xmax, lab_j.xmax)
                    - max(lab_i.xmin, lab_j.xmin)
                )
                overlap_y = (
                    min(lab_i.ymax, lab_j.ymax)
                    - max(lab_i.ymin, lab_j.ymin)
                )

                push_x = overlap_x * (dx / dist) * self.config.repulsion_strength
                push_y = overlap_y * (dy / dist) * self.config.repulsion_strength

                lab_i.x -= push_x
                lab_i.y -= push_y
                lab_j.x += push_x
                lab_j.y += push_y

                resolved += 2

        return LayoutResult(adjustments, self.config.max_iterations, False, resolved)

    def _collect_labels(
        self,
        template: DiagramTemplate,
        variables: dict[str, Any] | None,
    ) -> list[_LayoutLabel]:
        labels: list[_LayoutLabel] = []
        points = template.points_dict(variables)

        for prim in template.primitives:
            if isinstance(prim, TextLabel):
                font_size = prim.font.size if prim.font else self.config.default_font_size
                w = len(prim.text) * font_size * 0.6
                h = font_size * 1.2
                x = prim.resolved_x(variables) - w / 2
                y = prim.resolved_y(variables) - h / 2
                labels.append(_LayoutLabel(
                    primitive_id=prim.id,
                    x=x, y=y, width=w, height=h,
                ))

            elif isinstance(prim, Point) and prim.label:
                px = prim.resolved_x(variables)
                py = prim.resolved_y(variables)
                fs = self.config.default_font_size
                w = len(prim.label) * fs * 0.6
                h = fs * 1.2
                label_x = px - w / 2
                label_y = py - self.config.point_label_offset - h / 2
                labels.append(_LayoutLabel(
                    primitive_id=f"{prim.id}_label",
                    x=label_x, y=label_y, width=w, height=h,
                ))

            elif isinstance(prim, Measurement):
                target = template.get_primitive(prim.primitive_ref)
                if target is None:
                    continue
                from .primitives import Line
                if not isinstance(target, Line):
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
                fs = prim.font.size if prim.font else self.config.default_font_size
                label_text = prim.label
                val = prim.resolved_value(variables)
                if val is not None:
                    label_text = f"{label_text} = {val}"
                w = len(str(label_text)) * fs * 0.6
                h = fs * 1.2
                labels.append(_LayoutLabel(
                    primitive_id=prim.id,
                    x=lx - w / 2, y=ly - h / 2,
                    width=w, height=h,
                ))

        return labels

    def _find_overlaps(
        self, labels: list[_LayoutLabel],
    ) -> list[tuple[int, int]]:
        overlaps: list[tuple[int, int]] = []
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                if labels[i].overlaps(labels[j]):
                    overlaps.append((i, j))
        return overlaps


class _LayoutLabel:
    """Internal mutable label representation for layout calculations."""
    def __init__(
        self,
        primitive_id: str,
        x: float, y: float,
        width: float, height: float,
    ) -> None:
        self.primitive_id = primitive_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def xmin(self) -> float:
        return self.x

    @property
    def xmax(self) -> float:
        return self.x + self.width

    @property
    def ymin(self) -> float:
        return self.y

    @property
    def ymax(self) -> float:
        return self.y + self.height

    @property
    def cx(self) -> float:
        return self.x + self.width / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.height / 2.0

    def overlaps(self, other: _LayoutLabel) -> bool:
        return (
            self.xmin < other.xmax
            and self.xmax > other.xmin
            and self.ymin < other.ymax
            and self.ymax > other.ymin
        )
