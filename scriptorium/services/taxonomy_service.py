"""
services/taxonomy_service.py
Operaciones de taxonomia (alta, merge y utilidades).
Arquitectura: Services.
"""

from __future__ import annotations

from scriptorium.extensions import db
from scriptorium.models import Category, Tag


class TaxonomyService:
    """Gestion de entidades de taxonomia controladas por usuario."""

    def merge_tags(self, source_id: int, target_id: int) -> bool:
        source = Tag.query.get(source_id)
        target = Tag.query.get(target_id)
        if not source or not target or source.id == target.id:
            return False
        for idea in source.ideas:
            if target not in idea.tags:
                idea.tags.append(target)
        db.session.delete(source)
        db.session.commit()
        return True

    def merge_categories(self, source_id: int, target_id: int) -> bool:
        source = Category.query.get(source_id)
        target = Category.query.get(target_id)
        if not source or not target or source.id == target.id:
            return False
        for idea in source.ideas:
            idea.category_id = target.id
        source.is_active = False
        db.session.commit()
        return True
