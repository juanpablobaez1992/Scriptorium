"""
controllers/telegram_controller.py
Controlador para utilidades de integracion Telegram en web.
Arquitectura: Controllers.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from scriptorium.models import InputFile

telegram_bp = Blueprint("telegram", __name__)


@telegram_bp.get("/telegram/status")
def telegram_status():
    pending = InputFile.query.filter(InputFile.source == "telegram", InputFile.status != "procesado_como_idea").count()
    return jsonify({"status": "ok", "pending_inputs": pending})
