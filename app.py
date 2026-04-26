"""
app.py
Punto de entrada requerido para ejecutar Scriptorium con `python app.py`.
"""

from scriptorium.app import app

if __name__ == "__main__":
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"], debug=app.config["DEBUG"])
