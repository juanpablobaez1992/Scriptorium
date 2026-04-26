"""
models/project.py
Modelo de proyectos concretos.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True, nullable=False)
    scope_id = db.Column(db.Integer, db.ForeignKey("scopes.id"), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="activo", nullable=False)
    color = db.Column(db.String(20), default="#0ea5e9")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    scope = db.relationship("Scope", back_populates="projects")
    ideas = db.relationship("Idea", back_populates="project", lazy=True)

    def __repr__(self) -> str:
        return f"<Project {self.name}>"
