"""
models/classification_log.py
Historial de clasificacion sugerida y final.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class ClassificationLog(db.Model):
    __tablename__ = "classification_logs"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    suggested_scope_id = db.Column(db.Integer, db.ForeignKey("scopes.id"), nullable=True)
    final_scope_id = db.Column(db.Integer, db.ForeignKey("scopes.id"), nullable=True)
    suggested_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    final_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    suggested_category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    final_category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    suggested_tags = db.Column(db.Text, nullable=True)
    final_tags = db.Column(db.Text, nullable=True)
    corrected_by_user = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    idea = db.relationship("Idea", back_populates="classification_logs")

    def __repr__(self) -> str:
        return f"<ClassificationLog idea={self.idea_id}>"
