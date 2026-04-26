"""
controllers/suggestion_controller.py
Controlador para revisar sugerencias del sistema.
Arquitectura: Controllers.
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from scriptorium.extensions import db
from scriptorium.models import Category, Project, Scope, Tag, TaxonomySuggestion
from scriptorium.services.suggestion_service import SuggestionService

suggestion_bp = Blueprint("suggestions", __name__)


@suggestion_bp.get("/suggestions")
def list_suggestions():
    SuggestionService().generate_system_suggestions()
    suggestions = TaxonomySuggestion.query.order_by(TaxonomySuggestion.created_at.desc()).all()
    return render_template("suggestions/list.html", suggestions=suggestions)


@suggestion_bp.get("/suggestions/<int:id>")
def detail_suggestion(id: int):
    suggestion = TaxonomySuggestion.query.get_or_404(id)
    return render_template("suggestions/detail.html", suggestion=suggestion)


def _apply_suggestion(suggestion: TaxonomySuggestion) -> None:
    if suggestion.suggestion_type == "scope":
        db.session.add(Scope(name=suggestion.name, description=suggestion.description or ""))
    elif suggestion.suggestion_type == "project":
        db.session.add(Project(name=suggestion.name, description=suggestion.description or "", status="emergente"))
    elif suggestion.suggestion_type in ("category", "subcategory"):
        db.session.add(Category(name=suggestion.name, description=suggestion.description or ""))
    elif suggestion.suggestion_type == "tag":
        if not Tag.query.filter(Tag.name.ilike(suggestion.name)).first():
            db.session.add(Tag(name=suggestion.name.lower()))


@suggestion_bp.post("/suggestions/<int:id>/accept")
def accept_suggestion(id: int):
    suggestion = TaxonomySuggestion.query.get_or_404(id)
    _apply_suggestion(suggestion)
    suggestion.status = "aceptada"
    suggestion.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash("Sugerencia aceptada.", "success")
    return redirect(url_for("suggestions.list_suggestions"))


@suggestion_bp.post("/suggestions/<int:id>/reject")
def reject_suggestion(id: int):
    suggestion = TaxonomySuggestion.query.get_or_404(id)
    suggestion.status = "rechazada"
    suggestion.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash("Sugerencia rechazada.", "info")
    return redirect(url_for("suggestions.list_suggestions"))


@suggestion_bp.post("/suggestions/<int:id>/ignore")
def ignore_suggestion(id: int):
    suggestion = TaxonomySuggestion.query.get_or_404(id)
    suggestion.status = "ignorada"
    suggestion.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash("Sugerencia ignorada.", "info")
    return redirect(url_for("suggestions.list_suggestions"))


@suggestion_bp.post("/suggestions/<int:id>/merge")
def merge_suggestion(id: int):
    suggestion = TaxonomySuggestion.query.get_or_404(id)
    suggestion.status = "fusionada"
    suggestion.target_existing_id = int(request.form.get("target_id") or 0) or None
    suggestion.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash("Sugerencia fusionada con elemento existente.", "success")
    return redirect(url_for("suggestions.list_suggestions"))


@suggestion_bp.get("/api/suggestions")
def api_suggestions():
    suggestions = TaxonomySuggestion.query.filter_by(status="pendiente").all()
    return jsonify(
        [
            {
                "id": s.id,
                "type": s.suggestion_type,
                "name": s.name,
                "reason": s.reason,
                "confidence": s.confidence,
                "status": s.status,
                "related_idea_id": s.related_idea_id,
                "created_at": s.created_at.isoformat(),
            }
            for s in suggestions
        ]
    )
