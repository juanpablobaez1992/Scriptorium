"""
services/suggestion_service.py
Generacion y gestion de sugerencias de taxonomia.
Arquitectura: Services.
"""

from __future__ import annotations

from collections import Counter

from scriptorium.extensions import db
from scriptorium.models import Idea, Project, Tag, TaxonomySuggestion


class SuggestionService:
    """Propone elementos de taxonomia sin crear definitivos automaticamente."""

    def create_if_missing(
        self,
        suggestion_type: str,
        name: str,
        reason: str,
        confidence: float = 0.5,
        related_idea_id: int | None = None,
        description: str = "",
    ) -> TaxonomySuggestion:
        existing = TaxonomySuggestion.query.filter_by(
            suggestion_type=suggestion_type,
            name=name,
            status="pendiente",
        ).first()
        if existing:
            return existing
        suggestion = TaxonomySuggestion(
            suggestion_type=suggestion_type,
            name=name,
            reason=reason,
            confidence=confidence,
            related_idea_id=related_idea_id,
            description=description,
        )
        db.session.add(suggestion)
        db.session.commit()
        return suggestion

    def generate_system_suggestions(self) -> list[TaxonomySuggestion]:
        created: list[TaxonomySuggestion] = []
        # Regla 1/3: ideas sin proyecto con patrones repetidos
        no_project = Idea.query.filter(Idea.project_id.is_(None), Idea.is_archived.is_(False)).all()
        tokens = []
        for idea in no_project:
            text = (idea.summary or idea.title or "").lower().split()
            tokens.extend([t.strip(".,;:!?()") for t in text if len(t) > 5])
        common = Counter(tokens).most_common(5)
        if len(no_project) >= 3 and common:
            key = common[0][0].capitalize()
            created.append(
                self.create_if_missing(
                    "project",
                    f"Proyecto {key}",
                    "Hay 3 o mas ideas similares sin proyecto claro.",
                    confidence=0.62,
                )
            )

        # Regla 4: etiqueta repetida no oficializada
        tag_counts = Counter()
        for idea in Idea.query.all():
            for raw in (idea.summary or "").lower().split():
                token = raw.strip(".,;:!?()")
                if len(token) > 6:
                    tag_counts[token] += 1
        for token, count in tag_counts.most_common(8):
            if count < 5:
                continue
            exists_tag = Tag.query.filter(Tag.name.ilike(token)).first()
            if not exists_tag:
                created.append(
                    self.create_if_missing(
                        "tag",
                        token,
                        f'La palabra "{token}" aparece en {count} ideas.',
                        confidence=0.7,
                    )
                )
                break
        return created

    def emerging_projects(self) -> list[dict]:
        data = []
        no_project = Idea.query.filter(Idea.project_id.is_(None), Idea.is_archived.is_(False)).all()
        if len(no_project) < 3:
            return data
        groups = Counter()
        for idea in no_project:
            for word in (idea.summary or idea.title).lower().split():
                token = word.strip(".,;:!?()")
                if len(token) > 6:
                    groups[token] += 1
        for token, count in groups.most_common(5):
            if count >= 3:
                data.append(
                    {
                        "name": f"Proyecto {token.capitalize()}",
                        "scope": "Por definir",
                        "description": "Proyecto emergente detectado por recurrencia textual.",
                        "confidence": round(min(0.9, 0.4 + count * 0.08), 2),
                        "ideas_count": count,
                    }
                )
        return data

    def active_projects(self) -> list[Project]:
        return Project.query.filter(Project.status.in_(["activo", "emergente"])).all()
