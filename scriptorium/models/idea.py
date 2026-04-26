"""
models/idea.py
Modelo principal del sistema: Idea.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db
from scriptorium.models.tag import idea_tags

IDEA_STATUSES = [
    "semilla",
    "brote",
    "nodo",
    "proyecto",
    "tarea",
    "material",
    "archivada",
    "descartada",
]

MATURITY_LEVELS = [
    "cruda",
    "semilla",
    "brote",
    "conectada",
    "desarrollada",
    "accionable",
    "producida",
]

INPUT_TYPES = [
    "manual_text",
    "telegram_text",
    "telegram_audio",
    "telegram_voice",
    "telegram_image",
    "telegram_document",
    "imported_text",
    "pending_input",
]


class Idea(db.Model):
    __tablename__ = "ideas"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    processed_text = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)

    scope_id = db.Column(db.Integer, db.ForeignKey("scopes.id"), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    status = db.Column(db.String(30), default="semilla", nullable=False)
    maturity_level = db.Column(db.String(30), default="cruda", nullable=False)
    source = db.Column(db.String(60), default="web", nullable=False)
    source_detail = db.Column(db.String(255), nullable=True)
    input_type = db.Column(db.String(40), default="manual_text", nullable=False)
    priority = db.Column(db.Integer, default=3, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    review_at = db.Column(db.DateTime, nullable=True)

    scope = db.relationship("Scope", back_populates="ideas")
    project = db.relationship("Project", back_populates="ideas")
    category = db.relationship("Category", back_populates="ideas")
    tags = db.relationship("Tag", secondary=idea_tags, back_populates="ideas")

    input_files = db.relationship("InputFile", back_populates="idea", lazy=True)
    tasks = db.relationship("Task", back_populates="idea", lazy=True)
    reviews = db.relationship("Review", back_populates="idea", lazy=True)
    classification_logs = db.relationship("ClassificationLog", back_populates="idea", lazy=True)

    outgoing_relations = db.relationship(
        "Relation",
        foreign_keys="Relation.source_idea_id",
        back_populates="source_idea",
        lazy=True,
    )
    incoming_relations = db.relationship(
        "Relation",
        foreign_keys="Relation.target_idea_id",
        back_populates="target_idea",
        lazy=True,
    )

    def relation_count(self) -> int:
        return len(self.outgoing_relations) + len(self.incoming_relations)

    def __repr__(self) -> str:
        return f"<Idea {self.id}: {self.title[:40]}>"
