"""
services/export_service.py
Exportacion de ideas a CSV y Markdown.
Arquitectura: Services.
"""

from __future__ import annotations

import csv
from io import StringIO

from scriptorium.models import Idea


class ExportService:
    """Version inicial para exportaciones locales."""

    def export_ideas_csv(self, ideas: list[Idea]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "title", "summary", "scope", "project", "category", "status", "created_at"])
        for idea in ideas:
            writer.writerow(
                [
                    idea.id,
                    idea.title,
                    idea.summary or "",
                    idea.scope.name if idea.scope else "",
                    idea.project.name if idea.project else "",
                    idea.category.name if idea.category else "",
                    idea.status,
                    idea.created_at.isoformat(),
                ]
            )
        return output.getvalue()

    def export_idea_markdown(self, idea: Idea) -> str:
        tags = ", ".join([t.name for t in idea.tags]) or "-"
        return (
            f"# {idea.title}\n\n"
            f"## Resumen\n{idea.summary or '-'}\n\n"
            f"## Texto\n{idea.original_text}\n\n"
            f"## Metadatos\n"
            f"- Ambito: {idea.scope.name if idea.scope else '-'}\n"
            f"- Proyecto: {idea.project.name if idea.project else '-'}\n"
            f"- Categoria: {idea.category.name if idea.category else '-'}\n"
            f"- Etiquetas: {tags}\n"
            f"- Estado: {idea.status}\n"
            f"- Madurez: {idea.maturity_level}\n"
        )

    def export_ideas_markdown(self, ideas: list[Idea]) -> str:
        return "\n\n---\n\n".join(self.export_idea_markdown(idea) for idea in ideas)
