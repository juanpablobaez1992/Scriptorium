"""
services/transcription_service.py
Transcripcion configurable de audios.
Arquitectura: Services.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from flask import current_app


class TranscriptionService:
    """Interfaz base para motores de transcripcion."""

    def transcribe(self, file_path: str) -> str | None:
        raise NotImplementedError


class NoopTranscriptionService(TranscriptionService):
    """Motor por defecto: no transcribe, deja pendiente."""

    def transcribe(self, file_path: str) -> str | None:  # noqa: ARG002
        return None


class OpenAIWhisperTranscriptionService(TranscriptionService):
    """Motor opcional con OpenAI Whisper API."""

    def transcribe(self, file_path: str) -> str | None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception:
            return None

        api_key = current_app.config.get("OPENAI_API_KEY")
        if not api_key:
            return None
        client = OpenAI(api_key=api_key)
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return getattr(transcript, "text", None)


class TranscriptionFacade:
    """Façade de alto nivel para procesar audio dentro de la app."""

    def __init__(self) -> None:
        engine = current_app.config.get("TRANSCRIPTION_ENGINE", "none").lower()
        if engine == "openai":
            self.engine: TranscriptionService = OpenAIWhisperTranscriptionService()
        else:
            self.engine = NoopTranscriptionService()

    def download_telegram_audio(self, file_path: str) -> str:
        """El bot descarga el archivo; este metodo conserva la API de servicio."""
        return file_path

    def convert_audio_if_needed(self, file_path: str) -> str:
        """Lugar para conversiones futuras (ffmpeg)."""
        return file_path

    def clean_transcription(self, text: str) -> str:
        return " ".join((text or "").split()).strip()

    def transcribe_audio(self, file_path: str) -> str | None:
        return self.engine.transcribe(file_path)

    def process_audio_input(self, file_path: str) -> tuple[str | None, str]:
        path = self.convert_audio_if_needed(file_path)
        text = self.transcribe_audio(path)
        if not text:
            return None, "pendiente_transcripcion"
        return self.clean_transcription(text), "transcripto"

    @staticmethod
    def move_file(source: str, target: str) -> str:
        target_path = Path(target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source, target)
        return str(target_path)
