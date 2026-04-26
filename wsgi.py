"""
WSGI entrypoint para servidores como Gunicorn.
"""

from scriptorium.app import app

application = app
