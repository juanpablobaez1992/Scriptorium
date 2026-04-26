"""
controllers/dashboard_controller.py
Controlador del dashboard principal y metricas.
Arquitectura: Controllers.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, render_template
from sqlalchemy import func

from scriptorium.models import Idea, Project, TaxonomySuggestion

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def dashboard():
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=7)

    total_ideas = Idea.query.count()
    ideas_today = Idea.query.filter(Idea.created_at >= today_start).count()
    ideas_week = Idea.query.filter(Idea.created_at >= week_start).count()
    suggestions_pending = TaxonomySuggestion.query.filter_by(status="pendiente").count()
    orphan_ideas = Idea.query.filter(
        Idea.project_id.is_(None),
        Idea.category_id.is_(None),
        Idea.is_archived.is_(False),
    ).count()
    active_projects = Project.query.filter(Project.status.in_(["activo", "emergente"])).count()
    latest_ideas = Idea.query.order_by(Idea.created_at.desc()).limit(8).all()

    by_scope = (
        Idea.query.with_entities(Idea.scope_id, func.count(Idea.id))
        .group_by(Idea.scope_id)
        .all()
    )
    by_status = (
        Idea.query.with_entities(Idea.status, func.count(Idea.id))
        .group_by(Idea.status)
        .all()
    )
    by_maturity = (
        Idea.query.with_entities(Idea.maturity_level, func.count(Idea.id))
        .group_by(Idea.maturity_level)
        .all()
    )

    core_ideas = [
        idea for idea in Idea.query.filter(Idea.is_archived.is_(False)).all() if idea.relation_count() >= 5
    ][:8]

    return render_template(
        "dashboard.html",
        total_ideas=total_ideas,
        ideas_today=ideas_today,
        ideas_week=ideas_week,
        suggestions_pending=suggestions_pending,
        orphan_ideas=orphan_ideas,
        active_projects=active_projects,
        latest_ideas=latest_ideas,
        by_scope=by_scope,
        by_status=by_status,
        by_maturity=by_maturity,
        core_ideas=core_ideas,
    )
