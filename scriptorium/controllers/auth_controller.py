"""
controllers/auth_controller.py
Autenticacion local de usuario unico (session-based).
Arquitectura: Controllers.
"""

from __future__ import annotations

from hmac import compare_digest
from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)


def _is_safe_next_url(target: str) -> bool:
    parsed = urlparse(target)
    return not parsed.netloc and parsed.path.startswith("/")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        valid_user = compare_digest(username, current_app.config["AUTH_USERNAME"])
        password_hash = current_app.config.get("AUTH_PASSWORD_HASH", "")
        try:
            valid_pass = bool(password_hash) and check_password_hash(password_hash, password)
        except (ValueError, TypeError):
            valid_pass = False

        if valid_user and valid_pass:
            session["authenticated"] = True
            session["auth_user"] = username
            flash("Sesion iniciada.", "success")
            next_url = request.args.get("next", "")
            if next_url and _is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for("dashboard.dashboard"))

        flash("Credenciales invalidas.", "danger")

    return render_template("auth/login.html")


@auth_bp.get("/logout")
def logout():
    session.pop("authenticated", None)
    session.pop("auth_user", None)
    flash("Sesion cerrada.", "info")
    return redirect(url_for("auth.login"))
