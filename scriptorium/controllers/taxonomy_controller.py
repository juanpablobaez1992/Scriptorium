"""
controllers/taxonomy_controller.py
Controlador de ambitos, proyectos, categorias y etiquetas.
Arquitectura: Controllers.
"""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from scriptorium.extensions import db
from scriptorium.models import Category, Project, Scope, Tag
from scriptorium.services.taxonomy_service import TaxonomyService

taxonomy_bp = Blueprint("taxonomy", __name__)


@taxonomy_bp.get("/taxonomy/scopes")
def list_scopes():
    return render_template("taxonomy/scopes.html", scopes=Scope.query.order_by(Scope.name.asc()).all())


@taxonomy_bp.post("/taxonomy/scopes/create")
def create_scope():
    scope = Scope(
        name=request.form.get("name", "").strip(),
        description=request.form.get("description", "").strip(),
        color=request.form.get("color") or "#4f46e5",
    )
    if not scope.name:
        flash("El ambito necesita nombre.", "warning")
        return redirect(url_for("taxonomy.list_scopes"))
    db.session.add(scope)
    db.session.commit()
    flash("Ambito creado.", "success")
    return redirect(url_for("taxonomy.list_scopes"))


@taxonomy_bp.get("/taxonomy/projects")
def list_projects():
    return render_template(
        "taxonomy/projects.html",
        projects=Project.query.order_by(Project.created_at.desc()).all(),
        scopes=Scope.query.filter_by(is_active=True).all(),
    )


@taxonomy_bp.post("/taxonomy/projects/create")
def create_project():
    project = Project(
        name=request.form.get("name", "").strip(),
        scope_id=int(request.form["scope_id"]) if request.form.get("scope_id") else None,
        description=request.form.get("description", "").strip(),
        status=request.form.get("status", "activo"),
        color=request.form.get("color") or "#0ea5e9",
    )
    if not project.name:
        flash("El proyecto necesita nombre.", "warning")
        return redirect(url_for("taxonomy.list_projects"))
    db.session.add(project)
    db.session.commit()
    flash("Proyecto guardado.", "success")
    return redirect(url_for("taxonomy.list_projects"))


@taxonomy_bp.get("/taxonomy/categories")
def list_categories():
    return render_template(
        "taxonomy/categories.html",
        categories=Category.query.order_by(Category.name.asc()).all(),
    )


@taxonomy_bp.post("/taxonomy/categories/create")
def create_category():
    category = Category(
        name=request.form.get("name", "").strip(),
        description=request.form.get("description", "").strip(),
        parent_id=int(request.form["parent_id"]) if request.form.get("parent_id") else None,
        color=request.form.get("color") or "#14b8a6",
    )
    if not category.name:
        flash("La categoria necesita nombre.", "warning")
        return redirect(url_for("taxonomy.list_categories"))
    db.session.add(category)
    db.session.commit()
    flash("Categoria creada.", "success")
    return redirect(url_for("taxonomy.list_categories"))


@taxonomy_bp.post("/taxonomy/categories/merge")
def merge_categories():
    ok = TaxonomyService().merge_categories(
        int(request.form.get("source_id", "0")),
        int(request.form.get("target_id", "0")),
    )
    flash("Categorias fusionadas." if ok else "No se pudo fusionar categorias.", "info")
    return redirect(url_for("taxonomy.list_categories"))


@taxonomy_bp.get("/taxonomy/tags")
def list_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template("taxonomy/tags.html", tags=tags)


@taxonomy_bp.post("/taxonomy/tags/create")
def create_tag():
    name = request.form.get("name", "").strip().lower()
    if not name:
        flash("La etiqueta necesita nombre.", "warning")
        return redirect(url_for("taxonomy.list_tags"))
    if Tag.query.filter(Tag.name.ilike(name)).first():
        flash("La etiqueta ya existe.", "warning")
        return redirect(url_for("taxonomy.list_tags"))
    db.session.add(Tag(name=name))
    db.session.commit()
    flash("Etiqueta creada.", "success")
    return redirect(url_for("taxonomy.list_tags"))


@taxonomy_bp.post("/taxonomy/tags/merge")
def merge_tags():
    ok = TaxonomyService().merge_tags(
        int(request.form.get("source_id", "0")),
        int(request.form.get("target_id", "0")),
    )
    flash("Etiquetas fusionadas." if ok else "No se pudo fusionar etiquetas.", "info")
    return redirect(url_for("taxonomy.list_tags"))
