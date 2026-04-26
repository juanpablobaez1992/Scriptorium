"""
controllers/idea_controller.py
Controlador de ideas y API de ideas.
Arquitectura: Controllers.
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from scriptorium.extensions import db
from scriptorium.models import (
    IDEA_STATUSES,
    MATURITY_LEVELS,
    Category,
    Idea,
    InputFile,
    Project,
    RELATION_TYPES,
    Scope,
    Tag,
    Task,
)
from scriptorium.services.input_service import InputService
from scriptorium.services.relation_service import RelationService
from scriptorium.services.search_service import SearchService

idea_bp = Blueprint("ideas", __name__)


@idea_bp.get("/ideas")
def list_ideas():
    service = SearchService()
    ideas = service.search_ideas(request.args.to_dict())
    return render_template(
        "ideas/list.html",
        ideas=ideas,
        scopes=Scope.query.filter_by(is_active=True).all(),
        projects=Project.query.all(),
        categories=Category.query.filter_by(is_active=True).all(),
        tags=Tag.query.order_by(Tag.name.asc()).all(),
        statuses=IDEA_STATUSES,
        maturities=MATURITY_LEVELS,
    )


@idea_bp.get("/ideas/new")
def new_idea():
    return render_template(
        "ideas/new.html",
        scopes=Scope.query.filter_by(is_active=True).all(),
        projects=Project.query.all(),
        categories=Category.query.filter_by(is_active=True).all(),
        tags=Tag.query.order_by(Tag.name.asc()).all(),
        statuses=IDEA_STATUSES,
        maturities=MATURITY_LEVELS,
    )


@idea_bp.post("/ideas/create")
def create_idea():
    text = request.form.get("text", "").strip()
    if not text:
        flash("La idea necesita texto.", "warning")
        return redirect(url_for("ideas.new_idea"))

    input_service = InputService()
    title = request.form.get("title", "").strip() or None
    idea = input_service.create_idea_from_processed_text(
        text=text,
        source="web",
        source_detail="panel",
        input_type="manual_text",
        title=title,
    )
    self_scope = request.form.get("scope_id")
    self_project = request.form.get("project_id")
    self_category = request.form.get("category_id")
    if self_scope:
        idea.scope_id = int(self_scope)
    if self_project:
        idea.project_id = int(self_project)
    if self_category:
        idea.category_id = int(self_category)
    idea.status = request.form.get("status") or idea.status
    idea.maturity_level = request.form.get("maturity_level") or idea.maturity_level
    idea.priority = int(request.form.get("priority") or idea.priority)
    review_at = request.form.get("review_at")
    if review_at:
        idea.review_at = datetime.fromisoformat(review_at)

    selected_tag_ids = request.form.getlist("tags")
    for tag_id in selected_tag_ids:
        tag = Tag.query.get(int(tag_id))
        if tag and tag not in idea.tags:
            idea.tags.append(tag)
    db.session.commit()

    action = request.form.get("action")
    if action == "save_find_relations":
        RelationService().suggest_relations_for_idea(idea)
    elif action == "save_task":
        task = Task(
            idea_id=idea.id,
            title=idea.title,
            description=idea.summary or idea.original_text[:200],
            status="pendiente",
            priority=idea.priority,
        )
        db.session.add(task)
    elif action == "save_project":
        project = Project(
            name=f"Emergente: {idea.title[:80]}",
            scope_id=idea.scope_id,
            description=idea.summary,
            status="emergente",
        )
        db.session.add(project)
    db.session.commit()

    flash("Idea guardada correctamente.", "success")
    return redirect(url_for("ideas.idea_detail", id=idea.id))


@idea_bp.get("/ideas/<int:id>")
def idea_detail(id: int):
    idea = Idea.query.get_or_404(id)
    linked_inputs = InputFile.query.filter_by(idea_id=idea.id).all()
    return render_template(
        "ideas/detail.html",
        idea=idea,
        linked_inputs=linked_inputs,
        all_ideas=Idea.query.filter(Idea.id != idea.id).limit(120).all(),
        relation_types=RELATION_TYPES,
    )


@idea_bp.get("/ideas/<int:id>/edit")
def edit_idea(id: int):
    idea = Idea.query.get_or_404(id)
    return render_template(
        "ideas/edit.html",
        idea=idea,
        scopes=Scope.query.filter_by(is_active=True).all(),
        projects=Project.query.all(),
        categories=Category.query.filter_by(is_active=True).all(),
        tags=Tag.query.order_by(Tag.name.asc()).all(),
        statuses=IDEA_STATUSES,
        maturities=MATURITY_LEVELS,
    )


@idea_bp.post("/ideas/<int:id>/update")
def update_idea(id: int):
    idea = Idea.query.get_or_404(id)
    idea.title = request.form.get("title", idea.title).strip()
    idea.original_text = request.form.get("text", idea.original_text).strip()
    idea.processed_text = request.form.get("processed_text", idea.processed_text or "")
    idea.summary = request.form.get("summary", idea.summary or "")
    idea.scope_id = int(request.form["scope_id"]) if request.form.get("scope_id") else None
    idea.project_id = int(request.form["project_id"]) if request.form.get("project_id") else None
    idea.category_id = int(request.form["category_id"]) if request.form.get("category_id") else None
    idea.status = request.form.get("status", idea.status)
    idea.maturity_level = request.form.get("maturity_level", idea.maturity_level)
    idea.priority = int(request.form.get("priority", idea.priority))
    selected_tag_ids = {int(tag_id) for tag_id in request.form.getlist("tags")}
    idea.tags = [tag for tag in Tag.query.all() if tag.id in selected_tag_ids]
    db.session.commit()
    flash("Idea actualizada.", "success")
    return redirect(url_for("ideas.idea_detail", id=id))


@idea_bp.post("/ideas/<int:id>/archive")
def archive_idea(id: int):
    idea = Idea.query.get_or_404(id)
    idea.is_archived = True
    idea.status = "archivada"
    db.session.commit()
    flash("Idea archivada.", "info")
    return redirect(url_for("ideas.list_ideas"))


@idea_bp.post("/ideas/<int:id>/delete")
def delete_idea(id: int):
    idea = Idea.query.get_or_404(id)
    idea.status = "descartada"
    idea.is_archived = True
    db.session.commit()
    flash("Idea descartada.", "warning")
    return redirect(url_for("ideas.list_ideas"))


@idea_bp.post("/ideas/<int:id>/reprocess")
def reprocess_idea(id: int):
    idea = Idea.query.get_or_404(id)
    input_service = InputService()
    classifier = input_service.classifier.classify(idea.processed_text or idea.original_text)
    idea.scope_id = classifier["probable_scope"].id if classifier["probable_scope"] else idea.scope_id
    idea.project_id = classifier["probable_project"].id if classifier["probable_project"] else idea.project_id
    idea.category_id = classifier["probable_category"].id if classifier["probable_category"] else idea.category_id
    idea.priority = classifier["suggested_priority"]
    db.session.commit()
    flash("Idea reprocesada.", "success")
    return redirect(url_for("ideas.idea_detail", id=id))


@idea_bp.post("/ideas/<int:id>/find-relations")
def find_relations(id: int):
    idea = Idea.query.get_or_404(id)
    created = RelationService().suggest_relations_for_idea(idea)
    flash(f"Relaciones detectadas: {len(created)}", "info")
    return redirect(url_for("ideas.idea_detail", id=id))


@idea_bp.post("/ideas/<int:id>/relate")
def relate_idea(id: int):
    idea = Idea.query.get_or_404(id)
    target_id = int(request.form.get("target_idea_id", "0"))
    relation_type = request.form.get("relation_type", "complementa")
    strength = float(request.form.get("strength", "0.5"))
    reason = request.form.get("reason", "").strip()
    if target_id <= 0:
        flash("Selecciona una idea destino.", "warning")
        return redirect(url_for("ideas.idea_detail", id=id))
    relation = RelationService().create_relation(
        source_idea_id=idea.id,
        target_idea_id=target_id,
        relation_type=relation_type,
        strength=strength,
        reason=reason,
        created_by="user",
    )
    if relation:
        flash("Relación manual creada.", "success")
    else:
        flash("No se pudo crear la relación.", "warning")
    return redirect(url_for("ideas.idea_detail", id=id))


@idea_bp.post("/ideas/<int:id>/convert-task")
def convert_task(id: int):
    idea = Idea.query.get_or_404(id)
    task = Task(
        idea_id=idea.id,
        title=idea.title,
        description=idea.summary,
        status="pendiente",
        priority=idea.priority,
    )
    db.session.add(task)
    idea.status = "tarea"
    db.session.commit()
    flash("Idea convertida en tarea.", "success")
    return redirect(url_for("review.list_tasks"))


@idea_bp.post("/ideas/<int:id>/convert-project")
def convert_project(id: int):
    idea = Idea.query.get_or_404(id)
    project = Project(
        name=f"Proyecto: {idea.title[:100]}",
        scope_id=idea.scope_id,
        description=idea.summary,
        status="emergente",
    )
    db.session.add(project)
    idea.project = project
    idea.status = "proyecto"
    db.session.commit()
    flash("Idea convertida en proyecto emergente.", "success")
    return redirect(url_for("taxonomy.list_projects"))


@idea_bp.get("/ideas/orphan")
def orphan_ideas_view():
    ideas = Idea.query.filter(
        Idea.is_archived.is_(False),
        (Idea.project_id.is_(None) | Idea.category_id.is_(None)),
    ).all()
    return render_template("ideas/orphan.html", ideas=ideas)


@idea_bp.get("/api/ideas")
def api_ideas():
    ideas = Idea.query.order_by(Idea.created_at.desc()).limit(300).all()
    return jsonify(
        [
            {
                "id": idea.id,
                "title": idea.title,
                "summary": idea.summary,
                "scope": idea.scope.name if idea.scope else None,
                "project": idea.project.name if idea.project else None,
                "category": idea.category.name if idea.category else None,
                "status": idea.status,
                "maturity_level": idea.maturity_level,
                "priority": idea.priority,
                "relations": idea.relation_count(),
                "created_at": idea.created_at.isoformat(),
            }
            for idea in ideas
        ]
    )


@idea_bp.get("/api/orphan-ideas")
def api_orphan_ideas():
    ideas = Idea.query.filter(
        Idea.is_archived.is_(False),
        ((Idea.project_id.is_(None)) | (Idea.category_id.is_(None))),
    ).all()
    return jsonify(
        [
            {
                "id": idea.id,
                "title": idea.title,
                "missing_project": idea.project_id is None,
                "missing_category": idea.category_id is None,
                "missing_tags": len(idea.tags) == 0,
                "missing_relations": idea.relation_count() == 0,
            }
            for idea in ideas
        ]
    )


@idea_bp.get("/api/core-ideas")
def api_core_ideas():
    ideas = [i for i in Idea.query.filter(Idea.is_archived.is_(False)).all() if i.relation_count() >= 5]
    return jsonify(
        [{"id": idea.id, "title": idea.title, "relations": idea.relation_count()} for idea in ideas]
    )
