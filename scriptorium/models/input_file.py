"""
models/input_file.py
Modelo de archivos recibidos desde entradas externas.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class InputFile(db.Model):
    __tablename__ = "input_files"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=True)
    source = db.Column(db.String(40), nullable=False, default="telegram")
    file_type = db.Column(db.String(30), nullable=False)
    telegram_file_id = db.Column(db.String(255), nullable=True)
    original_filename = db.Column(db.String(255), nullable=True)
    local_path = db.Column(db.String(400), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    transcription_text = db.Column(db.Text, nullable=True)
    ocr_text = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="recibido")
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)

    idea = db.relationship("Idea", back_populates="input_files")

    def __repr__(self) -> str:
        return f"<InputFile {self.file_type} {self.status}>"
