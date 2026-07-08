#!/usr/bin/env python3
"""
BoostAI Content Pipeline
=======================
Processes PDF question banks into structured JSON, cropped diagrams,
and extraction reports.

Usage:
    python main.py

The pipeline automatically:
    1.  Scans input/pdfs/ for PDF files
    2.  Renders each page to high-resolution PNG
    3.  Extracts text via PyMuPDF (OCR fallback)
    4.  Detects questions using regex patterns
    5.  Extracts PDF-native drawing objects (lines, curves, rects)
    6.  Extracts embedded images from the PDF
    7.  Builds page layout with text blocks, drawings, and images
    8.  Maps question regions to page coordinates
    9.  Groups nearby drawings into diagram figures
    10. Associates diagrams with their parent questions
    11. Exports raw_questions.json with diagram_ids
    12. Exports diagram_metadata.json with structured metadata
    13. Generates extraction_report.txt
"""

import sys
import argparse
import json
import logging
from pathlib import Path

import fitz

import config
from src.renderer.pdf_renderer import PDFRenderer
from src.extractor.text_extractor import TextExtractor
from src.detector.question_detector import QuestionDetector
from src.pdf_objects.drawing_extractor import DrawingExtractor
from src.pdf_objects.image_extractor import ImageExtractor
from src.pdf_objects.layout_analyzer import LayoutAnalyzer
from src.pdf_objects.question_region_mapper import QuestionRegionMapper
from src.pdf_objects.diagram_assembler import DiagramAssembler
from src.exporter.json_exporter import JsonExporter
from src.exporter.metadata_exporter import MetadataExporter
from src.exporter.report_generator import ReportGenerator


def setup_logging() -> None:
    log_dir = config.LOGS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / config.LOG_FILENAME

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def find_pdfs() -> list[Path]:
    pdf_dir = config.PDF_DIR
    pdf_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"[!] No PDF files found in {pdf_dir}")
        print(f"    Place PDF files in: {pdf_dir}")
        sys.exit(0)

    return pdfs


def process_pdf(pdf_path: Path) -> dict:
    """Process a single PDF through the entire pipeline."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Processing: %s", pdf_path.name)
    logger.info("=" * 60)

    errors: list[str] = []
    warnings: list[str] = []

    # Create per-PDF output directories
    pdf_output_dir = config.get_per_pdf_output_dir(pdf_path)
    per_pdf = config.make_per_pdf_dirs(pdf_output_dir)
    logger.info("Output folder: %s", pdf_output_dir)

    renderer = PDFRenderer(output_dir=per_pdf["pages"])
    text_extractor = TextExtractor()
    question_detector = QuestionDetector()
    drawing_extractor = DrawingExtractor()
    image_extractor = ImageExtractor()
    layout_analyzer = LayoutAnalyzer()
    question_region_mapper = QuestionRegionMapper()
    diagram_assembler = DiagramAssembler(output_dir=per_pdf["diagrams"])
    json_exporter = JsonExporter(output_dir=per_pdf["raw_json"])
    metadata_exporter = MetadataExporter(output_dir=per_pdf["metadata"])
    report_generator = ReportGenerator(output_dir=per_pdf["reports"])

    # Step 1: Render pages
    logger.info("[1/11] Rendering PDF pages to PNG...")
    try:
        page_paths = renderer.render(pdf_path)
        pages_processed = len(page_paths)
    except Exception as e:
        logger.critical("Rendering failed: %s", e)
        errors.append(f"Rendering failed: {e}")
        return {"pdf_name": pdf_path.name, "pages_processed": 0, "questions_found": 0,
                "diagrams_found": 0, "questions_with_diagrams": 0,
                "questions_without_diagrams": 0, "errors": errors, "warnings": warnings,
                "output_dir": str(pdf_output_dir)}

    # Step 2: Extract text
    logger.info("[2/11] Extracting text from PDF...")
    try:
        pages_text = text_extractor.extract(pdf_path)
    except Exception as e:
        logger.critical("Text extraction failed: %s", e)
        errors.append(f"Text extraction failed: {e}")
        pages_text = {}

    # Step 3: Detect questions
    logger.info("[3/11] Detecting questions...")
    try:
        questions = question_detector.detect(pages_text)
        questions_found = len(questions)
    except Exception as e:
        logger.critical("Question detection failed: %s", e)
        errors.append(f"Question detection failed: {e}")
        questions = []
        questions_found = 0

    # Step 4: Open PDF for native extraction
    logger.info("[4/11] Opening PDF for native object extraction...")
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        logger.critical("Failed to open PDF: %s", e)
        errors.append(f"Failed to open PDF: {e}")
        doc = None

    diagrams_found = 0
    questions_with = 0
    questions_without = questions_found
    figures: list = []

    if doc is not None:
        try:
            # Step 5: Extract drawing objects
            logger.info("[5/11] Extracting PDF drawing objects...")
            page_drawings = drawing_extractor.extract_all(doc)

            # Step 6: Extract embedded images
            logger.info("[6/11] Extracting embedded images...")
            page_images = image_extractor.extract_all(doc)

            # Step 7: Build page layout (text blocks + drawings + images)
            logger.info("[7/11] Building page layout...")
            layouts = layout_analyzer.analyze(doc, page_drawings, page_images)

            # Step 8: Map question regions to page coordinates
            logger.info("[8/11] Mapping question regions...")
            question_regions = question_region_mapper.map_regions(
                doc, questions, layouts
            )

            # Step 9: Assemble diagrams and crop/save images
            logger.info("[9/11] Assembling diagram figures...")
            question_lookup = {q.number: q for q in questions}
            figures = diagram_assembler.assemble(
                page_drawings, page_images, layouts,
                question_regions, question_lookup,
            )
            diagrams_found = len(figures)

            if figures:
                logger.info("[9a/11] Cropping and saving diagram images...")
                diagram_assembler.save_diagram_images(
                    figures, pages_dir=per_pdf["pages"], layouts=layouts,
                )

            # Step 10: Update questions with diagram IDs
            for figure in figures:
                for q in questions:
                    if q.number == figure.question_number:
                        if figure.id not in q.diagram_ids:
                            q.diagram_ids.append(figure.id)
                        break

            questions_with = sum(1 for q in questions if q.diagram_ids)
            questions_without = questions_found - questions_with

        except Exception as e:
            logger.error("PDF object extraction failed: %s", e)
            errors.append(f"PDF object extraction failed: {e}")
        finally:
            doc.close()
    else:
        warnings.append("PDF object extraction skipped (doc is None)")

    # Step 10: Export questions JSON
    logger.info("[10/11] Exporting raw questions JSON...")
    try:
        json_exporter.export_questions(questions, output_dir=per_pdf["raw_json"])
    except Exception as e:
        logger.error("JSON export failed: %s", e)
        errors.append(f"JSON export failed: {e}")

    # Step 11: Export diagram metadata
    logger.info("[11/11] Exporting diagram metadata JSON...")
    try:
        metadata_exporter.export_diagram_figures(figures, output_dir=per_pdf["metadata"])
    except Exception as e:
        logger.error("Metadata export failed: %s", e)
        errors.append(f"Metadata export failed: {e}")

    # Step 12: Generate report
    logger.info("[12/12] Generating extraction report...")
    try:
        report_generator.generate(
            pdf_name=pdf_path.name,
            pages_processed=pages_processed,
            questions_found=questions_found,
            diagrams_found=diagrams_found,
            questions_with_diagrams=questions_with,
            questions_without_diagrams=questions_without,
            errors=errors,
            warnings=warnings,
            output_dir=per_pdf["reports"],
            pdf_output_dir=pdf_output_dir,
        )
    except Exception as e:
        logger.error("Report generation failed: %s", e)
        errors.append(f"Report generation failed: {e}")

    # Summary
    logger.info("Pipeline complete for %s", pdf_path.name)
    logger.info("  Pages: %d | Questions: %d | Diagrams: %d",
                pages_processed, questions_found, diagrams_found)

    return {
        "pdf_name": pdf_path.name,
        "pages_processed": pages_processed,
        "questions_found": questions_found,
        "diagrams_found": diagrams_found,
        "questions_with_diagrams": questions_with,
        "questions_without_diagrams": questions_without,
        "errors": errors,
        "warnings": warnings,
        "output_dir": str(pdf_output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="BoostAI Content Pipeline")
    parser.add_argument("--file", type=str, help="Process a single PDF file instead of scanning input/pdfs/")
    parser.add_argument("--json", action="store_true", help="Output results as JSON (for backend integration)")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    if args.file:
        pdf_path = Path(args.file)
        if not pdf_path.exists():
            print(json.dumps({"error": f"File not found: {pdf_path}"}))
            sys.exit(1)
        if pdf_path.suffix.lower() != ".pdf":
            print(json.dumps({"error": f"Not a PDF file: {pdf_path}"}))
            sys.exit(1)

        result = process_pdf(pdf_path)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "OK" if not result["errors"] else "ERRORS"
            print(f"  [{status}] {result['pdf_name']}: {result['pages_processed']}p / {result['questions_found']}q / {result['diagrams_found']}d")
        return

    print()
    print("  ============================================")
    print("    BOOSTAI CONTENT PIPELINE")
    print("    PDF Question Bank -> Structured Data")
    print("  ============================================")
    print()

    pdfs = find_pdfs()
    print(f"  Found {len(pdfs)} PDF file(s) to process")
    print()

    all_results: list[dict] = []
    for pdf_path in pdfs:
        result = process_pdf(pdf_path)
        all_results.append(result)

    # Final summary
    print()
    print("  ============================================")
    print("    PIPELINE COMPLETE")
    print("  ============================================")
    print()

    total_pages = sum(r["pages_processed"] for r in all_results)
    total_questions = sum(r["questions_found"] for r in all_results)
    total_diagrams = sum(r["diagrams_found"] for r in all_results)
    total_errors = sum(len(r["errors"]) for r in all_results)
    total_warnings = sum(len(r["warnings"]) for r in all_results)

    print(f"  PDFs Processed:       {len(all_results)}")
    print(f"  Total Pages:          {total_pages}")
    print(f"  Total Questions:      {total_questions}")
    print(f"  Total Diagrams:       {total_diagrams}")
    print(f"  Total Errors:         {total_errors}")
    print(f"  Total Warnings:       {total_warnings}")
    print()

    for r in all_results:
        status = "OK" if not r["errors"] else "ERRORS"
        print(f"  [{status}] {r['pdf_name']}: {r['pages_processed']}p / {r['questions_found']}q / {r['diagrams_found']}d")

    print()
    print(f"  Output directory: {config.OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
