from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

import config

from src.pdf_objects.drawing_extractor import DrawingObject
from src.pdf_objects.image_extractor import ImageObject
from src.pdf_objects.layout_analyzer import TextBlock, PageLayout, PageLayoutCollection
from src.pdf_objects.question_region_mapper import QuestionRegion

logger = logging.getLogger(__name__)


@dataclass
class DiagramFigure:
    id: str
    question_number: str
    page_number: int
    bbox: tuple[float, float, float, float]
    drawing_count: int
    text_labels: list[str] = field(default_factory=list)
    figure_type: str = "diagram"
    drawings: list[DrawingObject] = field(default_factory=list)
    images: list[ImageObject] = field(default_factory=list)

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    def to_metadata(self) -> dict:
        return {
            "id": self.id,
            "question_number": self.question_number,
            "page": self.page_number,
            "type": self.figure_type,
            "bbox": {
                "x": round(self.bbox[0], 1),
                "y": round(self.bbox[1], 1),
                "width": round(self.width, 1),
                "height": round(self.height, 1),
            },
            "drawing_count": self.drawing_count,
            "text_labels": self.text_labels,
            "image_count": len(self.images),
        }


class DiagramAssembler:
    CLUSTER_DISTANCE = 30.0
    MIN_FIGURE_DRAWINGS = 2
    MIN_FIGURE_AREA = 200.0

    FIGURE_TYPE_KEYWORDS: dict[str, list[str]] = {
        "coordinate_grid": ["axis", "grid", "plot"],
        "geometry": ["triangle", "circle", "angle", "polygon", "sector"],
        "graph": ["graph", "curve", "plot"],
        "histogram": ["histogram", "bar chart", "frequency"],
        "venn": ["venn", "set"],
        "diagram": [],
    }

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self._counter: int = 0

    def assemble(
        self,
        page_drawings: dict[int, list[DrawingObject]],
        page_images: dict[int, list[ImageObject]],
        layouts: PageLayoutCollection,
        question_regions: list[QuestionRegion],
        question_lookup: dict[str, Any],
    ) -> list[DiagramFigure]:
        figures: list[DiagramFigure] = []

        for region in question_regions:
            page_num = region.page_number
            drawings = page_drawings.get(page_num, [])
            images = page_images.get(page_num, [])
            layout = layouts.get(page_num)

            if not drawings and not images:
                continue

            region_drawings = self._filter_drawings_in_region(
                drawings, region
            )
            region_images = self._filter_images_in_region(images, region)
            region_texts = layout.text_blocks

            if not region_drawings and not region_images:
                continue

            clusters = self._cluster_drawings(region_drawings)

            for cluster in clusters:
                self._counter += 1
                figure = self._build_figure(
                    cluster, region_images, region_texts, region, page_num
                )
                if figure:
                    figures.append(figure)

        if not figures and page_drawings:
            figures = self._fallback_figures(
                page_drawings, page_images, question_regions, layouts
            )

        logger.info(
            "Assembled %d diagram figures across %d question regions",
            len(figures),
            len(question_regions),
        )
        return figures

    def save_diagram_images(
        self,
        figures: list[DiagramFigure],
        pages_dir: Path,
        layouts: PageLayoutCollection | None = None,
    ) -> list[Path]:
        """Crop each diagram figure from the rendered page image and save to
        ``self.output_dir`` (the per-PDF diagrams/ folder).

        Uses intelligent text-aware cropping when ``layouts`` is provided:
        the crop box is expanded to include nearby text that semantically
        belongs to the figure (vertex labels, measurements, axis values,
        graph labels) while excluding question text, marks, instructions,
        and page decorations.

        Returns a list of saved PNG paths.
        """
        scale = config.RENDER_DPI / 72.0
        saved: list[Path] = []

        for fig in figures:
            page_path = pages_dir / (config.PAGE_IMAGE_TEMPLATE % fig.page_number)
            if not page_path.exists():
                logger.warning("Page image not found: %s", page_path)
                continue

            # Determine crop bbox — either the raw drawing bbox or an
            # intelligently expanded version that includes figure labels.
            if layouts is not None:
                page_layout = layouts.get(fig.page_number)
                text_blocks = page_layout.text_blocks
                crop_bbox = self._compute_intelligent_crop_bbox(
                    fig, text_blocks, scale,
                )
            else:
                crop_bbox = fig.bbox

            # Convert PDF points → pixel coordinates
            x0 = int(crop_bbox[0] * scale)
            y0 = int(crop_bbox[1] * scale)
            x1 = int(crop_bbox[2] * scale)
            y1 = int(crop_bbox[3] * scale)

            # Guard against degenerate boxes
            if x1 <= x0 or y1 <= y0:
                logger.warning(
                    "Skipping degenerate bbox for %s: %s", fig.id, crop_bbox
                )
                continue

            try:
                page_img = Image.open(page_path)
                crop = page_img.crop((x0, y0, x1, y1))
                out_path = self.output_dir / f"{fig.id}.png"
                crop.save(out_path, format="PNG")
                saved.append(out_path)
                logger.debug("Saved diagram crop: %s", out_path)
            except Exception as e:
                logger.error("Failed to crop/save %s: %s", fig.id, e)

        logger.info("Saved %d diagram images to %s", len(saved), self.output_dir)
        return saved

    # ------------------------------------------------------------------
    # Public helpers (used externally)
    # ------------------------------------------------------------------

    @staticmethod
    def bbox_expand(
        bbox: tuple[float, float, float, float],
        margin: float,
    ) -> tuple[float, float, float, float]:
        return (
            bbox[0] - margin,
            bbox[1] - margin,
            bbox[2] + margin,
            bbox[3] + margin,
        )

    @staticmethod
    def bbox_union(
        *bboxes: tuple[float, float, float, float],
    ) -> tuple[float, float, float, float]:
        x0 = min(b[0] for b in bboxes)
        y0 = min(b[1] for b in bboxes)
        x1 = max(b[2] for b in bboxes)
        y1 = max(b[3] for b in bboxes)
        return (x0, y0, x1, y1)

    @staticmethod
    def bbox_intersects(
        a: tuple[float, float, float, float],
        b: tuple[float, float, float, float],
    ) -> bool:
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    @staticmethod
    def bbox_distance(
        a: tuple[float, float, float, float],
        b: tuple[float, float, float, float],
    ) -> float:
        dx = max(a[0], b[0]) - min(a[2], b[2])
        dy = max(a[1], b[1]) - min(a[3], b[3])
        dx = max(dx, 0.0)
        dy = max(dy, 0.0)
        return math.sqrt(dx * dx + dy * dy)

    # ------------------------------------------------------------------
    # Text classification — multi-signal label vs non-label
    # ------------------------------------------------------------------

    _RE_QUESTION_NUM = re.compile(r"^\d+\s*[\t\.\)]")
    _RE_TOTAL_MARKS = re.compile(r"Total for (Question|Paper)", re.IGNORECASE)
    _RE_PAGE_MARKS = re.compile(r"^\(\d+\)$")
    _RE_PAGE_HEADER = re.compile(r"^\*[A-Z0-9]+\*$")
    _RE_DO_NOT_WRITE = re.compile(r"DO\s+NOT\s+WRITE", re.IGNORECASE)
    _RE_BLANK_PAGE = re.compile(r"BLANK\s+PAGE", re.IGNORECASE)
    _RE_TURN_OVER = re.compile(r"Turn\s+over", re.IGNORECASE)
    _RE_DOTS_ONLY = re.compile(r"^[\.\s]+$")
    _RE_PURE_NUMBER = re.compile(r"^-?\d+(\.\d+)?$")
    _RE_MEASUREMENT = re.compile(
        r"^-?\d+\s*(cm|mm|m|km|g|kg|ml|l|°|degrees|minutes|hours|s)$",
        re.IGNORECASE,
    )
    _RE_SINGLE_LETTER = re.compile(r"^[A-Za-z]$")
    _RE_DOUBLE_LETTER = re.compile(r"^[A-Z]{2}$")
    _RE_LETTER_NUM = re.compile(r"^[A-Za-z]_\d+$")
    _RE_ANGLE_MEASURE = re.compile(r"^\d+°$")

    # First words that identify sentence text (not labels)
    _VERB_STARTS = frozenset({
        "find", "work", "calculate", "solve", "write", "show", "give",
        "complete", "draw", "sketch", "expand", "simplify", "rationalise",
        "factorise", "prove", "hence", "using", "determine", "explain",
        "describe", "state", "name", "identify", "evaluate", "make",
        "does", "is", "are", "was", "were", "will", "can", "have", "has",
        "had", "been", "being", "on", "in", "at", "the", "this", "that",
        "these", "those", "there", "here", "a", "an",
    })

    # ---- Content classification ----

    @classmethod
    def _is_hard_excluded(cls, text: str) -> bool:
        """Text that can never be a diagram label."""
        if not text.strip():
            return True
        if cls._RE_DOTS_ONLY.match(text):
            return True
        if cls._RE_PAGE_HEADER.match(text):
            return True
        if cls._RE_BLANK_PAGE.match(text):
            return True
        if cls._RE_TURN_OVER.match(text):
            return True
        if cls._RE_DO_NOT_WRITE.search(text):
            return True
        if cls._RE_PAGE_MARKS.match(text):
            return True
        if cls._RE_TOTAL_MARKS.search(text):
            return True
        if cls._RE_QUESTION_NUM.match(text):
            return True
        return False

    @classmethod
    def _is_strong_label(cls, text: str) -> bool:
        """Unambiguous diagram label — vertex, axis tick, measurement,
        coordinate value, or single-letter annotation."""
        t = text.strip()
        if not t:
            return False
        # Pure number (integer or decimal, optional minus sign)
        if cls._RE_PURE_NUMBER.match(t):
            return True
        # Measurement with unit
        if cls._RE_MEASUREMENT.match(t):
            return True
        # Single letter (vertex or axis label)
        if cls._RE_SINGLE_LETTER.match(t):
            return True
        # Two uppercase letters (edge or set label: AB, CD, PQ)
        if cls._RE_DOUBLE_LETTER.match(t):
            return True
        # Subscript notation (x_1, y_2)
        if cls._RE_LETTER_NUM.match(t):
            return True
        # Angle measurement
        if cls._RE_ANGLE_MEASURE.match(t):
            return True
        return False

    @classmethod
    def _is_label_like(cls, text: str) -> bool:
        """Short atomic text that could be a figure label, but is not
        as unambiguous as _is_strong_label.

        Examples: ``OAB``, ``sin``, ``Radius``, ``Mean``, ``Total``.
        """
        t = text.strip()
        if not t:
            return False
        # Must be short (≤ 12 chars) and at most 2 words
        if len(t) > 12:
            return False
        words = t.split()
        if len(words) > 2:
            return False
        # Must not start with an instruction verb
        first = words[0].lower()
        if first in cls._VERB_STARTS:
            return False
        # Require at least one letter or digit — excludes PDF extraction
        # artifacts (control characters, Unicode private-use glyphs) that
        # are never valid diagram labels.
        if not re.search(r"[A-Za-z0-9]", t):
            return False
        # Otherwise it's ambiguous — could be a label
        return True

    @classmethod
    def _is_sentence(cls, text: str) -> bool:
        """Text that reads like a question statement or instruction —
        NOT a diagram label."""
        t = text.strip()
        if not t:
            return False
        # Long text is always a sentence
        if len(t) > 50:
            return True
        words = t.split()
        # 4+ words is a sentence
        if len(words) >= 4:
            return True
        # 3 words: check if it starts with instruction verb
        if len(words) == 3:
            first = words[0].lower()
            if first in cls._VERB_STARTS:
                return True
            return False
        # 2 words: check length + verb start
        if len(words) == 2:
            if len(t) > 20 and words[0].lower() in cls._VERB_STARTS:
                return True
            return False
        # Single word — not a sentence
        return False

    # ---- Positional signals ----

    @staticmethod
    def _inside_xrange(
        tb: TextBlock,
        fig: DiagramFigure,
        margin: float = 0.0,
    ) -> bool:
        """Text center x is within drawing x-range (±margin)."""
        cx = (tb.bbox[0] + tb.bbox[2]) / 2
        return (fig.bbox[0] - margin) <= cx <= (fig.bbox[2] + margin)

    @staticmethod
    def _inside_yrange(
        tb: TextBlock,
        fig: DiagramFigure,
        margin: float = 0.0,
    ) -> bool:
        """Text center y is within drawing y-range (±margin)."""
        cy = (tb.bbox[1] + tb.bbox[3]) / 2
        return (fig.bbox[1] - margin) <= cy <= (fig.bbox[3] + margin)

    @staticmethod
    def _is_near_axis_edge(
        tb: TextBlock,
        fig: DiagramFigure,
        axis_threshold: float = 30.0,
    ) -> bool:
        """Text is near the left, right, top, or bottom edge of the
        drawing — a position consistent with axis labels."""
        fx0, fy0, fx1, fy1 = fig.bbox
        cx = (tb.bbox[0] + tb.bbox[2]) / 2
        cy = (tb.bbox[1] + tb.bbox[3]) / 2
        left = abs(cx - fx0) < axis_threshold
        right = abs(cx - fx1) < axis_threshold
        top = abs(cy - fy0) < axis_threshold
        bottom = abs(cy - fy1) < axis_threshold
        return left or right or top or bottom

    # ------------------------------------------------------------------
    # Main classifier — _is_diagram_label
    # ------------------------------------------------------------------

    @classmethod
    def _is_diagram_label(
        cls,
        tb: TextBlock,
        fig: DiagramFigure,
    ) -> bool:
        """Returns True if *tb* is a diagram label that should expand
        the crop box.

        The decision uses multiple signals in a decision-tree:
          1. Hard exclusions (never a label).
          2. Strong chemical labels → include within 120 pt
             (20 pt if the text centre is outside the figure both
             horizontally AND vertically — a strong indicator that
             the text is question-structural, not a diagram annotation).
          3. Sentence text → include ONLY if overlapping the drawing.
          4. Ambiguous label-like text → include within 40 pt
             (15 pt if outside both axes, i.e. likely question text).
          5. Default → include only if overlapping the drawing.
        """
        text = tb.text.strip()
        if not text:
            return False

        # ----- Step 1: Hard exclusions -----
        if cls._is_hard_excluded(text):
            return False

        dist = cls.bbox_distance(tb.bbox, fig.bbox)

        # ---- Outside-both check ----
        cx = (tb.bbox[0] + tb.bbox[2]) / 2.0
        cy = (tb.bbox[1] + tb.bbox[3]) / 2.0
        outside_both = (cx < fig.bbox[0] or cx > fig.bbox[2]) and (
            cy < fig.bbox[1] or cy > fig.bbox[3]
        )

        # ---- Vertical gap check ----
        fx0, fy0, fx1, fy1 = fig.bbox
        tx0, ty0, tx1, ty1 = tb.bbox
        far_vertical = False
        if ty1 < fy0:  # entirely above
            far_vertical = (fy0 - ty1) > 60.0
        elif ty0 > fy1:  # entirely below
            far_vertical = (ty0 - fy1) > 60.0

        # ----- Step 2: Strong label signals -----
        if cls._is_strong_label(text):
            threshold = 20.0 if (outside_both or far_vertical) else 120.0
            return dist <= threshold

        # ----- Step 3: Sentence detection -----
        if cls._is_sentence(text):
            return cls.bbox_intersects(tb.bbox, fig.bbox)

        # ----- Step 4: Label-like ambiguous text -----
        if cls._is_label_like(text):
            if cls._inside_xrange(tb, fig, margin=20.0):
                threshold = 20.0 if (outside_both or far_vertical) else 50.0
                return dist <= threshold
            threshold = 15.0 if (outside_both or far_vertical) else 40.0
            return dist <= threshold

        # ----- Step 5: Default -----
        return cls.bbox_intersects(tb.bbox, fig.bbox)

    # ------------------------------------------------------------------
    # Main crop computation
    # ------------------------------------------------------------------

    def _compute_intelligent_crop_bbox(
        self,
        fig: DiagramFigure,
        text_blocks: list[TextBlock],
        scale: float,
    ) -> tuple[float, float, float, float]:
        """Compute a crop bbox that includes the drawing plus every text
        block classified as a diagram label — no more, no less."""
        fig_bbox = fig.bbox
        page_bbox = (0.0, 0.0, 595.0, 842.0)

        # Start with the drawing bbox (no upfront expansion — expansion is
        # driven by actual label positions, not guesswork).
        crop = list(fig_bbox)

        # Include embedded image bboxes
        for img in fig.images:
            crop = list(self.bbox_union(tuple(crop), img.bbox))

        # Classify every text block and include only those that pass
        for tb in text_blocks:
            if self._is_diagram_label(tb, fig):
                crop = list(self.bbox_union(tuple(crop), tb.bbox))

        # Final whitespace padding
        crop = list(
            self.bbox_expand(tuple(crop), config.CROP_WHITESPACE_MARGIN)
        )

        # Clip to page
        crop[0] = max(crop[0], page_bbox[0])
        crop[1] = max(crop[1], page_bbox[1])
        crop[2] = min(crop[2], page_bbox[2])
        crop[3] = min(crop[3], page_bbox[3])

        return tuple(crop)

    def _filter_drawings_in_region(
        self, drawings: list[DrawingObject], region: QuestionRegion
    ) -> list[DrawingObject]:
        return [
            d
            for d in drawings
            if region.contains_bbox(d.bbox)
        ]

    def _filter_images_in_region(
        self, images: list[ImageObject], region: QuestionRegion
    ) -> list[ImageObject]:
        return [
            img
            for img in images
            if not img.is_side_strip
            and img.is_diagram_size
            and region.contains_bbox(img.bbox)
        ]

    def _cluster_drawings(
        self, drawings: list[DrawingObject]
    ) -> list[list[DrawingObject]]:
        if not drawings:
            return []

        if len(drawings) <= 2:
            return [drawings]

        clusters: list[list[DrawingObject]] = []
        used = [False] * len(drawings)

        for i, d1 in enumerate(drawings):
            if used[i]:
                continue

            cluster = [d1]
            used[i] = True
            c_bbox = list(d1.bbox)

            changed = True
            while changed:
                changed = False
                for j, d2 in enumerate(drawings):
                    if used[j]:
                        continue
                    if self._is_near(c_bbox, d2.bbox):
                        cluster.append(d2)
                        used[j] = True
                        c_bbox = self._merge_bbox(c_bbox, d2.bbox)
                        changed = True

            clusters.append(cluster)

        merged_clusters: list[list[DrawingObject]] = []
        used_c = [False] * len(clusters)

        for i, c1 in enumerate(clusters):
            if used_c[i]:
                continue
            merged = list(c1)
            used_c[i] = True
            c_bbox = self._cluster_bbox(merged)

            for j, c2 in enumerate(clusters):
                if used_c[j] or i == j:
                    continue
                c2_bbox = self._cluster_bbox(c2)
                gap = self._bbox_gap(c_bbox, c2_bbox)
                if gap < self.CLUSTER_DISTANCE * 2:
                    merged.extend(c2)
                    used_c[j] = True
                    c_bbox = self._merge_bbox(c_bbox, c2_bbox)

            merged_clusters.append(merged)

        return merged_clusters

    def _is_near(
        self,
        bbox1: tuple[float, float, float, float],
        bbox2: tuple[float, float, float, float],
    ) -> bool:
        gap = self._bbox_gap(bbox1, bbox2)
        return gap < self.CLUSTER_DISTANCE

    def _bbox_gap(
        self,
        bbox1: tuple[float, float, float, float],
        bbox2: tuple[float, float, float, float],
    ) -> float:
        x0_1, y0_1, x1_1, y1_1 = bbox1
        x0_2, y0_2, x1_2, y1_2 = bbox2

        dx = max(x0_1, x0_2) - min(x1_1, x1_2)
        dy = max(y0_1, y0_2) - min(y1_1, y1_2)

        gap_x = max(dx, 0)
        gap_y = max(dy, 0)

        return math.sqrt(gap_x**2 + gap_y**2)

    def _merge_bbox(
        self,
        bbox1: tuple[float, float, float, float],
        bbox2: tuple[float, float, float, float],
    ) -> tuple[float, float, float, float]:
        return (
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        )

    def _cluster_bbox(
        self, cluster: list[DrawingObject]
    ) -> tuple[float, float, float, float]:
        x0 = min(d.bbox[0] for d in cluster)
        y0 = min(d.bbox[1] for d in cluster)
        x1 = max(d.bbox[2] for d in cluster)
        y1 = max(d.bbox[3] for d in cluster)
        return (x0, y0, x1, y1)

    MIN_FIGURE_DIMENSION = 20.0
    MAX_PAGE_COVERAGE = 0.6
    PAGE_WIDTH = 595.0
    PAGE_HEIGHT = 842.0

    def _build_figure(
        self,
        cluster: list[DrawingObject],
        region_images: list[ImageObject],
        region_texts: list[TextBlock],
        region: QuestionRegion,
        page_num: int,
    ) -> DiagramFigure | None:
        if not cluster:
            return None

        c_bbox = self._cluster_bbox(cluster)
        fig_w = c_bbox[2] - c_bbox[0]
        fig_h = c_bbox[3] - c_bbox[1]
        area = fig_w * fig_h

        if fig_w < self.MIN_FIGURE_DIMENSION and fig_h < self.MIN_FIGURE_DIMENSION:
            return None
        if area < self.MIN_FIGURE_AREA and len(cluster) < self.MIN_FIGURE_DRAWINGS:
            return None

        page_area = self.PAGE_WIDTH * self.PAGE_HEIGHT
        if area > page_area * self.MAX_PAGE_COVERAGE:
            return None

        nearby_texts = self._find_nearby_texts(c_bbox, region_texts)
        figure_type = self._classify(cluster, nearby_texts)

        fig_id = f"diag_{self._counter:04d}"

        region_images_in_figure = [
            img
            for img in region_images
            if self._bbox_overlaps(c_bbox, img.bbox)
        ]

        return DiagramFigure(
            id=fig_id,
            question_number=region.question_number,
            page_number=page_num,
            bbox=c_bbox,
            drawing_count=len(cluster),
            text_labels=nearby_texts[:10],
            figure_type=figure_type,
            drawings=cluster,
            images=region_images_in_figure,
        )

    def _find_nearby_texts(
        self,
        fig_bbox: tuple[float, float, float, float],
        text_blocks: list[TextBlock],
        margin: float = 15.0,
    ) -> list[str]:
        results: list[str] = []
        fx0, fy0, fx1, fy1 = fig_bbox

        for tb in text_blocks:
            tx0, ty0, tx1, ty1 = tb.bbox
            if (
                tx0 < fx1 + margin
                and tx1 > fx0 - margin
                and ty0 < fy1 + margin
                and ty1 > fy0 - margin
            ):
                text = tb.text.strip()
                if text and text not in results:
                    results.append(text)

        return results

    def _bbox_overlaps(
        self,
        bbox1: tuple[float, float, float, float],
        bbox2: tuple[float, float, float, float],
    ) -> bool:
        return not (
            bbox1[2] < bbox2[0]
            or bbox1[0] > bbox2[2]
            or bbox1[3] < bbox2[1]
            or bbox1[1] > bbox2[3]
        )

    def _classify(
        self, cluster: list[DrawingObject], nearby_texts: list[str]
    ) -> str:
        text_lower = " ".join(nearby_texts).lower()

        for fig_type, keywords in self.FIGURE_TYPE_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return fig_type

        line_count = 0
        for d in cluster:
            for item in d.items:
                if item[0] == "l":
                    line_count += 1

        circle_count = 0
        for d in cluster:
            for item in d.items:
                if item[0] == "c" or item[0] == "cu":
                    circle_count += 1

        if line_count > 20 and circle_count > 2:
            return "coordinate_grid"
        if circle_count > 3:
            return "geometry"
        if line_count > 10:
            return "graph"

        return "diagram"

    def _fallback_figures(
        self,
        page_drawings: dict[int, list[DrawingObject]],
        page_images: dict[int, list[ImageObject]],
        question_regions: list[QuestionRegion],
        layouts: PageLayoutCollection,
    ) -> list[DiagramFigure]:
        figures: list[DiagramFigure] = []

        for region in question_regions:
            page_num = region.page_number
            drawings = page_drawings.get(page_num, [])
            if not drawings:
                continue

            c_bbox = (
                min(d.bbox[0] for d in drawings),
                min(d.bbox[1] for d in drawings),
                max(d.bbox[2] for d in drawings),
                max(d.bbox[3] for d in drawings),
            )

            self._counter += 1
            fig_id = f"diag_{self._counter:04d}"
            layout = layouts.get(page_num)
            texts = layout.text_blocks if layout else []

            figure = DiagramFigure(
                id=fig_id,
                question_number=region.question_number,
                page_number=page_num,
                bbox=c_bbox,
                drawing_count=len(drawings),
                text_labels=self._find_nearby_texts(c_bbox, texts),
                figure_type="diagram",
                drawings=drawings,
            )
            figures.append(figure)

        return figures
