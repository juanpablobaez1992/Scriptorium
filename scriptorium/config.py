"""
config.py
Configuracion central de la aplicacion.
Arquitectura: capa de configuracion transversal.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(BASE_DIR / ".env")


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Configuracion base de Flask."""

    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = _env_flag("FLASK_DEBUG", False)
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'scriptorium.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    STORAGE_PATH = os.getenv("STORAGE_PATH", str(BASE_DIR / "storage"))
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("PORT", os.getenv("APP_PORT", "5000")))
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")
    REQUIRE_AUTH = _env_flag("REQUIRE_AUTH", True)
    INIT_DB_ON_BOOT = _env_flag("INIT_DB_ON_BOOT", True)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _env_flag("SESSION_COOKIE_SECURE", False)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "32")) * 1024 * 1024
    PROXY_FIX_X_FOR = int(os.getenv("PROXY_FIX_X_FOR", "1"))
    PROXY_FIX_X_PROTO = int(os.getenv("PROXY_FIX_X_PROTO", "1"))
    PROXY_FIX_X_HOST = int(os.getenv("PROXY_FIX_X_HOST", "1"))
    PROXY_FIX_X_PORT = int(os.getenv("PROXY_FIX_X_PORT", "1"))
    PROXY_FIX_X_PREFIX = int(os.getenv("PROXY_FIX_X_PREFIX", "1"))

    TRANSCRIPTION_ENGINE = os.getenv("TRANSCRIPTION_ENGINE", "none")
    OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract")
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    WHISPER_LOCAL_MODEL = os.getenv("WHISPER_LOCAL_MODEL", "")

    AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD_HASH = os.getenv(
        "AUTH_PASSWORD_HASH",
        "scrypt:32768:8:1$bxBJKMzGwFTD3Vz1$85066691b7e5063eccd9962cad72ee9cc4cf90adfc1c99f34af4e4d0da90065235a15d668539fa4aa704ae64c6ff8b0b76e1c806aa6406aaa2abe8cc6647592c",
    )
    PUBLIC_ENDPOINTS = {
        endpoint.strip()
        for endpoint in os.getenv("PUBLIC_ENDPOINTS", "telegram.telegram_status,system.healthz").split(",")
        if endpoint.strip()
    }
