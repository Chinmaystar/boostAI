from pathlib import Path
import logging
import fitz
import config

logger = logging.getLogger(__name__)


class TextExtractionError(Exception):
    pass


class TextExtractor:
    """Extracts text from PDF pages using PyMuPDF, with OCR fallback."""

    def extract(self, pdf_path: Path) -> dict[int, str]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info("Extracting text from: %s", pdf_path.name)

        doc = fitz.open(str(pdf_path))
        pages_text: dict[int, str] = {}

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                if text and text.strip():
                    pages_text[page_num + 1] = text.strip()
                    logger.debug("Page %d: text extracted (%d chars)", page_num + 1, len(text))
                else:
                    logger.warning(
                        "Page %d: no text found via PyMuPDF, attempting OCR fallback",
                        page_num + 1,
                    )
                    ocr_text = self._ocr_fallback(page, page_num + 1)
                    pages_text[page_num + 1] = ocr_text

        except Exception as e:
            raise TextExtractionError(f"Failed to extract text from {pdf_path.name}: {e}") from e
        finally:
            doc.close()

        logger.info(
            "Extracted text from %d pages in %s", len(pages_text), pdf_path.name
        )
        return pages_text

    def _ocr_fallback(self, page, page_num: int) -> str:
        """Fallback OCR using pytesseract if available, otherwise raise."""
        try:
            import pytesseract
            from PIL import Image
            import io

            pix = page.get_pixmap(dpi=config.OCR_DPI)
            img_bytes = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(pil_image, lang=config.OCR_LANGUAGES)
            logger.info("OCR fallback succeeded for page %d", page_num)
            return text.strip()
        except ImportError:
            logger.error(
                "pytesseract not installed. Cannot OCR page %d. "
                "Install with: pip install pytesseract",
                page_num,
            )
            return ""
        except Exception as e:
            logger.error("OCR fallback failed for page %d: %s", page_num, e)
            return ""
