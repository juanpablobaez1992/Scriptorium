"""
controllers/__init__.py
Registro de blueprints de la aplicacion.
Arquitectura: Controllers package.
"""

from scriptorium.controllers.dashboard_controller import dashboard_bp
from scriptorium.controllers.graph_controller import graph_bp
from scriptorium.controllers.idea_controller import idea_bp
from scriptorium.controllers.input_controller import input_bp
from scriptorium.controllers.auth_controller import auth_bp
from scriptorium.controllers.review_controller import review_bp
from scriptorium.controllers.suggestion_controller import suggestion_bp
from scriptorium.controllers.system_controller import system_bp
from scriptorium.controllers.taxonomy_controller import taxonomy_bp
from scriptorium.controllers.telegram_controller import telegram_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(idea_bp)
    app.register_blueprint(taxonomy_bp)
    app.register_blueprint(suggestion_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(input_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(telegram_bp)
