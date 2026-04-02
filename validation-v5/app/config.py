#app\config.py

"""Application configuration module."""

from __future__ import annotations

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Base configuration for the Flask application."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
