from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz

logger = logging.getLogger(__name__)


@dataclass
class DrawingObject:
    page_number: int
    bbox: tuple[float, float, float, float]
    items: list[Any] = field(default_factory=list)
    item_count: int = 0
    stroke: bool = False
    fill: bool = False
    stroke_width: float | None = None
    drawing_type: str = "stroke"

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return (
            (self.bbox[0] + self.bbox[2]) / 2,
            (self.bbox[1] + self.bbox[3]) / 2,
        )

    def contains(self, other: DrawingObject) -> bool:
        return (
            self.bbox[0] <= other.bbox[0]
            and self.bbox[1] <= other.bbox[1]
            and self.bbox[2] >= other.bbox[2]
            and self.bbox[3] >= other.bbox[3]
        )


class DrawingExtractor:
    PAGE_WIDTH = 595.0
    PAGE_HEIGHT = 842.0

    CONTENT_X0 = 50
    CONTENT_X1 = 560
    CONTENT_Y0 = 50
    CONTENT_Y1 = 780

    MIN_DIAGRAM_DIMENSION = 15.0
    MIN_DIAGRAM_ITEMS = 2
    PAGE_BORDER_THRESHOLD = 0.7
    PAGE_WIDTH = 595.0
    PAGE_HEIGHT = 842.0
    MIN_DRAWING_AREA = 100.0

    LAYOUT_RECT = (35.0, 36.4, 560.3, 794.1)

    def extract(self, page: fitz.Page) -> list[DrawingObject]:
        page_num = page.number + 1
        raw_drawings = page.get_drawings()
        logger.debug(
            "Page %d: %d raw drawings found", page_num, len(raw_drawings)
        )

        result: list[DrawingObject] = []
        for raw in raw_drawings:
            obj = self._convert(page_num, raw)
            if obj and self._is_diagram_candidate(obj):
                result.append(obj)

        logger.debug(
            "Page %d: %d diagram candidate drawings", page_num, len(result)
        )
        return result

    def _convert(self, page_num: int, raw: dict) -> DrawingObject | None:
        rect = raw.get("rect")
        if not rect:
            return None

        items = raw.get("items", [])
        return DrawingObject(
            page_number=page_num,
            bbox=(rect.x0, rect.y0, rect.x1, rect.y1),
            items=items,
            item_count=len(items),
            stroke=raw.get("stroke") is not None,
            fill=raw.get("fill") is not None,
            stroke_width=raw.get("width"),
            drawing_type=raw.get("type", "s"),
        )

    def _is_diagram_candidate(self, obj: DrawingObject) -> bool:
        if self._is_page_border(obj):
            return False

        if obj.width < self.MIN_DIAGRAM_DIMENSION and obj.height < self.MIN_DIAGRAM_DIMENSION:
            return False

        if obj.item_count < self.MIN_DIAGRAM_ITEMS and obj.area < 500:
            return False

        if obj.area < self.MIN_DRAWING_AREA and obj.item_count < 3:
            return False

        if obj.bbox[0] < self.CONTENT_X0 and obj.bbox[2] < self.CONTENT_X0 + 20:
            return False
        if obj.bbox[2] > self.CONTENT_X1 and obj.bbox[0] > self.CONTENT_X1 - 20:
            return False
        if obj.bbox[3] > self.CONTENT_Y1 and obj.bbox[1] > self.CONTENT_Y1 - 20:
            return False

        return True

    def _is_page_border(self, obj: DrawingObject) -> bool:
        page_area = self.PAGE_WIDTH * self.PAGE_HEIGHT
        obj_area = obj.area
        if obj_area > page_area * self.PAGE_BORDER_THRESHOLD:
            return True
        lx, ly, rx, ry = self.LAYOUT_RECT
        ox0, oy0, ox1, oy1 = obj.bbox
        overlap_x = max(0, min(rx, ox1) - max(lx, ox0))
        overlap_y = max(0, min(ry, oy1) - max(ly, oy0))
        overlap_area = overlap_x * overlap_y
        layout_area = (rx - lx) * (ry - ly)
        if layout_area > 0 and overlap_area / layout_area > 0.8:
            if obj.item_count <= 10:
                return True
        return False

    def extract_all(self, doc: fitz.Document) -> dict[int, list[DrawingObject]]:
        result: dict[int, list[DrawingObject]] = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            drawings = self.extract(page)
            if drawings:
                result[page_num + 1] = drawings
        return result
