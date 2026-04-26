"""
models/task.py
Modelo de tareas creadas desde ideas.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="pendiente", nullable=False)
    priority = db.Column(db.Integer, default=3, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    idea = db.relationship("Idea", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task {self.title}>"
