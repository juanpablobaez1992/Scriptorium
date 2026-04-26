"""
models/taxonomy_suggestion.py
Modelo de sugerencias de taxonomia.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class TaxonomySuggestion(db.Model):
    __tablename__ = "taxonomy_suggestions"

    id = db.Column(db.Integer, primary_key=True)
    suggestion_type = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, default=0.5, nullable=False)
    status = db.Column(db.String(20), default="pendiente", nullable=False)
    related_idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=True)
    target_existing_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    related_idea = db.relationship("Idea", lazy=True)

    def __repr__(self) -> str:
        return f"<TaxonomySuggestion {self.suggestion_type}:{self.name}>"
