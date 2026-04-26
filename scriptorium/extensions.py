"""
extensions.py
Inicializa extensiones compartidas.
Arquitectura: infraestructura (DB y migraciones).
"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
