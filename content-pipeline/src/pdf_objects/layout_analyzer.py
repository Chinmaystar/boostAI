from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import fitz

from src.pdf_objects.drawing_extractor import DrawingObject
from src.pdf_objects.image_extractor import ImageObject

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    page_number: int
    bbox: tuple[float, float, float, float]
    text: str
    font_size: float = 0.0
    font_name: str = ""

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def y_center(self) -> float:
        return (self.bbox[1] + self.bbox[3]) / 2

    @property
    def x_center(self) -> float:
        return (self.bbox[0] + self.bbox[2]) / 2


@dataclass
class PageLayout:
    page_number: int
    text_blocks: list[TextBlock] = field(default_factory=list)
    drawings: list[DrawingObject] = field(default_factory=list)
    images: list[ImageObject] = field(default_factory=list)

    @property
    def has_diagram_content(self) -> bool:
        return bool(self.drawings) or any(
            img.is_diagram_size and not img.is_side_strip for img in self.images
        )


@dataclass
class PageLayoutCollection:
    layouts: dict[int, PageLayout] = field(default_factory=dict)

    def get(self, page_num: int) -> PageLayout:
        return self.layouts.get(page_num, PageLayout(page_number=page_num))

    def add(self, layout: PageLayout) -> None:
        self.layouts[layout.page_number] = layout


class LayoutAnalyzer:
    MARGIN_X0 = 35.0
    MARGIN_X1 = 575.0
    MARGIN_Y0 = 35.0
    MARGIN_Y1 = 810.0

    LAYOUT_BBOX = (MARGIN_X0, MARGIN_Y0, MARGIN_X1, MARGIN_Y1)

    def analyze(
        self,
        doc: fitz.Document,
        page_drawings: dict[int, list[DrawingObject]],
        page_images: dict[int, list[ImageObject]],
    ) -> PageLayoutCollection:
        collection = PageLayoutCollection()

        for page_num in range(len(doc)):
            page = doc[page_num]
            pn = page_num + 1

            text_blocks = self._extract_text_blocks(page, pn)
            drawings = page_drawings.get(pn, [])
            images = page_images.get(pn, [])

            layout = PageLayout(
                page_number=pn,
                text_blocks=text_blocks,
                drawings=drawings,
                images=images,
            )
            collection.add(layout)

            logger.debug(
                "Page %d: %d text blocks, %d drawings, %d images",
                pn,
                len(text_blocks),
                len(drawings),
                len(images),
            )

        logger.info(
            "Analyzed %d pages", len(collection.layouts)
        )
        return collection

    def _extract_text_blocks(
        self, page: fitz.Page, page_num: int
    ) -> list[TextBlock]:
        text_dict = page.get_text("dict")
        blocks: list[TextBlock] = []

        for block in text_dict.get("blocks", []):
            if block.get("type") != 0:
                continue

            bbox = block.get("bbox")
            if not bbox:
                continue

            if not self._is_in_content_area(bbox):
                continue

            full_text = ""
            font_sizes = set()
            font_names = set()

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    full_text += span.get("text", "")
                    font_sizes.add(span.get("size", 0))
                    font_names.add(span.get("font", ""))

            text = full_text.strip()
            if not text:
                continue

            avg_font = max(font_sizes) if font_sizes else 0
            font_name = next(iter(font_names)) if font_names else ""

            tb = TextBlock(
                page_number=page_num,
                bbox=tuple(bbox),
                text=text,
                font_size=avg_font,
                font_name=font_name,
            )
            blocks.append(tb)

        return blocks

    def _is_in_content_area(self, bbox: tuple) -> bool:
        x0, y0, x1, y1 = bbox
        if x1 < self.LAYOUT_BBOX[0] or x0 > self.LAYOUT_BBOX[2]:
            return False
        if y1 < self.LAYOUT_BBOX[1] or y0 > self.LAYOUT_BBOX[3]:
            return False
        return True
