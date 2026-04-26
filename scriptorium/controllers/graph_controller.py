"""
controllers/graph_controller.py
Controlador de vista y API del grafo.
Arquitectura: Controllers.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from scriptorium.models import Category, Project, Scope
from scriptorium.services.graph_service import GraphService

graph_bp = Blueprint("graph", __name__)


@graph_bp.get("/graph")
def graph_page():
    return render_template(
        "graph/graph.html",
        scopes=Scope.query.filter_by(is_active=True).all(),
        projects=Project.query.all(),
        categories=Category.query.filter_by(is_active=True).all(),
    )


@graph_bp.get("/api/graph")
def api_graph():
    filters = {
        "scope_id": int(request.args["scope_id"]) if request.args.get("scope_id") else None,
        "project_id": int(request.args["project_id"]) if request.args.get("project_id") else None,
        "category_id": int(request.args["category_id"]) if request.args.get("category_id") else None,
        "status": request.args.get("status"),
        "min_strength": request.args.get("min_strength"),
        "orphan_only": request.args.get("orphan_only") == "1",
        "core_only": request.args.get("core_only") == "1",
    }
    data = GraphService().build_graph(filters=filters)
    return jsonify(data)
