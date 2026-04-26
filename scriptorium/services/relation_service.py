"""
services/relation_service.py
Logica para crear y sugerir relaciones entre ideas.
Arquitectura: Services.
"""

from __future__ import annotations

from scriptorium.extensions import db
from scriptorium.models import Idea, Relation


class RelationService:
    """Crea relaciones manuales y sugiere relaciones automaticas."""

    def create_relation(
        self,
        source_idea_id: int,
        target_idea_id: int,
        relation_type: str = "complementa",
        strength: float = 0.5,
        reason: str = "",
        created_by: str = "user",
    ) -> Relation | None:
        if source_idea_id == target_idea_id:
            return None
        exists = Relation.query.filter_by(
            source_idea_id=source_idea_id,
            target_idea_id=target_idea_id,
            relation_type=relation_type,
        ).first()
        if exists:
            return exists
        relation = Relation(
            source_idea_id=source_idea_id,
            target_idea_id=target_idea_id,
            relation_type=relation_type,
            strength=max(0.0, min(1.0, strength)),
            reason=reason or "Relacion sugerida por coincidencias basicas",
            created_by=created_by,
        )
        db.session.add(relation)
        db.session.commit()
        return relation

    def suggest_relations_for_idea(self, idea: Idea, limit: int = 6) -> list[Relation]:
        suggestions: list[Relation] = []
        candidates = Idea.query.filter(Idea.id != idea.id, Idea.is_archived.is_(False)).all()
        for candidate in candidates:
            strength, reason = self._calculate_strength(idea, candidate)
            if strength < 0.35:
                continue
            relation_type = "desarrolla" if strength > 0.7 else "complementa"
            relation = self.create_relation(
                source_idea_id=idea.id,
                target_idea_id=candidate.id,
                relation_type=relation_type,
                strength=strength,
                reason=reason,
                created_by="system",
            )
            if relation:
                suggestions.append(relation)
            if len(suggestions) >= limit:
                break
        return suggestions

    def _calculate_strength(self, a: Idea, b: Idea) -> tuple[float, str]:
        score = 0.0
        reasons = []

        tags_a = {t.name.lower() for t in a.tags}
        tags_b = {t.name.lower() for t in b.tags}
        shared_tags = tags_a.intersection(tags_b)
        if shared_tags:
            score += min(0.5, 0.12 * len(shared_tags))
            reasons.append(f"Comparten etiquetas: {', '.join(sorted(shared_tags)[:4])}")

        if a.category_id and a.category_id == b.category_id:
            score += 0.2
            reasons.append("Comparten categoria")
        if a.project_id and a.project_id == b.project_id:
            score += 0.2
            reasons.append("Comparten proyecto")
        if a.scope_id and a.scope_id == b.scope_id:
            score += 0.15
            reasons.append("Comparten ambito")

        words_a = set((a.processed_text or a.original_text or "").lower().split())
        words_b = set((b.processed_text or b.original_text or "").lower().split())
        words_a = {w.strip(".,;:!?()[]{}") for w in words_a if len(w) > 4}
        words_b = {w.strip(".,;:!?()[]{}") for w in words_b if len(w) > 4}
        shared_words = words_a.intersection(words_b)
        if shared_words:
            score += min(0.25, 0.02 * len(shared_words))
            reasons.append("Coincidencia de conceptos en texto")

        return round(min(1.0, score), 2), "; ".join(reasons) or "Relacion textual simple"
