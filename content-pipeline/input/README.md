# Client PDF Inputs

Place client PDF files inside `pdfs/` to process them through the pipeline.

## Usage

1. Copy your PDF question banks into `pdfs/`
2. From the project root (`content-pipeline/`), run:

       python main.py

3. Processed outputs appear under `output/`

## Notes

- The `pdfs/` directory and all its contents are intentionally ignored by Git.
- Supported format: `.pdf`
- Each PDF is processed independently; results are grouped by PDF filename under `output/`.
