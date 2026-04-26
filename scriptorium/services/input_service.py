"""
services/input_service.py
Orquesta entradas de texto/audio/imagen y garantiza persistencia.
Arquitectura: Services.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

from scriptorium.extensions import db
from scriptorium.models import ClassificationLog, Idea, InputFile
from scriptorium.services.classifier_service import ClassifierService
from scriptorium.services.relation_service import RelationService
from scriptorium.services.summary_service import SummaryService
from scriptorium.services.suggestion_service import SuggestionService
from scriptorium.services.title_service import TitleService
from scriptorium.services.transcription_service import TranscriptionFacade
from scriptorium.services.image_input_service import ImageInputService


class InputService:
    """Servicio principal de captura: nada se pierde, todo se registra."""

    def __init__(self) -> None:
        self.classifier = ClassifierService()
        self.title_service = TitleService()
        self.summary_service = SummaryService()
        self.relation_service = RelationService()
        self.suggestion_service = SuggestionService()

    def process_text_input(self, text: str, source: str, source_detail: str = "") -> Idea:
        return self.create_idea_from_processed_text(
            text=text,
            source=source,
            source_detail=source_detail,
            input_type=f"{source}_text" if source == "telegram" else "manual_text",
        )

    def process_audio_input(self, file_data: dict, source: str, source_detail: str = "") -> tuple[Idea | None, InputFile]:
        input_file = self.create_pending_input(
            source=source,
            file_type=file_data.get("file_type", "audio"),
            original_filename=file_data.get("original_filename", "audio.ogg"),
            local_path=file_data["local_path"],
            telegram_file_id=file_data.get("telegram_file_id"),
            mime_type=file_data.get("mime_type"),
            status="descargado",
        )
        facade = TranscriptionFacade()
        transcript, status = facade.process_audio_input(input_file.local_path)
        input_file.status = status
        input_file.transcription_text = transcript
        input_file.processed_at = datetime.utcnow() if transcript else None
        if not transcript:
            db.session.commit()
            return None, input_file

        idea = self.create_idea_from_processed_text(
            text=transcript,
            source=source,
            source_detail=source_detail,
            input_type="telegram_voice" if file_data.get("file_type") == "voice" else "telegram_audio",
        )
        input_file.idea_id = idea.id
        input_file.status = "procesado_como_idea"
        db.session.commit()
        return idea, input_file

    def process_image_input(
        self,
        file_data: dict,
        caption: str | None,
        source: str,
        source_detail: str = "",
    ) -> tuple[Idea | None, InputFile]:
        input_file = self.create_pending_input(
            source=source,
            file_type=file_data.get("file_type", "image"),
            original_filename=file_data.get("original_filename", "image.jpg"),
            local_path=file_data["local_path"],
            telegram_file_id=file_data.get("telegram_file_id"),
            mime_type=file_data.get("mime_type"),
            status="descargado",
        )
        image_service = ImageInputService()
        text, status = image_service.process_image_input(input_file.local_path, caption)
        input_file.ocr_text = text
        input_file.status = status
        if not text:
            db.session.commit()
            return None, input_file

        idea = self.create_idea_from_processed_text(
            text=text,
            source=source,
            source_detail=source_detail,
            input_type="telegram_image" if file_data.get("file_type") == "image" else "telegram_document",
        )
        input_file.idea_id = idea.id
        input_file.status = "procesado_como_idea"
        input_file.processed_at = datetime.utcnow()
        db.session.commit()
        return idea, input_file

    def create_pending_input(
        self,
        source: str,
        file_type: str,
        original_filename: str,
        local_path: str,
        telegram_file_id: str | None = None,
        mime_type: str | None = None,
        status: str = "recibido",
    ) -> InputFile:
        input_file = InputFile(
            source=source,
            file_type=file_type,
            telegram_file_id=telegram_file_id,
            original_filename=original_filename,
            local_path=local_path,
            mime_type=mime_type,
            status=status,
        )
        db.session.add(input_file)
        db.session.commit()
        return input_file

    def create_idea_from_processed_text(
        self,
        text: str,
        source: str,
        source_detail: str = "",
        input_type: str = "manual_text",
        title: str | None = None,
    ) -> Idea:
        classification = self.classifier.classify(text)
        idea = Idea(
            title=title or self.title_service.generate(text),
            original_text=text,
            raw_text=text,
            processed_text=text,
            summary=self.summary_service.summarize(text),
            scope_id=classification["probable_scope"].id if classification["probable_scope"] else None,
            project_id=classification["probable_project"].id if classification["probable_project"] else None,
            category_id=classification["probable_category"].id if classification["probable_category"] else None,
            status=classification["suggested_status"],
            maturity_level="semilla" if len(text) < 500 else "brote",
            source=source,
            source_detail=source_detail,
            input_type=input_type,
            priority=classification["suggested_priority"],
        )
        db.session.add(idea)
        db.session.flush()
        for tag in classification["suggested_tags"]:
            if tag not in idea.tags:
                idea.tags.append(tag)

        log = ClassificationLog(
            idea_id=idea.id,
            suggested_scope_id=idea.scope_id,
            final_scope_id=idea.scope_id,
            suggested_project_id=idea.project_id,
            final_project_id=idea.project_id,
            suggested_category_id=idea.category_id,
            final_category_id=idea.category_id,
            suggested_tags=", ".join([t.name for t in idea.tags]),
            final_tags=", ".join([t.name for t in idea.tags]),
            corrected_by_user=False,
        )
        db.session.add(log)
        db.session.commit()

        self.relation_service.suggest_relations_for_idea(idea)
        self.suggestion_service.generate_system_suggestions()
        return idea

    @staticmethod
    def save_uploaded_file(file_storage, folder: str) -> str:
        storage_path = Path(current_app.config["STORAGE_PATH"]) / folder
        storage_path.mkdir(parents=True, exist_ok=True)
        safe_name = secure_filename(file_storage.filename or "input.bin")
        final_name = f"{uuid4().hex}_{safe_name}"
        final_path = storage_path / final_name
        file_storage.save(final_path)
        return str(final_path)
