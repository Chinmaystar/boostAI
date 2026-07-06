# Generated Pipeline Outputs

This directory contains **automatically generated artifacts** produced by the Content Pipeline.

## Structure

- `output/<pdf_name>/pages/`       — Rendered page images (PNG)
- `output/<pdf_name>/diagrams/`    — Cropped diagram images (PNG)
- `output/<pdf_name>/raw-json/`    — Structured question data (JSON)
- `output/<pdf_name>/metadata/`    — Diagram metadata (JSON)
- `output/<pdf_name>/reports/`     — Extraction reports (TXT)
- `output/<pdf_name>/logs/`        — Pipeline execution logs

## Important

- This entire directory is **recreated every pipeline run**.
- Timestamped subdirectories (e.g., `output/<pdf_name>_20260706_175818/`) are created when the output folder already exists, preserving prior runs.
- **Never commit** the contents of `output/`.
- The directory is intentionally ignored by Git.
