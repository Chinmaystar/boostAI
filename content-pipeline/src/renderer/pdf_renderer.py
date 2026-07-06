from pathlib import Path
import logging
import fitz
from PIL import Image
import io
import config

logger = logging.getLogger(__name__)


class PDFRenderer:
    """Renders every page of a PDF to high-resolution PNG images using PyMuPDF."""

    def __init__(self, dpi: int = None, output_dir: Path = None):
        self.dpi = dpi or config.RENDER_DPI
        self.output_dir: Path = output_dir or config.PAGES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render(self, pdf_path: Path, output_dir: Path = None) -> list[Path]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        render_dir = output_dir or self.output_dir
        render_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Rendering PDF: %s  (dpi=%d)", pdf_path.name, self.dpi)

        doc = fitz.open(str(pdf_path))
        rendered_paths: list[Path] = []

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=self.dpi)
                img_bytes = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_bytes))

                filename = config.PAGE_IMAGE_TEMPLATE % (page_num + 1)
                output_path = render_dir / filename
                pil_image.save(output_path, format="PNG")
                rendered_paths.append(output_path)
                logger.debug("Rendered page %d -> %s", page_num + 1, output_path)
        finally:
            doc.close()

        logger.info(
            "Rendered %d pages from %s", len(rendered_paths), pdf_path.name
        )
        return rendered_paths
