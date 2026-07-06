# BoostAI Content Pipeline — Validation Report

**PDF**: `11 - p1h-june-2024.pdf` (Pearson Edexcel GCSE Maths 1MA1/1H, Paper 1 Higher Tier)
**Date**: 2026-07-06
**Pages**: 24 | **Questions**: 23 | **Expected Diagrams**: 9+ | **Detected**: 27 (all false positives)

---

## 1. Page Rendering — FAIL

| Check | Result |
|-------|--------|
| Every page exists | PASS — 24/24 pages rendered |
| Total pages match PDF | PASS — PDF has 24 pages |
| Images are readable | PASS — 300 DPI, 2481×3508 px |
| Mathematical symbols preserved | WARNING — π, °, ≤, ≥ preserved; superscripts lost |
| Resolution sufficient | PASS |

**Issues**:
- No issues with rendering itself. All 24 pages rendered at 300 DPI correctly.

---

## 2. Question Detection — PASS (with issues)

| Check | Result |
|-------|--------|
| Question count | PASS — 23 detected, matches PDF |
| Question numbering | PASS — Q1–Q23 all present, sequential |
| Missing questions | PASS — none missing |
| Duplicate questions | PASS — none duplicated |
| Page numbers | PASS — each question starts on correct page |
| Question text completeness | WARNING — see below |

**Issues**:
1. **Noise characters**: `` (U+F0A2) appears throughout extracted text — these are PDF Private Use Area font artifacts that should be stripped.
2. **Superscript/subscript lost**: `m²` → `m\n2`, `x³` → `x\n3`, `cm²` → `cm\n2` — the superscript is extracted as a separate newline.
3. **Answer-dot noise**: Some answer space dots (`........`) are preserved as text.
4. **Question type misclassification**: Q3 labelled "proof" instead of "computation".

---

## 3. Manual Question Comparison — PASS (with formatting issues)

| Question | Text Matches | Missing Equations | Missing Symbols | Truncated |
|----------|-------------|-------------------|-----------------|-----------|
| Q3 (floor plan) | YES | No | No (m² is on separate line) | No — 501 chars, both (a) and (b) present |
| Q6 (coordinate grid) | YES | No | No | No — 251 chars |
| Q12 (graphs) | YES | y=x²–4 extracted as "y = x\n2 – 4" | No | No — 220 chars |
| Q15 (sector) | YES | No — π preserved | No | No — 272 chars |
| Q23 (circle/line) | YES | No | No | No — 340 chars |

**Issue**: Formatting is correct at the word level, but mathematical notation is broken by newlines wherever superscripts/subscripts were used in the PDF.

---

## 4. Diagram Crop Inspection — FAIL

| Check | Result |
|-------|--------|
| Actual mathematical figures | FAIL — 0/27 are mathematical diagrams |
| Plain text regions | FAIL — every crop is a horizontal text strip from the cover page |
| Page margins | FAIL — some crops include margin borders |
| Answer spaces | FAIL — not answer spaces but text/form labels |
| Page header | FAIL — some crops are header text |
| Footer | FAIL — one crop is the footer area |

**Counts**:
- **Correct diagrams**: 0/27 (0%)
- **False positives**: 27/27 (100%) — all from cover page
- **Missed diagrams**: 9+ (floor plan, Venn, grid, 2× triangles, 8× graphs, histogram, sector, sin axes)

All 27 crops are thin horizontal strips (39–218 px tall, 166–908 px wide) containing text from the cover page's candidate information fields and instructions. None are mathematical figures.

---

## 5. Expected vs Actual Diagrams — FAIL

| Question | Expected Diagram | Detected |
|----------|-----------------|----------|
| Q3 | Floor plan | MISSED |
| Q4 | Venn diagram | MISSED |
| Q6 | Coordinate grid + line L | MISSED |
| Q11 | Triangle on grid | MISSED |
| Q12 | 8× function graphs (A–J) | MISSED |
| Q13 | Histogram grid | MISSED |
| Q15 | Sector of circle | MISSED |
| Q19 | Triangle diagram | MISSED |
| Q22 | sin x° axes | MISSED |

**0 out of 9+ diagrams correctly detected. 27 false positives detected on the cover page.**

---

## 6. diagram_metadata.json — FAIL

| Check | Result |
|-------|--------|
| Question mapping | FAIL — all mapped to wrong questions (the Y-split heuristic on page 1 vs questions on pages 2–23 is fundamentally wrong) |
| Diagram paths | PASS — all 27 paths are valid files |
| Types | FAIL — all classified as "geometry", none are diagrams |
| Page numbers | FAIL — all show page 1, should be on pages 4, 6, 8, 12, 13, 14, 16, 19, 22 |
| Image dimensions | PASS — width/height accurate |

---

## 7. diagram_paths in raw_questions.json — PASS (files exist, content wrong)

All referenced files exist on disk. However, they point to false-positive text crops, not actual diagrams.

---

## 8. Numerical Scores

| Stage | Score |
|-------|-------|
| Pages | PASS (100%) |
| Question Detection | PASS (85%) — 23/23 found, minor formatting issues |
| Question Mapping | FAIL (39%) — 9/23 questions assigned false diagram paths |
| Diagram Detection | FAIL (0%) — 0/9+ real diagrams detected |
| Diagram Mapping | FAIL (0%) — all 27 crops mapped to wrong questions |
| Metadata | FAIL (40%) — page numbers wrong, types wrong, questions wrong |

**Overall Score: 15/100**

---

## Root Cause Analysis

### Issue 1: DiagramDetector detects zero real diagrams

- **File**: `src/detector/diagram_detector.py`
- **Class**: `DiagramDetector`
- **Method**: `_find_candidate_regions()` (line 108)
- **Root cause**: Uses Canny edge detection → dilation → morphological closing → contour finding. Mathematical diagrams in this PDF are thin line art (1 px at 300 DPI). These form edge pixels but do NOT form connected contours after dilation with kernel_size=5. The min region area threshold (10000 px² = ~1.15% of page area) is far too large for individual diagram components (a coordinate grid line might be 1×1000 px = 1000 px², well below threshold). The only contours that pass are page-layout elements: the main content area, footer, and margin sidebars. The margin/footer regions are then filtered by `is_in_margin()`.

### Issue 2: Cover page triggers 27 false positives

- **File**: `src/detector/diagram_detector.py`
- **Class**: `DiagramDetector`
- **Method**: `_score_regions()` (line 138)
- **Root cause**: The cover page has thick layout boxes (candidate name fields, exam details) with strong, connected edges. These create contours that pass the size filter AND the scoring function. The scoring weights (edge density 0.4, line density 0.3, circle score 0.2, aspect ratio 0.1) assign high scores to these text+box regions because they have high edge density and line counts. The scoring system has no mechanism to distinguish text/layout from mathematical diagrams.

### Issue 3: False positives assigned to random questions

- **File**: `src/mapper/question_mapper.py`
- **Class**: `QuestionMapper`
- **Method**: `_assign_crops_to_questions()` (line 75)
- **Root cause**: All 27 crops are on page 1. Questions start on page 2. The page-based grouping fails (`crops_by_page[1]` has crops, but `questions_by_page[1]` is empty). The fallback `if not page_questions: page_questions = [q for q in questions]` assigns ALL questions as if they were on page 1. Then `crop_cy / segment_height` maps crop Y-coordinates from page 1's layout onto questions 1–23, producing random assignments. Example: a crop at y=2248 on the cover page maps to question 11 (wrong).

### Issue 4: Text extraction loses superscript formatting

- **File**: `src/extractor/text_extractor.py`
- **Class**: `TextExtractor`
- **Method**: `extract()` (line 16)
- **Root cause**: PyMuPDF's `get_text()` extracts superscript characters as separate text runs positioned above the baseline. These are output on separate logical lines by PyMuPDF, so "m²" becomes "m\n2". There is no post-processing to detect and re-join superscript/subscript text.

### Issue 5: PDF font artifacts in extracted text

- **File**: `src/detector/question_detector.py`
- **Class**: `QuestionDetector`
- **Method**: `_check_noise()` (line 86)
- **Root cause**: The `` character (U+F0A2) is a Private Use Area glyph from the PDF's custom font encoding. It appears in the extracted text where the PDF uses answer-dot patterns. The noise filter only handles `?`, `*`, dots, underscores, and known exam instructions. U+F0A2 is not matched by any noise pattern and passes through into the question text.

---

## Answers to Final Questions

### 1. Is this pipeline reliable enough for production?

**NO.** The diagram detection is completely non-functional for this type of mathematical PDF. It produces 100% false positives on the cover page and 0% true positives on all other pages. The question text extraction works at 85% but has formatting issues that would break any downstream template engine that expects clean mathematical notation.

### 2. Would you trust it to process 1000 mathematics PDFs?

**Absolutely not.** The diagram detection failure is systematic — it will fail on every PDF whose diagrams are thin line art (which is virtually all GCSE/A-level maths papers). The cover page detection pattern (boxes = false positive diagrams) will trigger on every exam paper's front page. The question text formatting issues (broken superscripts, noise characters) will accumulate across 1000 PDFs, requiring massive manual cleanup.

### 3. What are the top five weaknesses?

1. **Diagram detection algorithm** — contour-based approach is fundamentally wrong for line-art mathematical diagrams. It only finds page layout elements, not actual figures.
2. **False positive rate** — 27 false positives from cover page vs 0 true positives from 9+ pages with actual diagrams. The system has no way to reject non-diagram regions.
3. **Scoring heuristic** — the weighted scoring system (edge density, line density, circles, aspect ratio) cannot distinguish between a text paragraph and a coordinate grid. Both have similar edge/line profiles.
4. **Diagram-to-question mapper** — the Y-coordinate ratio-based mapping assumes diagrams and questions are on the same page with uniform spacing. When crops are on a different page than questions, the mapping completely breaks.
5. **Text formatting** — no superscript/subscript recovery, no cleanup of PDF font artifacts. The extracted text would require significant manual editing before it could be used in templates.

### 4. What should be improved before building the Question Template Engine?

**Critical (blocking):**
1. Replace the diagram detection approach entirely. Consider: (a) extracting embedded vector graphics from the PDF, (b) using ML-based figure detection, (c) region proposal with HOG + SVM, (d) sliding-window edge density analysis with smarter classification.
2. Add a rejection system for non-diagram regions (text classifiers, layout analysis).
3. Fix the diagram-to-question mapper to handle cross-page crops correctly.

**Important:**
4. Add post-processing to repair superscript/subscript formatting in extracted text.
5. Add PDF font artifact cleanup (strip U+F0A2 and similar private-use characters).
6. Expand the noise filter patterns to cover more PDF artifacts.

### 5. Should we move to the next phase, or continue improving this pipeline?

**Continue improving this pipeline.** The Question Template Engine depends on:
- Correct question text (with proper mathematical notation)
- Correct diagram positioning and cropping
- Accurate question-to-diagram associations

The current pipeline fails on all three. Building a template engine on top of this data would produce incorrect templates that require manual rework for every single question with a diagram. Do not proceed until:
1. Diagram detection has been fundamentally reworked and validated against at least 10 diverse maths PDFs.
2. Text extraction cleanly handles superscripts/subscripts.
3. The mapper correctly associates diagrams with the right questions.
4. False positive rate for diagrams is below 10%.
5. True positive rate for diagrams is above 90%.

**Minimum acceptable threshold before next phase: 70/100 overall score.**
