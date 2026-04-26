"""
services/classifier_service.py
Clasificador inicial basado en reglas y palabras clave.
Arquitectura: Services.
"""

from __future__ import annotations

from collections import Counter

from scriptorium.models import Category, Project, Scope, Tag

CATEGORY_KEYWORDS = {
    "Educacion": ["clase", "alumnos", "actividad", "rubrica", "unidad", "escuela", "curso"],
    "Tecnologia": ["python", "telegram", "app", "dashboard", "bot", "api", "sqlite"],
    "Pastoral": ["oracion", "cristo", "dios", "adoracion", "jovenes", "evangelio", "misa"],
    "Empresa": ["cliente", "precio", "venta", "producto", "servicio", "negocio"],
    "Editorial": ["libro", "edicion", "editorial", "imprenta", "autor", "publicacion"],
    "Audiovisual": ["video", "reel", "camara", "drone", "guion", "filmacion"],
    "Filosofia": ["verdad", "libertad", "felicidad", "virtud", "sentido", "ser", "alma"],
    "Comunicacion": ["copy", "campana", "publicacion", "instagram", "facebook", "ads"],
    "Productividad": ["organizar", "tarea", "sistema", "automatizar", "flujo", "eficiencia"],
}


class ClassifierService:
    """Clasificador extensible preparado para evolucionar a IA."""

    def classify(self, text: str) -> dict:
        txt = (text or "").lower()
        found = []
        scores = Counter()
        for category, words in CATEGORY_KEYWORDS.items():
            for word in words:
                if word in txt:
                    scores[category] += 1
                    found.append(word)

        category_name = scores.most_common(1)[0][0] if scores else None
        confidence = min(0.95, 0.2 + (scores[category_name] * 0.15)) if category_name else 0.2
        priority = 4 if any(w in txt for w in ["urgente", "hoy", "importante"]) else 3
        status = "semilla" if len(txt) < 400 else "brote"

        probable_scope = self._find_scope(category_name)
        probable_category = self._find_category(category_name)
        probable_project = self._find_project(txt, probable_scope)
        tags = self._extract_tags(found, txt)

        return {
            "probable_scope": probable_scope,
            "probable_project": probable_project,
            "probable_category": probable_category,
            "suggested_tags": tags,
            "suggested_priority": priority,
            "suggested_status": status,
            "confidence": round(confidence, 2),
            "keywords": list(dict.fromkeys(found)),
        }

    def _find_scope(self, hint: str | None) -> Scope | None:
        if not hint:
            return None
        return Scope.query.filter(Scope.name.ilike(f"%{hint}%")).first()

    def _find_project(self, text: str, scope: Scope | None) -> Project | None:
        query = Project.query
        if scope:
            query = query.filter_by(scope_id=scope.id)
        for project in query.all():
            if project.name.lower() in text:
                return project
        return None

    def _find_category(self, hint: str | None) -> Category | None:
        if not hint:
            return None
        return Category.query.filter(Category.name.ilike(f"%{hint}%")).first()

    def _extract_tags(self, keywords: list[str], text: str) -> list[Tag]:
        matched_tags: list[Tag] = []
        seen = set()
        for tag in Tag.query.all():
            if tag.name.lower() in text and tag.name.lower() not in seen:
                matched_tags.append(tag)
                seen.add(tag.name.lower())

        for keyword in keywords[:6]:
            if keyword in seen:
                continue
            existing = Tag.query.filter(Tag.name.ilike(keyword)).first()
            if existing:
                matched_tags.append(existing)
                seen.add(keyword)
        return matched_tags
