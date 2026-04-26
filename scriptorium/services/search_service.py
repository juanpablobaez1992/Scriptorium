"""
services/search_service.py
Busqueda textual y por filtros de ideas.
Arquitectura: Services.
"""

from __future__ import annotations

from sqlalchemy import or_

from scriptorium.models import Idea, Tag


class SearchService:
    """Encapsula consultas de ideas para panel y API."""

    def search_ideas(self, filters: dict) -> list[Idea]:
        query = Idea.query
        text = filters.get("q", "").strip()
        if text:
            pattern = f"%{text}%"
            query = query.filter(
                or_(Idea.title.ilike(pattern), Idea.summary.ilike(pattern), Idea.original_text.ilike(pattern))
            )
        for field in ["scope_id", "project_id", "category_id", "status", "maturity_level", "source"]:
            value = filters.get(field)
            if value:
                query = query.filter(getattr(Idea, field) == value)

        tag_id = filters.get("tag_id")
        if tag_id:
            tag = Tag.query.get(int(tag_id))
            if tag:
                query = query.filter(Idea.tags.contains(tag))

        order_by = filters.get("order_by", "created_at")
        if order_by == "priority":
            query = query.order_by(Idea.priority.desc(), Idea.created_at.desc())
        else:
            query = query.order_by(Idea.created_at.desc())
        return query.all()
