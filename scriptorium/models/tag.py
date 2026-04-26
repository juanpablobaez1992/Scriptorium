"""
models/tag.py
Modelo de etiquetas y tabla many-to-many con ideas.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db

idea_tags = db.Table(
    "idea_tags",
    db.Column("idea_id", db.Integer, db.ForeignKey("ideas.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ideas = db.relationship("Idea", secondary=idea_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
