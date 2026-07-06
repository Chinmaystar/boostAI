from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

logger = logging.getLogger(__name__)

# Minimum image dimension in pixels to be considered a diagram
MIN_IMAGE_DIMENSION_PX = 50


@dataclass
class ImageObject:
    page_number: int
    bbox: tuple[float, float, float, float]
    xref: int
    width: int
    height: int
    ext: str

    @property
    def is_side_strip(self) -> bool:
        page_w = 595.0
        strip_x_margin = 30
        page_center = page_w / 2
        img_center = (self.bbox[0] + self.bbox[2]) / 2
        return abs(img_center - page_center) > (page_w / 2 - strip_x_margin)

    @property
    def is_diagram_size(self) -> bool:
        return self.width >= MIN_IMAGE_DIMENSION_PX and self.height >= MIN_IMAGE_DIMENSION_PX


class ImageExtractor:
    def extract(self, page: fitz.Page) -> list[ImageObject]:
        page_num = page.number + 1
        image_info = page.get_images(full=True)
        result: list[ImageObject] = []

        if not image_info:
            logger.debug("Page %d: no embedded images", page_num)
            return result

        for img in image_info:
            xref = img[0]
            width = img[2]
            height = img[3]

            bbox = page.get_image_bbox(img)
            if bbox is None:
                continue

            obj = ImageObject(
                page_number=page_num,
                bbox=(bbox.x0, bbox.y0, bbox.x1, bbox.y1),
                xref=xref,
                width=width,
                height=height,
                ext=img[6] if len(img) > 6 else "unknown",
            )

            result.append(obj)

        logger.debug(
            "Page %d: %d embedded images found",
            page_num,
            len(result),
        )
        return result

    def extract_all(self, doc: fitz.Document) -> dict[int, list[ImageObject]]:
        result: dict[int, list[ImageObject]] = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            images = self.extract(page)
            if images:
                result[page_num + 1] = images
        return result

    def save_image(
        self, doc: fitz.Document, image_obj: ImageObject, output_dir: Path
    ) -> Path | None:
        if image_obj.is_side_strip:
            logger.debug(
                "Skipping side-strip image on page %d", image_obj.page_number
            )
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        pix = fitz.Pixmap(doc, image_obj.xref)
        filename = f"img_p{image_obj.page_number:03d}_{image_obj.xref}.png"
        output_path = output_dir / filename

        if pix.n > 4:
            pix = fitz.Pixmap(fitz.csRGB, pix)

        pix.save(str(output_path))
        logger.debug("Saved image: %s", output_path)
        return output_path
