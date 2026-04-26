"""
models/relation.py
Modelo de relaciones entre ideas.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db

RELATION_TYPES = [
    "desarrolla",
    "contradice",
    "complementa",
    "recuerda_a",
    "deriva_en",
    "pertenece_a",
    "aplica_a",
    "inspira",
    "depende_de",
    "es_ejemplo_de",
    "es_pregunta_de",
    "es_respuesta_a",
    "profundiza",
    "sintetiza",
    "tensiona",
    "ilumina",
    "transforma_en",
]


class Relation(db.Model):
    __tablename__ = "relations"

    id = db.Column(db.Integer, primary_key=True)
    source_idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    target_idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    relation_type = db.Column(db.String(50), nullable=False, default="complementa")
    strength = db.Column(db.Float, default=0.5, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(30), default="system", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    source_idea = db.relationship(
        "Idea",
        foreign_keys=[source_idea_id],
        back_populates="outgoing_relations",
    )
    target_idea = db.relationship(
        "Idea",
        foreign_keys=[target_idea_id],
        back_populates="incoming_relations",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "source_idea_id",
            "target_idea_id",
            "relation_type",
            name="uq_relation_unique_edge",
        ),
    )

    def __repr__(self) -> str:
        return f"<Relation {self.source_idea_id}->{self.target_idea_id} ({self.relation_type})>"
