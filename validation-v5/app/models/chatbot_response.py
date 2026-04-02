from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ChatbotResponse:
    """Service response for the chatbot controller.

    If should_append is True, the controller appends (question, reply, sources)
    to the conversation history.

    If should_append is False, the controller should show toast_error (if any)
    and keep the draft question.
    """
    should_append: bool
    reply: List[str]
    sources: List[Dict[str, str]]
    toast_error: Optional[str] = None