from __future__ import annotations

from typing import Any, Dict

from flask import session


COMMON_FIELDS_KEY = "common_fields"


def ensure_generator_session() -> None:
    """Ensure the generator session has the expected structure."""
    if not isinstance(session.get(COMMON_FIELDS_KEY), dict):
        session[COMMON_FIELDS_KEY] = {}
        session.modified = True


def set_toast_error(message: str) -> None:
    """Store a toast error message to display on the next page load."""
    session["toast_error"] = message
    session.modified = True


def set_common_fields(common_fields: Dict[str, Any]) -> None:
    """Store common (general) fields for the generator in server-side session."""
    ensure_generator_session()
    session[COMMON_FIELDS_KEY] = common_fields
    session.modified = True


def get_common_fields() -> Dict[str, Any]:
    """Read common fields from session (returns {} if missing)."""
    ensure_generator_session()
    data = session.get(COMMON_FIELDS_KEY)
    return data if isinstance(data, dict) else {}