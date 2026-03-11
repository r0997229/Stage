from __future__ import annotations

from typing import Any, Dict, List, Tuple

from flask import session

from ...control.general.chatbot_config import MAX_EXCHANGES


def ensure_chatbot_session() -> None:
    """Ensure the session contains the expected chatbot storage keys."""
    if not isinstance(session.get("exchanges"), list):
        session["exchanges"] = []
        session.modified = True

def set_toast_error(message: str) -> None:
    """Set a toast error message for the next page load."""
    session["toast_error"] = message
    session.modified = True

def append_exchange(question: str, reply: List[str], sources: List[Dict[str, str]]) -> None:
    """Append a new chatbot exchange to the session."""
    exchanges = session.get("exchanges", [])
    
    if len(exchanges) >= MAX_EXCHANGES:
        exchanges.pop(0)

    exchanges.append(
        {
            "question": question,
            "reply": reply,
            "sources": sources,
        }
    )

    session["exchanges"] = exchanges
    session.modified = True