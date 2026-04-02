"""
Routes for the GAMP chatbot functionality.
"""

from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for


from ..control.general.chatbot_config import (
    MAX_QUESTION_CHARS, 
    LOADING_MESSAGES, 
    LOADING_MAX_TIME_SEC,
    LOADING_TERMINAL_COUNT,
)
from ..services.chatbot.chatbot_session import ensure_chatbot_session, set_toast_error, append_exchange
from ..services.chatbot.chatbot_service import ask_gamp

chatbot_bp = Blueprint("chatbot_bp", __name__)


@chatbot_bp.route("/")
@chatbot_bp.route("/chatbot")
def chatbot_page():
    """Render the chatbot UI.

    Returns:
        The chatbot.html template.
    """
    ensure_chatbot_session()
    draft_question = session.pop("draft_question", "")

    return render_template(
        "chatbot/chatbot.html",
        title="Chatbot",
        active_page="chatbot",
        exchanges=session["exchanges"],
        draft_question=draft_question,
        toast_error=session.pop("toast_error", None),
        chatbot_config={
            "maxQuestionChars": MAX_QUESTION_CHARS,
            "loadingMessages": LOADING_MESSAGES,
            "loadingMaxTimeSec": LOADING_MAX_TIME_SEC,
            "loadingTerminalCount": LOADING_TERMINAL_COUNT,
        },
    )


@chatbot_bp.route("/chatbot_ask", methods=["POST"])
def chatbot_ask():
    """Process a user-submitted GAMP question.

    Flow:
    - Validate input (length, non-empty)
    - Build prompt
    - Call LLM assistant
    - Validate/normalize payload
    - Save exchange
    - Redirect back to /chatbot

    Returns:
        Redirect response to the chatbot page.
    """
    ensure_chatbot_session()
    
    question = request.form.get("question", "").strip()
    if not question:
        return redirect(url_for("chatbot_bp.chatbot_page"))

    # Keep draft in session in case anything fails before we append an exchange
    session["draft_question"] = question
    session.modified = True

    resp = ask_gamp(question)

    # exception path => toast only, keep draft
    if not resp.should_append:
        if resp.toast_error:
            set_toast_error(resp.toast_error)
        return redirect(url_for("chatbot_bp.chatbot_page"))

    # append exchange (success or chat-level error)
    append_exchange(question=question, reply=resp.reply, sources=resp.sources)

    # once appended, clear draft
    session.pop("draft_question", None)
    session.modified = True

    return redirect(url_for("chatbot_bp.chatbot_page"))
