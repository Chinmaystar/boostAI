import os
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
PDF_DIR = INPUT_DIR / "pdfs"

OUTPUT_DIR = BASE_DIR / "output"
PAGES_DIR = OUTPUT_DIR / "pages"
DIAGRAMS_DIR = OUTPUT_DIR / "diagrams"
RAW_JSON_DIR = OUTPUT_DIR / "raw-json"
TEMPLATES_DIR = OUTPUT_DIR / "templates"
METADATA_DIR = OUTPUT_DIR / "metadata"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = OUTPUT_DIR / "logs"


def get_per_pdf_output_dir(pdf_path: Path) -> Path:
    """Derive a unique per-PDF output folder from the PDF filename.

    Creates: output/<sanitized_filename>/
    If the folder already exists, appends a timestamp suffix to avoid overwrites.
    """
    stem = pdf_path.stem
    folder_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", stem).strip("_")
    if not folder_name:
        folder_name = "pdf"

    pdf_output = OUTPUT_DIR / folder_name
    if not pdf_output.exists():
        return pdf_output

    timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
    pdf_output = OUTPUT_DIR / f"{folder_name}{timestamp}"
    return pdf_output


def make_per_pdf_dirs(pdf_output: Path) -> dict[str, Path]:
    """Create and return per-PDF subdirectory paths."""
    subdirs = {
        "root": pdf_output,
        "pages": pdf_output / "pages",
        "diagrams": pdf_output / "diagrams",
        "raw_json": pdf_output / "raw-json",
        "metadata": pdf_output / "metadata",
        "reports": pdf_output / "reports",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return subdirs

RENDER_DPI = 300
RENDER_FORMAT = "png"
RENDER_FMT = RENDER_FORMAT

PAGE_IMAGE_PREFIX = "page"
PAGE_IMAGE_TEMPLATE = f"{PAGE_IMAGE_PREFIX}_%03d.{RENDER_FMT}"

DIAGRAM_PREFIX = "diagram"
DIAGRAM_TEMPLATE = f"{DIAGRAM_PREFIX}_q%s_%d.{RENDER_FMT}"

RAW_QUESTIONS_FILENAME = "raw_questions.json"
DIAGRAM_METADATA_FILENAME = "diagram_metadata.json"
REPORT_FILENAME = "extraction_report.txt"

LOG_FILENAME = "pipeline.log"

QUESTION_PATTERNS = [
    r"^(\d+)\s*\.",
    r"^(\d+)\s*\)",
    r"^Q(?:uestion)?\s*(\d+)",
    r"^(\d+)\s*\[",
]

QUESTION_TYPE_KEYWORDS = {
    "computation": ["solve", "find", "calculate", "evaluate", "determine", "compute", "simplify", "expand", "factorise", "factorize"],
    "proof": ["prove", "show", "hence", "deduce", "verify", "demonstrate"],
    "construction": ["draw", "construct", "sketch", "plot", "graph", "complete"],
    "explanation": ["explain", "describe", "state", "write", "give", "list", "name", "identify"],
    "diagram": ["diagram", "figure", "graph", "sketch"],
    "application": ["apply", "use", "using", "express"],
}

OPENCV_MIN_REGION_AREA = 10000
OPENCV_MAX_REGION_AREA_RATIO = 0.6
OPENCV_CANNY_THRESHOLD1 = 50
OPENCV_CANNY_THRESHOLD2 = 150
OPENCV_DILATION_KERNEL_SIZE = 5
OPENCV_DILATION_ITERATIONS = 2
OPENCV_MORPH_CLOSE_KERNEL_SIZE = 7
OPENCV_MIN_LINE_LENGTH = 80
OPENCV_HOUGH_THRESHOLD = 100
OPENCV_TABLE_LINE_THRESHOLD = 20
OPENCV_CIRCLE_DP = 1.2
OPENCV_CIRCLE_MIN_DIST = 50
OPENCV_CIRCLE_PARAM1 = 100
OPENCV_CIRCLE_PARAM2 = 30
OPENCV_CIRCLE_MIN_RADIUS = 10
OPENCV_CIRCLE_MAX_RADIUS = 500
OPENCV_MARGIN_FRACTION = 0.03
OPENCV_DIAGRAM_SCORE_THRESHOLD = 0.3
OPENCV_EDGE_DENSITY_WEIGHT = 0.4
OPENCV_LINE_DENSITY_WEIGHT = 0.3
OPENCV_CIRCLE_SCORE_WEIGHT = 0.2
OPENCV_ASPECT_RATIO_WEIGHT = 0.1
OPENCV_TABLE_SCORE_WEIGHT = 0.3
OPENCV_MIN_EDGE_DENSITY = 0.05

# ---------------------------------------------------------------------------
# Diagram crop configuration
# ---------------------------------------------------------------------------

# Whitespace padding around the final crop bbox (PDF points)
CROP_WHITESPACE_MARGIN = 12.0

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"

OCR_LANGUAGES = "eng"
OCR_DPI = 300

SUPPORTED_EXTENSIONS = {".pdf"}
