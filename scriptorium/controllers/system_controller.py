"""
controllers/system_controller.py
Endpoints operativos para health checks y estado basico.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

system_bp = Blueprint("system", __name__)


@system_bp.get("/healthz")
def healthz():
    return jsonify(
        {
            "status": "ok",
            "app": "scriptorium",
            "auth_enabled": current_app.config.get("REQUIRE_AUTH", True),
        }
    )
