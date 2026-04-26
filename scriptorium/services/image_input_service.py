"""
services/image_input_service.py
Procesamiento de imagenes con OCR configurable.
Arquitectura: Services.
"""

from __future__ import annotations

from flask import current_app


class ImageInputService:
    """Extrae texto de imagenes cuando existe OCR disponible."""

    def download_telegram_image(self, file_path: str) -> str:
        return file_path

    def extract_text_from_image(self, image_path: str) -> tuple[str | None, str]:
        engine = current_app.config.get("OCR_ENGINE", "tesseract").lower()
        if engine != "tesseract":
            return None, "pendiente_ocr"
        try:
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore
        except Exception:
            return None, "pendiente_ocr"

        tesseract_cmd = current_app.config.get("TESSERACT_CMD")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        try:
            text = pytesseract.image_to_string(Image.open(image_path), lang="spa+eng")
        except Exception:
            return None, "error_ocr"
        clean = " ".join((text or "").split()).strip()
        return (clean if clean else None), "ocr_realizado"

    def process_image_input(self, image_path: str, caption: str | None = None) -> tuple[str | None, str]:
        ocr_text, status = self.extract_text_from_image(image_path)
        parts = [caption or "", ocr_text or ""]
        final_text = " ".join(p for p in parts if p).strip()
        if final_text:
            return final_text, status
        if status == "ocr_realizado":
            return None, "pendiente_ocr"
        return None, status
