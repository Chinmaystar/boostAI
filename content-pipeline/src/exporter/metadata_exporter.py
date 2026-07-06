import json
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)


class MetadataExporter:
    """Exports diagram metadata to a structured JSON file."""

    def __init__(self, output_dir: Path = None):
        self.output_dir: Path = output_dir or config.METADATA_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_metadata(
        self,
        diagram_crops: list[dict],
        filename: str = None,
        output_dir: Path = None,
    ) -> Path:
        if filename is None:
            filename = config.DIAGRAM_METADATA_FILENAME

        export_dir = output_dir or self.output_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        output_path = export_dir / filename
        metadata = self._build_metadata(diagram_crops)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(
                "Exported metadata for %d diagrams to %s",
                len(metadata),
                output_path,
            )
        except Exception as e:
            logger.error("Failed to export diagram metadata: %s", e)
            raise

        return output_path

    def _build_metadata(self, diagram_crops: list[dict]) -> list[dict]:
        metadata_list: list[dict] = []
        for idx, crop in enumerate(diagram_crops, start=1):
            entry = {
                "id": f"diag{idx:03d}",
                "question": str(crop.get("question", "")),
                "type": crop.get("type", "diagram"),
                "page": crop.get("page", 0),
                "filename": crop.get("filename", ""),
                "width": crop.get("width", 0),
                "height": crop.get("height", 0),
            }
            metadata_list.append(entry)
        return metadata_list

    def export_diagram_figures(
        self,
        figures: list,
        filename: str = None,
        output_dir: Path = None,
    ) -> Path:
        if filename is None:
            filename = config.DIAGRAM_METADATA_FILENAME

        export_dir = output_dir or self.output_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        output_path = export_dir / filename
        metadata = [
            f.to_metadata() if hasattr(f, "to_metadata") else f
            for f in figures
        ]

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(
                "Exported metadata for %d diagram figures to %s",
                len(metadata),
                output_path,
            )
        except Exception as e:
            logger.error("Failed to export diagram metadata: %s", e)
            raise

        return output_path
