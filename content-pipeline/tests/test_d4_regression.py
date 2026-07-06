"""Tests for the diag_0004 fix: alphanumeric requirement in _is_label_like."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import re
from src.pdf_objects.diagram_assembler import DiagramAssembler, DiagramFigure
from src.pdf_objects.layout_analyzer import TextBlock


def _fig(bbox=(118.9, 101.3, 459.1, 441.5), page=12):
    return DiagramFigure(
        id="diag_test", question_number="11", page_number=page,
        bbox=bbox, drawing_count=1,
    )


def test_control_character_excluded():
    """\\x1b (ESC) must NOT be label_like — it's a PDF extraction artifact."""
    assert not DiagramAssembler._is_label_like("\x1b")
    assert not DiagramAssembler._is_label_like("\x19")
    assert not DiagramAssembler._is_label_like("\x1a")


def test_unicode_artifact_excluded():
    """\\uf0a2 (private use area) must NOT be label_like."""
    assert not DiagramAssembler._is_label_like("\uf0a2\uf0a2")


def test_axis_tick_labels_still_label_like():
    """Tick labels like -6, -5, -4, 123456O must still be label_like."""
    assert DiagramAssembler._is_label_like("–6")
    assert DiagramAssembler._is_label_like("–5")
    assert DiagramAssembler._is_label_like("–4")
    assert DiagramAssembler._is_label_like("–3")
    assert DiagramAssembler._is_label_like("–2")
    assert DiagramAssembler._is_label_like("–1")
    assert DiagramAssembler._is_label_like("–5–6–4–3–2–1")
    assert DiagramAssembler._is_label_like("123456O")


def test_single_letters_still_label_like():
    """Single letters like A, B, x, y are strong_labels, not label_like.
    They're handled by Step 2, not Step 4. This test verifies that
    non-strong-label single-character text still works."""
    # These are strong_label — test at classifier level:
    fig = _fig()
    for text, bbox, expected in [
        ("x", (478, 269, 483, 285), True),   # on the axis
        ("y", (280, 71, 285, 87), True),     # axis label above fig
    ]:
        tb = TextBlock(page_number=12, bbox=bbox, text=text)
        assert DiagramAssembler._is_diagram_label(tb, fig) == expected, f"{repr(text)}"


def test_bare_minus_not_label_like():
    """A lone minus sign has no alphanumeric — should not be label_like."""
    assert not DiagramAssembler._is_label_like("–")


def test_measurement_still_label_like():
    assert DiagramAssembler._is_label_like("6 cm")
    assert DiagramAssembler._is_label_like("90°")


def test_strong_label_unaffected():
    """Strong labels still pass through Step 2 regardless."""
    fig = _fig()
    tb = TextBlock(page_number=12, bbox=(280, 71, 285, 87), text="y")
    assert DiagramAssembler._is_diagram_label(tb, fig)


def test_diag_0004_crop_no_question_text():
    """The crop should NOT include question text below the fig."""
    fig = _fig()
    blocks = [
        TextBlock(page_number=12, bbox=(274, 433, 286, 445), text="–6"),
        TextBlock(page_number=12, bbox=(43, 463, 268, 495), text="Triangle A is translated by the vector"),
        TextBlock(page_number=12, bbox=(269, 464, 274, 478), text="\x1b"),
        TextBlock(page_number=12, bbox=(269, 471, 373, 498), text="\x1a\x19  to give triangle B."),
    ]
    for tb in blocks:
        result = DiagramAssembler._is_diagram_label(tb, fig)
        if tb.text == "\x1b":
            assert not result, f"|{repr(tb.text)}| must NOT be included"
        elif "Triangle" in tb.text:
            assert not result, f"sentence must not be included"


def test_all_legitimate_d4_labels_included():
    """All real diagram labels from diag_0004 must still be included."""
    fig = _fig()
    labels = [
        ("y", (280, 71, 285, 87)),
        ("6", (280, 94, 286, 106)),
        ("5", (280, 122, 286, 134)),
        ("4", (280, 150, 286, 162)),
        ("3", (280, 178, 286, 190)),
        ("A", (216, 192, 225, 208)),
        ("2", (280, 206, 286, 218)),
        ("1", (280, 235, 286, 247)),
        ("x", (478, 269, 483, 285)),
        ("123456O", (278, 270, 462, 286)),
        ("–5–6–4–3–2–1", (114, 274, 267, 286)),
        ("–1", (274, 292, 286, 304)),
        ("–2", (274, 320, 286, 332)),
        ("–3", (274, 348, 286, 360)),
        ("–4", (274, 376, 286, 388)),
        ("–5", (274, 405, 286, 417)),
        ("–6", (274, 433, 286, 445)),
    ]
    for text, bbox in labels:
        tb = TextBlock(page_number=12, bbox=bbox, text=text)
        assert DiagramAssembler._is_diagram_label(tb, fig), f"|{repr(text)}| should be included"
