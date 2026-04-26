"""
services/title_service.py
Generacion de titulos breves para ideas.
Arquitectura: Services.
"""

from __future__ import annotations

import re


class TitleService:
    """Servicio simple para crear titulos legibles."""

    def generate(self, text: str, fallback: str = "Idea sin titulo") -> str:
        if not text:
            return fallback
        cleaned = re.sub(r"\s+", " ", text).strip()
        cleaned = re.sub(r"^(eh+|mmm+|bueno|ok)\s+", "", cleaned, flags=re.IGNORECASE)
        first_sentence = re.split(r"[.!?\n]", cleaned)[0].strip()
        title = first_sentence[:80] if first_sentence else cleaned[:80]
        return title.capitalize() if title else fallback
