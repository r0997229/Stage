# app/__init__.py
"""Flask application factory and blueprint registration."""

from __future__ import annotations

import os

from flask import Flask
from flask_session import Session

from .config import Config
from .routes.chatbot_routes import chatbot_bp
from .routes.generator_routes import generator_bp
from .routes.resource_ingest_routes import resource_ingest_bp
from .util.paths import SESSIONS_DIR


def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    Returns:
        Flask: Configured Flask application.
    """
    # -----------------------------------------------------------------------
    # Enable server-side sessions (Flask-Session)
    #
    # We store session files at the project root: /storage/sessions
    # Reason: session files are runtime data (not application code),
    # and keeping them at the project root simplifies backups and deployments.
    # -----------------------------------------------------------------------
    app = Flask(__name__)
    app.config.from_object(Config)

    # ----------------------------------------
    # Enable server-side sessions (Flask-Session)
    # Store runtime data under /storage/sessions
    # ----------------------------------------
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = str(SESSIONS_DIR)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_FILE_THRESHOLD"] = 500

    Session(app)

    _validate_config(app)
    _register_blueprints(app)
    return app


def _validate_config(app: Flask) -> None:
    """Validate essential configuration values.

    Args:
        app: Flask application instance.

    Raises:
        RuntimeError: If OPENAI_API_KEY is missing.
    """
    if not app.config.get("OPENAI_API_KEY"):
        raise RuntimeError("Environment variable OPENAI_API_KEY is missing.")


def _register_blueprints(app: Flask) -> None:
    """Register all Flask blueprints.

    Args:
        app: Flask application instance.
    """
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(generator_bp)
    app.register_blueprint(resource_ingest_bp)