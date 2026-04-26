"""
services/learning_service.py
Registro de correcciones humanas para aprendizaje futuro.
Arquitectura: Services.
"""

from __future__ import annotations

from scriptorium.extensions import db
from scriptorium.models import ClassificationLog, Idea


class LearningService:
    """Guarda historial de ajustes hechos por usuario."""

    def register_correction(self, idea: Idea, suggested: dict, final: dict) -> ClassificationLog:
        log = ClassificationLog(
            idea_id=idea.id,
            suggested_scope_id=suggested.get("scope_id"),
            final_scope_id=final.get("scope_id"),
            suggested_project_id=suggested.get("project_id"),
            final_project_id=final.get("project_id"),
            suggested_category_id=suggested.get("category_id"),
            final_category_id=final.get("category_id"),
            suggested_tags=", ".join(suggested.get("tags", [])),
            final_tags=", ".join(final.get("tags", [])),
            corrected_by_user=True,
        )
        db.session.add(log)
        db.session.commit()
        return log
