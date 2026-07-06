import re
import logging
import config

logger = logging.getLogger(__name__)


class QuestionInfo:
    """Represents a single detected question."""

    def __init__(
        self,
        number: str,
        text: str,
        page_number: int,
        question_type: str = "",
    ):
        self.number = number
        self.text = text
        self.page_number = page_number
        self.question_type = question_type
        self.diagram_ids: list[str] = []

    def to_dict(self) -> dict:
        return {
            "id": "",
            "question_number": self.number,
            "page_number": self.page_number,
            "question_type": self.question_type,
            "question_text": self.text,
            "diagram_ids": list(self.diagram_ids),
        }


class QuestionDetector:
    """Detects questions from extracted page text using multiple strategies.

    Strategy:
    1. Normalize and filter noise from raw page text.
    2. Split each page into chunks at natural boundary markers
       (e.g. '(Total for Question N is M marks)', 'Turn over').
       Each chunk should contain at most one question start.
    3. Within each chunk, detect the first question start using:
       a. Primary — tab-separated number (Edexcel GCSE format 'N\\t<Title>').
       b. Secondary — number followed by paren/dot patterns (general formats).
       c. Tertiary — bare number on its own line (Edexcel continuation).
    4. Accept only the FIRST detection per chunk, rejecting false positives
       (math expressions, diagram coordinates) that appear mid-question.
    5. Merge multi-page questions by tracking the active question.
    6. Validate detected question numbers against expected sequence.
    """

    # Boundary markers: lines that separate one question from the next.
    BOUNDARY_RE = re.compile(
        r"^\(?Total\s+for\s+Question\b|^Turn\s+over\b|^BLANK\s+PAGE\b|^TOTAL\s+FOR\s+PAPER\b",
        re.IGNORECASE,
    )

    def __init__(self):
        self.main_patterns = [
            re.compile(r"^(\d+)\s*\t"),  # Edexcel: N\t<Title> (primary)
            re.compile(r"^(\d+)\s+\([a-zA-Z0-9]+\)"),  # N (a)/ (i)/ (A)
            re.compile(r"^(\d+)\s*\)"),  # N)
            re.compile(r"^(\d+)\s*\."),  # N.
            re.compile(r"^Question\s+(\d+)"),
            re.compile(r"^Q\s*(\d+)"),
        ]

        self.bare_number_pattern = re.compile(r"^(\d+)\s*$")

        self._noise_cache: dict[str, bool] = {}
        self._boundary_cache: dict[str, bool] = {}

    # ------------------------------------------------------------------
    # Noise filtering
    # ------------------------------------------------------------------

    def _is_noise(self, line: str) -> bool:
        if line in self._noise_cache:
            return self._noise_cache[line]

        result = self._check_noise(line)
        self._noise_cache[line] = result
        return result

    def _check_noise(self, line: str) -> bool:
        if not line:
            return True

        if re.match(
            r"^\**\s*\d*\s*[A-Z]\d{4,}[A-Z0-9]*\s*\**\s*$", line
        ):
            return True

        if re.match(r"^DO NOT WRITE IN THIS AREA", line):
            return True

        if re.match(r"^[\?\*]{2,}\s*$", line):
            return True

        if re.match(r"^[\?\*]\s*$", line):
            return True

        if re.match(r"^Turn\s+over", line, re.IGNORECASE):
            return True

        if re.match(
            r"^\(?Total\s+for\s+Question\b", line, re.IGNORECASE
        ):
            return True

        if re.match(r"^\(?\d+\s*marks?\)?\s*$", line, re.IGNORECASE):
            return True

        # Marks in parentheses: (2), (3) etc. — NOT bare numbers.
        if re.match(r"^\(\d+\)\s*$", line):
            return True

        if re.match(r"^\.{5,}$", line):
            return True

        if re.match(r"^_{5,}$", line):
            return True

        if re.match(r"^BLANK\s+PAGE", line, re.IGNORECASE):
            return True

        return False

    # ------------------------------------------------------------------
    # Boundary detection
    # ------------------------------------------------------------------

    def _is_boundary(self, line: str) -> bool:
        if line in self._boundary_cache:
            return self._boundary_cache[line]
        result = bool(self.BOUNDARY_RE.match(line))
        self._boundary_cache[line] = result
        return result

    def _page_ends_with_boundary(self, raw_text: str) -> bool:
        """Check if a page ends with a boundary marker indicating question closure.

        Scans backwards from the end of the page to find the last meaningful
        (non-noise) line. If that line is a boundary marker, the page cleanly
        ends one or more questions. If not, the page ends mid-question and a
        continuation is expected on the next page.
        """
        raw_lines = raw_text.strip().split("\n")
        for line in reversed(raw_lines):
            stripped = line.strip()
            if not stripped:
                continue
            if self._is_noise(stripped):
                continue
            if self._is_boundary(stripped):
                return True
            if re.match(
                r"^\(?\d+\s*marks?\)?\s*$", stripped, re.IGNORECASE
            ):
                return True
            return False
        return True

    AXIS_LABEL_SEQUENCE_MIN = 3

    def _is_axis_label_sequence(
        self, lines: list[str], start_idx: int
    ) -> bool:
        """Detect sequences of consecutive bare numbers (graph/axis labels).

        If the current line and the next N lines are all bare numbers, this
        is almost certainly an axis/graph label sequence, not a question start.
        Returns True if 3+ consecutive lines starting at start_idx are bare numbers.
        """
        count = 0
        for i in range(start_idx, len(lines)):
            if re.match(r"^\d+\s*$", lines[i]):
                count += 1
                if count >= self.AXIS_LABEL_SEQUENCE_MIN:
                    return True
            else:
                break
        return False

    def _split_into_chunks(self, raw_text: str) -> list[str]:
        """Split page text into chunks at boundary-marker lines.

        Each chunk is expected to contain at most one question start.
        The boundary line itself is discarded (serves as separator).
        """
        raw_lines = raw_text.split("\n")
        chunks: list[str] = []
        current: list[str] = []

        for line in raw_lines:
            stripped = line.strip()
            if self._is_boundary(stripped):
                if current:
                    chunks.append("\n".join(current))
                    current = []
            else:
                current.append(line)

        if current:
            chunks.append("\n".join(current))

        return chunks

    # ------------------------------------------------------------------
    # Line preparation
    # ------------------------------------------------------------------

    def _prepare_lines(self, page_text: str) -> list[str]:
        raw_lines = page_text.split("\n")
        clean: list[str] = []

        for line in raw_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if self._is_noise(stripped):
                continue
            clean.append(stripped)

        return clean

    # ------------------------------------------------------------------
    # Question start detection
    # ------------------------------------------------------------------

    def _match_main_pattern(self, line: str) -> str | None:
        for pattern in self.main_patterns:
            m = pattern.match(line)
            if m:
                return m.group(1)
        return None

    def _is_bare_question_start(
        self,
        line: str,
        all_lines: list[str],
        line_idx: int,
        page_num: int,
        last_question_num: int | None,
        is_first_content_line: bool,
        is_continuation: bool = False,
    ) -> bool:
        m = self.bare_number_pattern.match(line)
        if not m:
            return False

        num = int(m.group(1))

        if is_first_content_line and num == page_num:
            logger.debug(
                "  Skipping bare %d (page number on page %d)", num, page_num
            )
            return False

        if last_question_num is not None and num <= last_question_num:
            logger.debug(
                "  Skipping bare %d (out of sequence, last=%d)",
                num,
                last_question_num,
            )
            return False

        if not self._has_content_ahead(all_lines, line_idx):
            logger.debug(
                "  Skipping bare %d (no content ahead)", num
            )
            return False

        # Reject axis label sequences: 3+ consecutive bare numbers.
        # These are graph/axis tick labels, never question starts.
        if self._is_axis_label_sequence(all_lines, line_idx):
            logger.debug(
                "  Skipping bare %d (axis label sequence, %d consecutive numbers)",
                num, self.AXIS_LABEL_SEQUENCE_MIN,
            )
            return False

        # On a continuation page (previous page ended mid-question),
        # a bare number as the first content line is almost certainly
        # a graph label or diagram value, not a new question.
        if is_continuation and line_idx == 0:
            logger.debug(
                "  Skipping bare %d (continuation page, first content line)", num
            )
            return False

        return True

    def _has_content_ahead(
        self, all_lines: list[str], start_idx: int
    ) -> bool:
        for j in range(start_idx + 1, len(all_lines)):
            candidate = all_lines[j]
            if self._is_noise(candidate):
                continue
            if re.search(r"[a-zA-Z]", candidate):
                return True
            if re.match(r"^\d+\s+\([a-zA-Z]", candidate):
                return True
        return False

    # ------------------------------------------------------------------
    # Page segmentation
    # ------------------------------------------------------------------

    def _segment_page(
        self,
        lines: list[str],
        page_num: int,
        last_q_num: int | None,
        stop_after_first: bool = False,
        is_continuation: bool = False,
    ) -> list[tuple[str | None, list[str]]]:
        starts: dict[int, str] = {}
        is_first = True

        for idx, line in enumerate(lines):
            num = self._match_main_pattern(line)
            if num is not None:
                starts[idx] = num
                is_first = False
                if stop_after_first:
                    break
                continue

            if self._is_bare_question_start(
                line, lines, idx, page_num, last_q_num, is_first,
                is_continuation=is_continuation
            ):
                m = self.bare_number_pattern.match(line)
                starts[idx] = m.group(1)
                is_first = False
                if stop_after_first:
                    break
                continue

            if is_first:
                is_first = False

        return self._build_segments(lines, starts)

    def _build_segments(
        self, lines: list[str], starts: dict[int, str]
    ) -> list[tuple[str | None, list[str]]]:
        if not starts:
            return [(None, list(lines))]

        segments: list[tuple[str | None, list[str]]] = []
        sorted_starts = sorted(starts.items())

        first_idx = sorted_starts[0][0]
        if first_idx > 0:
            segments.append((None, lines[:first_idx]))

        for i, (idx, num) in enumerate(sorted_starts):
            end = (
                sorted_starts[i + 1][0]
                if i + 1 < len(sorted_starts)
                else len(lines)
            )
            segments.append((num, lines[idx:end]))

        return segments

    # ------------------------------------------------------------------
    # Main detection
    # ------------------------------------------------------------------

    def detect(self, pages_text: dict[int, str]) -> list[QuestionInfo]:
        questions: list[QuestionInfo] = []
        last_question_num: int | None = None
        page_ended_with_boundary: bool = True

        for page_num in sorted(pages_text.keys()):
            raw_text = pages_text[page_num]

            is_continuation = not page_ended_with_boundary

            # Split page into chunks at boundary markers.
            # Each chunk should contain at most one question.
            chunks = self._split_into_chunks(raw_text)

            for chunk_idx, chunk_text in enumerate(chunks):
                lines = self._prepare_lines(chunk_text)

                if not lines:
                    continue

                # The first chunk of a continuation page should NOT start a
                # new question from bare numbers. If the previous page ended
                # mid-question, the first content lines are likely graph labels,
                # axis values, or sub-part markers ((c), (d)), not a new question.
                is_continuation_chunk = is_continuation and chunk_idx == 0

                # Within a chunk, accept only the FIRST question detection.
                # This rejects false-positive bare numbers that appear
                # mid-question (math results, diagram coordinates, etc.).
                segments = self._segment_page(
                    lines, page_num, last_question_num, stop_after_first=True,
                    is_continuation=is_continuation_chunk,
                )

                for num, seg_lines in segments:
                    text = "\n".join(seg_lines)

                    if num is not None:
                        qtype = self._classify_type(text)
                        q = QuestionInfo(
                            number=num,
                            text=text,
                            page_number=page_num,
                            question_type=qtype,
                        )
                        questions.append(q)
                        last_question_num = (
                            int(num) if num.isdigit() else last_question_num
                        )
                        logger.info(
                            "  Question %s | Page %d | %d chars",
                            num,
                            page_num,
                            len(text),
                        )
                    else:
                        # Lines before the first question in this chunk
                        # (or entire chunk if no question found).
                        # Append as continuation of the previous question.
                        if questions:
                            prev = questions[-1]
                            prev.text += "\n" + text
                            logger.debug(
                                "  Continuation -> Q%s (page %d, %d chars added)",
                                prev.number,
                                page_num,
                                len(text),
                            )

            page_ended_with_boundary = self._page_ends_with_boundary(raw_text)

        logger.info(
            "Detected %d questions across %d pages",
            len(questions),
            len(pages_text),
        )
        return questions

    # ------------------------------------------------------------------
    # Type classification
    # ------------------------------------------------------------------

    def _classify_type(self, text: str) -> str:
        text_lower = text.lower()
        scores: dict[str, int] = {}

        for qtype, keywords in config.QUESTION_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[qtype] = score

        if not scores:
            return "computation"

        return max(scores, key=scores.get)
