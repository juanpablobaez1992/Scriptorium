"""
services/summary_service.py
Generacion de resumen simple para ideas.
Arquitectura: Services.
"""

from __future__ import annotations

import re


class SummaryService:
    """Resume texto con reglas basicas."""

    def summarize(self, text: str, max_len: int = 220) -> str:
        if not text:
            return ""
        cleaned = re.sub(r"\s+", " ", text).strip()
        cleaned = re.sub(r"\b(eh+|mmm+)\b", "", cleaned, flags=re.IGNORECASE)
        sentence = re.split(r"(?<=[.!?])\s+", cleaned)[0]
        if len(sentence) > max_len:
            return sentence[: max_len - 3].strip() + "..."
        return sentence
