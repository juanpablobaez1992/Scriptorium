"""
services/embedding_service.py
Stub de embeddings para futura busqueda semantica.
Arquitectura: Services.
"""

from __future__ import annotations


class EmbeddingService:
    """Interface preparada para integrar motores de embeddings."""

    def generate_embedding(self, text: str):  # noqa: ANN201
        return None

    def compare_embeddings(self, embedding_a, embedding_b) -> float:  # noqa: ANN001
        return 0.0

    def find_similar_ideas(self, text: str) -> list[dict]:
        return []

    def update_idea_embedding(self, idea_id: int) -> None:  # noqa: ARG002
        return None
