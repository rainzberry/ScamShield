"""Application configuration. All secrets come from environment variables."""
from __future__ import annotations

import logging
import os
import secrets
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
load_dotenv(BASE_DIR / ".env")

log = logging.getLogger(__name__)


def _env(name: str, default=None):
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, default))
    except (TypeError, ValueError):
        return default


def _env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in str(_env(name, default)).split(",") if item.strip()]


class BaseConfig:
    APP_ENV = "development"
    DEBUG = False
    TESTING = False

    INSTANCE_DIR = INSTANCE_DIR
    SECRET_KEY = _env("SECRET_KEY")
    JWT_SECRET_KEY = _env("JWT_SECRET_KEY")

    # Database
    SQLALCHEMY_DATABASE_URI = _env(
        "DATABASE_URL", "sqlite:///" + (INSTANCE_DIR / "scamshield.db").as_posix()
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    AUTO_CREATE_DB = True  # create tables on startup (dev convenience)

    # Auth
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=_env_int("JWT_ACCESS_TOKEN_MINUTES", 60))
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000"

    # Request / upload limits
    MAX_CONTENT_LENGTH = _env_int("MAX_CONTENT_LENGTH", 4 * 1024 * 1024)
    QR_MAX_UPLOAD_BYTES = _env_int("QR_MAX_UPLOAD_BYTES", 2 * 1024 * 1024)
    QR_MAX_PIXELS = 25_000_000
    QR_ALLOWED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
    QR_ALLOWED_MIME_TYPES = (
        "image/png", "image/jpeg", "image/webp", "image/bmp", "image/gif",
    )

    # CORS
    CORS_ORIGINS = _env_list("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

    # Rate limiting (Flask-Limiter reads the RATELIMIT_* keys directly)
    RATELIMIT_ENABLED = True
    RATELIMIT_HEADERS_ENABLED = True  # adds Retry-After / X-RateLimit-* headers
    RATELIMIT_STORAGE_URI = _env("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = _env("RATELIMIT_DEFAULT", "300 per minute")
    RATELIMIT_AUTH = _env("RATELIMIT_AUTH", "10 per minute")
    RATELIMIT_ANALYZE = _env("RATELIMIT_ANALYZE", "30 per minute")

    # ML engine (module:function specs; see README "ML integration")
    ML_PROJECT_PATH = _env("ML_PROJECT_PATH")
    ML_TEXT_ANALYZER = _env("ML_TEXT_ANALYZER", "ml.inference.text_analyzer:analyze_text")
    ML_URL_ANALYZER = _env("ML_URL_ANALYZER", "ml.inference.url_analyzer:analyze_url")
    ML_PAYLOAD_ANALYZER = _env("ML_PAYLOAD_ANALYZER", "ml.inference.qr_analyzer:analyze_payload")
    ML_INFO_FUNC = _env("ML_INFO_FUNC")

    LOG_LEVEL = _env("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        for key in ("SECRET_KEY", "JWT_SECRET_KEY"):
            if not getattr(cls, key):
                # Dev only: ephemeral secret (tokens die on restart).
                setattr(cls, key, secrets.token_urlsafe(48))
                log.warning("%s not set; using an ephemeral secret. Set it in .env.", key)


class DevelopmentConfig(BaseConfig):
    DEBUG = _env("FLASK_DEBUG", "1") in ("1", "true", "True")


class ProductionConfig(BaseConfig):
    APP_ENV = "production"
    DEBUG = False

    @classmethod
    def validate(cls) -> None:
        missing = [k for k in ("SECRET_KEY", "JWT_SECRET_KEY") if not getattr(cls, k)]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


class TestConfig(BaseConfig):
    APP_ENV = "testing"
    TESTING = True
    SECRET_KEY = "test-secret-key-not-for-production-0123456789abcdef"
    JWT_SECRET_KEY = "test-jwt-secret-key-not-for-production-0123456789abcdef"
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # in-memory
    RATELIMIT_ENABLED = False
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:1000"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    MAX_CONTENT_LENGTH = 600_000
    QR_MAX_UPLOAD_BYTES = 200_000
    ML_PROJECT_PATH = None


_CONFIGS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestConfig,
}


def get_config(name: str | None = None):
    cfg = _CONFIGS.get((name or _env("APP_ENV", "development")).lower(), DevelopmentConfig)
    cfg.validate()
    return cfg
