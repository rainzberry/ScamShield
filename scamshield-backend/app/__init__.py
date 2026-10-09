"""ScamShield AI backend - Flask application factory (modular monolith)."""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from flask import Flask, g

__version__ = "1.0.0"


def _configure_logging(app: Flask) -> None:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=app.config.get("LOG_LEVEL", "INFO"),
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    root.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def create_app(config_object=None, ml_engine=None) -> Flask:
    """Build the app. `ml_engine` lets tests inject an engine with the MLEngine interface."""
    # Imports are local so lightweight modules (analyzers, security helpers) can be imported
    # and unit-tested without initialising the whole Flask extension stack.
    from . import models  # noqa: F401  (registers tables)
    from .config import get_config
    from .errors.handlers import register_error_handlers
    from .extensions import cors, db, jwt, limiter, migrate
    from .routes import register_blueprints
    from .security.headers import register_security_headers
    from .services.ml_adapter import MLEngine

    app = Flask(__name__)
    app.config.from_object(config_object or get_config())
    app.json.sort_keys = False
    _configure_logging(app)
    Path(app.config["INSTANCE_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "OPTIONS"],
        expose_headers=["Content-Disposition", "X-Request-ID"],
        supports_credentials=False,   # Bearer tokens in headers; no cookies
        max_age=600,
    )

    @app.before_request
    def _assign_request_id():
        g.request_id = uuid.uuid4().hex[:12]

    register_error_handlers(app)
    register_security_headers(app)
    register_blueprints(app)

    engine = ml_engine or MLEngine.from_config(app.config)
    app.extensions["ml_engine"] = engine
    if ml_engine is None:
        engine.preload()          # load ML code/models once at startup (never per request)

    if app.config["AUTO_CREATE_DB"]:
        with app.app_context():
            db.create_all()
    return app
