import logging
from pathlib import Path
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates a human-readable extraction report."""

    def __init__(self, output_dir: Path = None):
        self.output_dir: Path = output_dir or config.REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        pdf_name: str,
        pages_processed: int,
        questions_found: int,
        diagrams_found: int,
        questions_with_diagrams: int,
        questions_without_diagrams: int,
        errors: list[str],
        warnings: list[str],
        filename: str = None,
        output_dir: Path = None,
        pdf_output_dir: Path = None,
    ) -> Path:
        if filename is None:
            filename = config.REPORT_FILENAME

        export_dir = output_dir or self.output_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        output_path = export_dir / filename
        report = self._build_report(
            pdf_name=pdf_name,
            pages_processed=pages_processed,
            questions_found=questions_found,
            diagrams_found=diagrams_found,
            questions_with_diagrams=questions_with_diagrams,
            questions_without_diagrams=questions_without_diagrams,
            errors=errors,
            warnings=warnings,
            pdf_output_dir=pdf_output_dir,
        )

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info("Report generated: %s", output_path)
        except Exception as e:
            logger.error("Failed to write report: %s", e)
            raise

        return output_path

    def _build_report(
        self,
        pdf_name: str,
        pages_processed: int,
        questions_found: int,
        diagrams_found: int,
        questions_with_diagrams: int,
        questions_without_diagrams: int,
        errors: list[str],
        warnings: list[str],
        pdf_output_dir: Path = None,
    ) -> str:
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("  BOOSTAI CONTENT PIPELINE - EXTRACTION REPORT")
        lines.append("=" * 60)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"  Generated: {now}")
        lines.append("")

        lines.append("-" * 60)
        lines.append("  PDF INFORMATION")
        lines.append("-" * 60)
        lines.append(f"  File:               {pdf_name}")
        lines.append(f"  Pages Processed:    {pages_processed}")
        lines.append("")

        lines.append("-" * 60)
        lines.append("  EXTRACTION SUMMARY")
        lines.append("-" * 60)
        lines.append(f"  Questions Found:    {questions_found}")
        lines.append(f"  Diagrams Found:     {diagrams_found}")
        lines.append(f"  Questions w/ Diags: {questions_with_diagrams}")
        lines.append(f"  Questions w/o Diags:{questions_without_diagrams}")
        lines.append("")

        coverage = 0.0
        if questions_found > 0:
            coverage = (questions_with_diagrams / questions_found) * 100
        lines.append(f"  Diagram Coverage:   {coverage:.1f}%")
        lines.append("")

        if errors:
            lines.append("-" * 60)
            lines.append("  ERRORS")
            lines.append("-" * 60)
            for err in errors:
                lines.append(f"  ! {err}")
            lines.append("")

        if warnings:
            lines.append("-" * 60)
            lines.append("  WARNINGS")
            lines.append("-" * 60)
            for warn in warnings:
                lines.append(f"  ? {warn}")
            lines.append("")

        lines.append("-" * 60)
        lines.append("  OUTPUT FILES")
        lines.append("-" * 60)
        if pdf_output_dir:
            lines.append(f"  Output Root: {pdf_output_dir}")
            lines.append(f"  Pages:       {pdf_output_dir / 'pages'}")
            lines.append(f"  Diagrams:    {pdf_output_dir / 'diagrams'}")
            lines.append(f"  Questions:   {pdf_output_dir / 'raw-json' / config.RAW_QUESTIONS_FILENAME}")
            lines.append(f"  Metadata:    {pdf_output_dir / 'metadata' / config.DIAGRAM_METADATA_FILENAME}")
            lines.append(f"  Report:      {pdf_output_dir / 'reports' / config.REPORT_FILENAME}")
        else:
            lines.append(f"  Pages:       {config.PAGES_DIR}")
            lines.append(f"  Diagrams:    {config.DIAGRAMS_DIR}")
            lines.append(f"  Questions:   {config.RAW_JSON_DIR / config.RAW_QUESTIONS_FILENAME}")
            lines.append(f"  Metadata:    {config.METADATA_DIR / config.DIAGRAM_METADATA_FILENAME}")
            lines.append(f"  Report:      {config.REPORTS_DIR / config.REPORT_FILENAME}")
        lines.append("")

        lines.append("=" * 60)
        lines.append("  END OF REPORT")
        lines.append("=" * 60)

        return "\n".join(lines)
