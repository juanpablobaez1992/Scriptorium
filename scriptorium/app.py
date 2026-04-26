"""
app.py
Entrypoint Flask y composicion de la aplicacion.
Arquitectura: bootstrap (MVC + Services).
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from scriptorium.config import Config
from scriptorium.controllers import register_blueprints
from scriptorium.extensions import db, migrate
from scriptorium.models import Category, Scope

DEFAULT_SCOPES = [
    "Educacion",
    "Filosofia",
    "Pastoral",
    "Tecnologia",
    "Empresa",
    "Editorial",
    "Audiovisual",
    "Vida personal",
    "Lecturas",
    "Comunicacion",
    "Productividad",
]

DEFAULT_CATEGORIES = [
    "Clase",
    "Reflexion filosofica",
    "Automatizacion",
    "Proyecto digital",
    "Articulo",
    "Campana",
    "Encuentro pastoral",
    "Guion",
    "Gestion institucional",
    "Lectura",
    "Idea personal",
]


def _ensure_storage_dirs(app: Flask) -> None:
    base = Path(app.config["STORAGE_PATH"])
    for section in ["audio", "images", "documents"]:
        for state in ["pending", "processed", "error"]:
            (base / section / state).mkdir(parents=True, exist_ok=True)


def _seed_initial_data() -> None:
    if Scope.query.count() == 0:
        for scope in DEFAULT_SCOPES:
            db.session.add(Scope(name=scope, description=f"Ambito {scope}"))
    if Category.query.count() == 0:
        for category in DEFAULT_CATEGORIES:
            db.session.add(Category(name=category, description=f"Categoria {category}"))
    db.session.commit()


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        instance_path=str(Path(__file__).resolve().parent / "instance"),
    )
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=app.config["PROXY_FIX_X_FOR"],
        x_proto=app.config["PROXY_FIX_X_PROTO"],
        x_host=app.config["PROXY_FIX_X_HOST"],
        x_port=app.config["PROXY_FIX_X_PORT"],
        x_prefix=app.config["PROXY_FIX_X_PREFIX"],
    )
    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)

    if app.config["ENV"] == "production" and app.config["SECRET_KEY"] == "change-this-secret-key":
        raise RuntimeError("SECRET_KEY must be set for production deployments.")

    @app.before_request
    def require_login():
        endpoint = request.endpoint or ""
        public_endpoints = set(app.config.get("PUBLIC_ENDPOINTS", set()))
        if not app.config.get("REQUIRE_AUTH", True):
            return None
        if endpoint in {"auth.login", "auth.logout"}:
            return None
        if endpoint.startswith("static") or endpoint in public_endpoints:
            return None
        if not session.get("authenticated"):
            next_url = request.full_path if request.query_string else request.path
            return redirect(url_for("auth.login", next=next_url))
        return None

    with app.app_context():
        _ensure_storage_dirs(app)
        if app.config.get("INIT_DB_ON_BOOT", True):
            db.create_all()
            _seed_initial_data()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"], debug=app.config["DEBUG"])
