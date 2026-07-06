from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import fitz

from src.pdf_objects.layout_analyzer import TextBlock, PageLayoutCollection

logger = logging.getLogger(__name__)


@dataclass
class QuestionRegion:
    question_number: str
    page_number: int
    y_start: float
    y_end: float
    x_start: float = 35.0
    x_end: float = 575.0
    text_blocks: list[TextBlock] = field(default_factory=list)

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        return (self.x_start, self.y_start, self.x_end, self.y_end)

    def contains_y(self, y: float, margin: float = 5.0) -> bool:
        return (self.y_start - margin) <= y <= (self.y_end + margin)

    def contains_bbox(self, bbox: tuple[float, float, float, float], margin: float = 10.0) -> bool:
        _, y0, _, y1 = bbox
        return self.contains_y(y0, margin) or self.contains_y(y1, margin)


class QuestionRegionMapper:
    QUESTION_START_PATTERNS = [
        re.compile(r"^(\d+)\s*\t"),
        re.compile(r"^Question\s+(\d+)"),
        re.compile(r"^Q\s*(\d+)"),
        re.compile(r"^(\d+)\s*\)"),
        re.compile(r"^(\d+)\s*\."),
    ]

    BOUNDARY_PATTERNS = [
        re.compile(r"^\(?Total\s+for\s+Question\b", re.IGNORECASE),
        re.compile(r"^Turn\s+over\b", re.IGNORECASE),
        re.compile(r"^TOTAL\s+FOR\s+PAPER\b", re.IGNORECASE),
        re.compile(r"^BLANK\s+PAGE\b", re.IGNORECASE),
    ]

    def map_regions(
        self,
        doc: fitz.Document,
        questions: list,
        layouts: PageLayoutCollection,
    ) -> list[QuestionRegion]:
        questions_by_page: dict[int, list] = {}
        for q in questions:
            page_num = q.page_number
            if page_num not in questions_by_page:
                questions_by_page[page_num] = []
            questions_by_page[page_num].append(q)

        regions: list[QuestionRegion] = []

        for page_num in sorted(questions_by_page.keys()):
            page_questions = questions_by_page[page_num]
            page_layout = layouts.get(page_num)
            page_text = self._get_page_text(doc, page_num)

            page_regions = self._map_page_regions(
                page_num, page_questions, page_text, page_layout.text_blocks
            )
            regions.extend(page_regions)

        logger.info("Mapped %d question regions", len(regions))
        return regions

    def _get_page_text(self, doc: fitz.Document, page_num: int) -> str:
        page = doc[page_num - 1]
        return page.get_text()

    def _map_page_regions(
        self,
        page_num: int,
        questions: list,
        raw_text: str,
        text_blocks: list[TextBlock],
    ) -> list[QuestionRegion]:
        raw_lines = raw_text.split("\n")
        stripped_lines = [line.strip() for line in raw_lines]

        question_positions: list[tuple[str, int]] = []
        boundary_positions: list[int] = []

        for idx, line in enumerate(stripped_lines):
            for pattern in self.QUESTION_START_PATTERNS:
                m = pattern.match(line)
                if m:
                    qnum = m.group(1)
                    for q in questions:
                        if q.number == qnum:
                            question_positions.append((qnum, idx))
                            break
                    break

            for pattern in self.BOUNDARY_PATTERNS:
                if pattern.match(line):
                    boundary_positions.append(idx)
                    break

        if not question_positions:
            return self._fallback_regions(page_num, questions, text_blocks)

        question_positions.sort(key=lambda x: x[1])

        regions: list[QuestionRegion] = []
        for i, (qnum, start_line) in enumerate(question_positions):
            if i + 1 < len(question_positions):
                _, next_start = question_positions[i + 1]
                end_line = next_start
            else:
                end_line = len(stripped_lines)

            for bp in sorted(boundary_positions):
                if start_line < bp < end_line:
                    end_line = bp
                    break

            start_y = self._y_at_line(text_blocks, raw_lines, start_line)
            end_y = self._y_at_line(text_blocks, raw_lines, end_line)

            if end_y <= start_y:
                end_y = start_y + 50

            region = QuestionRegion(
                question_number=qnum,
                page_number=page_num,
                y_start=start_y,
                y_end=end_y,
                text_blocks=[tb for tb in text_blocks if self._block_in_range(tb, start_y, end_y)],
            )
            regions.append(region)

        return regions

    def _fallback_regions(
        self,
        page_num: int,
        questions: list,
        text_blocks: list[TextBlock],
    ) -> list[QuestionRegion]:
        if not text_blocks:
            return [
                QuestionRegion(
                    question_number=q.number,
                    page_number=page_num,
                    y_start=50.0,
                    y_end=800.0,
                )
                for q in questions
            ]

        first_y = min(tb.bbox[1] for tb in text_blocks)
        last_y = max(tb.bbox[3] for tb in text_blocks)

        num_questions = len(questions)
        segment = (last_y - first_y) / num_questions if num_questions > 0 else 700

        regions = []
        for i, q in enumerate(sorted(questions, key=lambda x: int(x.number))):
            y0 = first_y + i * segment
            y1 = y0 + segment if i < num_questions - 1 else last_y
            regions.append(
                QuestionRegion(
                    question_number=q.number,
                    page_number=page_num,
                    y_start=y0,
                    y_end=y1,
                    text_blocks=[
                        tb
                        for tb in text_blocks
                        if self._block_in_range(tb, y0, y1)
                    ],
                )
            )
        return regions

    def _y_at_line(
        self, text_blocks: list[TextBlock], raw_lines: list[str], line_idx: int
    ) -> float:
        if line_idx < len(raw_lines):
            line_text = raw_lines[line_idx].strip()
            for tb in text_blocks:
                if line_text in tb.text or tb.text.startswith(line_text):
                    return tb.bbox[1]
            for tb in text_blocks:
                if line_text[:10] in tb.text:
                    return tb.bbox[1]
        return 50.0 + line_idx * 15.0

    def _block_in_range(
        self, block: TextBlock, y_start: float, y_end: float, margin: float = 10.0
    ) -> bool:
        y_mid = (block.bbox[1] + block.bbox[3]) / 2
        return (y_start - margin) <= y_mid <= (y_end + margin)
