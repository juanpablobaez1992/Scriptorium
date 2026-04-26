"""
controllers/input_controller.py
Controlador de entradas pendientes y reprocesamiento.
Arquitectura: Controllers.
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from scriptorium.extensions import db
from scriptorium.models import InputFile
from scriptorium.services.input_service import InputService

input_bp = Blueprint("inputs", __name__)


@input_bp.get("/inputs/pending")
def pending_inputs():
    items = InputFile.query.filter(InputFile.status.notin_(["procesado_como_idea"])).order_by(
        InputFile.created_at.desc()
    )
    return render_template("inputs/pending.html", inputs=items.all())


@input_bp.get("/inputs/<int:id>")
def input_detail(id: int):
    item = InputFile.query.get_or_404(id)
    return render_template("inputs/detail.html", input_item=item)


@input_bp.post("/inputs/<int:id>/describe")
def describe_input(id: int):
    item = InputFile.query.get_or_404(id)
    description = request.form.get("description", "").strip()
    if not description:
        flash("Debe ingresar descripcion.", "warning")
        return redirect(url_for("inputs.input_detail", id=id))
    idea = InputService().create_idea_from_processed_text(
        text=description,
        source=item.source,
        source_detail=f"manual_description_input_{id}",
        input_type="pending_input",
    )
    item.idea_id = idea.id
    item.status = "procesado_como_idea"
    item.processed_at = datetime.utcnow()
    db.session.commit()
    flash("Descripcion agregada y convertida en idea.", "success")
    return redirect(url_for("ideas.idea_detail", id=idea.id))


@input_bp.post("/inputs/<int:id>/reprocess")
def reprocess_input(id: int):
    item = InputFile.query.get_or_404(id)
    service = InputService()
    idea = None
    if item.file_type in ("audio", "voice"):
        idea, updated = service.process_audio_input(
            {
                "file_type": item.file_type,
                "local_path": item.local_path,
                "original_filename": item.original_filename or "audio",
                "mime_type": item.mime_type,
            },
            source=item.source,
            source_detail="manual_reprocess",
        )
        item.status = updated.status
    elif item.file_type in ("image", "document_image"):
        idea, updated = service.process_image_input(
            {
                "file_type": item.file_type,
                "local_path": item.local_path,
                "original_filename": item.original_filename or "image",
                "mime_type": item.mime_type,
            },
            caption=item.ocr_text,
            source=item.source,
            source_detail="manual_reprocess",
        )
        item.status = updated.status
    db.session.commit()
    if idea:
        flash("Entrada reprocesada y convertida en idea.", "success")
        return redirect(url_for("ideas.idea_detail", id=idea.id))
    flash("Entrada reprocesada pero sigue pendiente.", "info")
    return redirect(url_for("inputs.input_detail", id=id))
