# app/services/openai_client.py
"""OpenAI client factory for the Flask application."""

from __future__ import annotations

from typing import Optional

from flask import current_app
from openai import OpenAI

_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Return a shared OpenAI client configured from Flask app settings.

    Returns:
        Configured OpenAI client instance.

    Raises:
        RuntimeError: If OPENAI_API_KEY is not configured.
    """
    global _client

    if _client is not None:
        return _client

    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured on the Flask application."
        )

    _client = OpenAI(api_key=api_key)
    return _client