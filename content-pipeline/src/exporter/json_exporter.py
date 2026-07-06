import json
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)


class JsonExporter:
    """Exports extracted questions to a structured JSON file."""

    def __init__(self, output_dir: Path = None):
        self.output_dir: Path = output_dir or config.RAW_JSON_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_questions(
        self,
        questions: list,
        filename: str = None,
        output_dir: Path = None,
    ) -> Path:
        if filename is None:
            filename = config.RAW_QUESTIONS_FILENAME

        export_dir = output_dir or self.output_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        output_path = export_dir / filename
        data = self._build_export_data(questions)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Exported %d questions to %s", len(data), output_path)
        except Exception as e:
            logger.error("Failed to export questions JSON: %s", e)
            raise

        return output_path

    def _build_export_data(self, questions: list) -> list[dict]:
        return [
            q.to_dict() if hasattr(q, "to_dict") else q for q in questions
        ]
