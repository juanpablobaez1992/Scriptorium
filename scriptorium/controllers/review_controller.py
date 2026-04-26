"""
controllers/review_controller.py
Controlador de revision semanal y tareas.
Arquitectura: Controllers.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from scriptorium.extensions import db
from scriptorium.models import Idea, Review, Task
from scriptorium.services.suggestion_service import SuggestionService

review_bp = Blueprint("review", __name__)


@review_bp.get("/review/weekly")
def weekly_review():
    since = datetime.utcnow() - timedelta(days=7)
    new_ideas = Idea.query.filter(Idea.created_at >= since).order_by(Idea.created_at.desc()).all()
    unreviewed = Idea.query.filter(Idea.review_at.is_(None), Idea.is_archived.is_(False)).all()
    orphans = [
        idea
        for idea in Idea.query.filter(Idea.is_archived.is_(False)).all()
        if idea.project_id is None or idea.category_id is None or idea.relation_count() == 0
    ]
    core = [idea for idea in Idea.query.all() if idea.relation_count() >= 5]
    return render_template(
        "reviews/weekly.html",
        new_ideas=new_ideas,
        unreviewed=unreviewed,
        orphans=orphans,
        core_ideas=core,
        emerging=SuggestionService().emerging_projects(),
    )


@review_bp.post("/review/<int:idea_id>/action")
def review_action(idea_id: int):
    idea = Idea.query.get_or_404(idea_id)
    action = request.form.get("action", "").strip()
    notes = request.form.get("notes", "").strip()
    review = Review(
        idea_id=idea.id,
        review_type="weekly",
        notes=notes,
        action_taken=action,
    )
    idea.review_at = datetime.utcnow()
    db.session.add(review)
    db.session.commit()
    flash("Revision registrada.", "success")
    return redirect(url_for("review.weekly_review"))


@review_bp.get("/tasks")
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("tasks/list.html", tasks=tasks, ideas=Idea.query.order_by(Idea.created_at.desc()).all())


@review_bp.post("/tasks/create")
def create_task():
    task = Task(
        idea_id=int(request.form["idea_id"]) if request.form.get("idea_id") else None,
        title=request.form.get("title", "").strip(),
        description=request.form.get("description", "").strip(),
        status=request.form.get("status", "pendiente"),
        priority=int(request.form.get("priority", "3")),
    )
    if not task.title:
        flash("La tarea necesita titulo.", "warning")
        return redirect(url_for("review.list_tasks"))
    db.session.add(task)
    db.session.commit()
    flash("Tarea creada.", "success")
    return redirect(url_for("review.list_tasks"))


@review_bp.post("/tasks/<int:id>/update")
def update_task(id: int):
    task = Task.query.get_or_404(id)
    task.status = request.form.get("status", task.status)
    task.priority = int(request.form.get("priority", task.priority))
    task.title = request.form.get("title", task.title).strip()
    task.description = request.form.get("description", task.description or "").strip()
    db.session.commit()
    flash("Tarea actualizada.", "success")
    return redirect(url_for("review.list_tasks"))


@review_bp.get("/api/projects/emerging")
def api_emerging_projects():
    return jsonify(SuggestionService().emerging_projects())
