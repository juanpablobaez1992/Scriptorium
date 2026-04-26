"""
models/scope.py
Modelo de ambitos de conocimiento/vida.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class Scope(db.Model):
    __tablename__ = "scopes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(20), default="#4f46e5")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    projects = db.relationship("Project", back_populates="scope", lazy=True)
    ideas = db.relationship("Idea", back_populates="scope", lazy=True)

    def __repr__(self) -> str:
        return f"<Scope {self.name}>"
