"""
models/review.py
Modelo de revisiones periodicas de ideas.
Arquitectura: Models.
"""

from __future__ import annotations

from datetime import datetime

from scriptorium.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    review_type = db.Column(db.String(40), nullable=False, default="weekly")
    notes = db.Column(db.Text, nullable=True)
    action_taken = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    idea = db.relationship("Idea", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review idea={self.idea_id} type={self.review_type}>"
