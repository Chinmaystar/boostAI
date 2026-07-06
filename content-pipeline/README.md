# BoostAI Content Pipeline

A production-grade Python pipeline that transforms PDF question banks into structured, machine-readable data. Built for the BoostAI EdTech platform's School Module.

## Folder Structure

```
content-pipeline/
├── main.py                     # Pipeline orchestrator
├── config.py                   # Central configuration
├── requirements.txt            # Python dependencies
├── .gitignore
├── README.md
├── input/
│   └── pdfs/                   # Place PDF files here
├── output/
│   ├── pages/                  # Rendered page PNGs (page_001.png, ...)
│   ├── diagrams/               # Cropped diagram PNGs (diagram_q3_1.png, ...)
│   ├── raw-json/               # raw_questions.json
│   ├── templates/              # (reserved for future use)
│   ├── metadata/               # diagram_metadata.json
│   ├── reports/                # extraction_report.txt
│   └── logs/                   # pipeline.log
└── src/
    ├── pdf_objects/
    │   ├── drawing_extractor.py     # PDF-native vector drawing extraction
    │   ├── image_extractor.py       # Embedded image extraction
    │   ├── layout_analyzer.py       # Page model with text, drawings, images
    │   ├── question_region_mapper.py # Question-to-page-coordinate mapping
    │   └── diagram_assembler.py     # Cluster drawings into diagram figures
    ├── renderer/
    │   └── pdf_renderer.py          # PDF -> high-res PNG pages
    ├── extractor/
    │   └── text_extractor.py        # PyMuPDF text extraction (OCR fallback)
    ├── detector/
    │   └── question_detector.py     # Question identification via regex
    └── exporter/
        ├── json_exporter.py         # Export raw_questions.json
        ├── metadata_exporter.py     # Export diagram_metadata.json
        └── report_generator.py      # Generate extraction report
```

## Dependencies

- **Python** >= 3.10
- **PyMuPDF** (fitz) — text extraction and vector drawing extraction
- **pdf2image** — PDF-to-PNG rendering
- **Pillow** — image loading and cropping
- **tqdm** — progress bars

Optional (for OCR fallback):

- **pytesseract** — Tesseract OCR engine wrapper
- **Tesseract** — installed system-level OCR engine

## Installation

```bash
# 1. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) For OCR fallback support
pip install pytesseract
# Also install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
```

## How to Add New PDFs

1. Place your PDF question bank file(s) into `input/pdfs/`
2. Each PDF should contain exam questions with numbered items and optional diagrams
3. Run the pipeline (below)
4. Find all outputs in the `output/` directory

## How to Execute

```bash
python main.py
```

The pipeline will automatically:
1. Scan `input/pdfs/` for all PDF files
2. Process each PDF through the full pipeline
3. Generate all output files
4. Print a summary to the console

## How Outputs Are Generated

### 1. Page Rendering (`output/pages/`)
Every page of the PDF is rendered at 300 DPI to a PNG file named `page_001.png`, `page_002.png`, etc.

### 2. Text Extraction
PyMuPDF extracts raw text from each page. If no text is found, the pipeline falls back to OCR via pytesseract (if installed).

### 3. Question Detection
Questions are identified using regex patterns (`^\d+.`, `^\d+)`, `Question \d+`). Each question's text is captured from its number to the next question number or end-of-page. Question types are classified by keyword analysis (computation, proof, construction, explanation, diagram, application).

### 4. PDF Drawing Object Extraction
Instead of rasterizing pages and running computer vision algorithms, the pipeline extracts **native PDF vector objects** directly from the PDF via PyMuPDF's `page.get_drawings()`:

- **Vector path extraction**: lines, curves, rectangles, and bezier curves are extracted with exact coordinates and dimensions
- **Page border filtering**: the outer page content rectangle is excluded from diagram consideration
- **Margin/size filtering**: tiny or marginal drawing artifacts are discarded

### 5. Embedded Image Extraction
Images embedded in the PDF (e.g., logos, diagrams stored as image streams) are extracted via `page.get_images()` and filtered for diagram-suitable size.

### 6. Question Region Mapping
Each detected question is mapped to its vertical coordinate region on the page using:
- **Text block position**: PyMuPDF's `page.get_text("dict")` provides exact Y-coordinates for each text block
- **Question number matching**: regex patterns locate question headers in the raw text stream
- **Boundary detection**: `"Total for Question"` and `"Turn over"` markers delimit question boundaries
- **Fallback segmentation**: even distribution when no markers are found

### 7. Diagram Assembly and Classification
Drawings within each question region are **clustered by spatial proximity** and assembled into diagram figures:
- **Spatial clustering**: nearby drawing objects (within 30pt) are grouped into a single figure
- **Figure classification**: each figure is classified by analyzing its component drawing types and nearby text keywords (venn, geometry, graph, histogram, coordinate_grid)
- **Question association**: each figure is linked to its parent question by region overlap
- **Quality filters**: minimum size/area thresholds eliminate false positives

### 7. JSON Export (`output/raw-json/raw_questions.json`)
A structured JSON array where each entry contains:
```json
{
  "id": "",
  "question_number": "3",
  "page_number": 1,
  "question_type": "computation",
  "question_text": "3. Solve for x: 2x + 5 = 13",
  "diagram_ids": ["diag_0001"]
}
```

### 8. Metadata Export (`output/metadata/diagram_metadata.json`)
A structured JSON array for each diagram:
```json
{
  "id": "diag_0001",
  "question_number": "3",
  "page": 4,
  "type": "graph",
  "bbox": {
    "x": 219.9,
    "y": 102.7,
    "width": 156.1,
    "height": 109.9
  },
  "drawing_count": 1,
  "text_labels": ["10 m", "6 m", "8 m", "5 m"],
  "image_count": 0
}
```

### 9. Extraction Report (`output/reports/extraction_report.txt`)
A human-readable summary showing PDF name, pages processed, questions found, diagrams found, coverage statistics, errors, and warnings.

## Limitations

- **Digitally-generated PDFs only**: This pipeline relies on `page.get_drawings()` which only returns vector objects for digitally-generated PDFs. Scanned/handwritten documents will yield no drawings, and all diagram detection will come from embedded images only.
- **Question detection**: Depends on consistent numbering in the source PDF. Non-standard formats may require custom regex patterns.
- **OCR**: Optical Character Recognition requires manual installation of both `pytesseract` (Python package) and `Tesseract` (system binary). OCR quality depends on the source PDF image quality.
- **Complex layouts**: Multi-column layouts or heavily formatted tables may confuse the text extraction and question segmentation.
- **Figure classification**: Type tagging (graph/geometry/venn/etc.) is heuristic based on drawing primitive counts and nearby text; may misclassify ambiguous figures.

## Future Improvements

- **Question template engine**: Replace raw JSON with a template system that can generate random question variants
- **LaTeX extraction**: Convert math expressions in detected text regions to LaTeX using vision models
- **Multi-board support**: Extend configuration for different academic board formats
- **Parallel processing**: Process multiple PDFs concurrently for batch operations
- **Cross-page diagram merging**: Detect when a single diagram spans multiple pages (e.g., a multi-part graph)
- **Enhanced classification**: Improve figure type detection using shape analysis on vector paths rather than heuristic rules

## Integration with Question Template Engine

The `raw_questions.json` output is designed as the data source for a future **Dynamic Question Template Engine**:

1. `question_type` informs which template to use (computation, proof, construction, etc.)
2. `question_text` provides the human-readable prompt
 3. `diagram_ids` reference the visual assets via diagram_metadata.json
4. The engine can generate random variants by parameterizing numeric values in the question text
5. AI step-by-step solutions can be generated from the structured question data

## License

Proprietary — BoostAI Platform
