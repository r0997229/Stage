from __future__ import annotations

import logging
from openai import OpenAIError

from ...control.resources.gamp_text import GAMP_TEXT
from ...control.ai_call_param.chatbot_param import MODEL, EFFORT, VERBOSITY, SYSTEM, INSTRUCTIONS, PROMPT
from ...control.general.chatbot_config import MAX_QUESTION_CHARS
from ..openai_api_call import call_openai
from ..chatbot.prompt_builder_chatbot import build_chatbot_prompt
from .payload_normalizer import normalize_reply_and_sources
from ...models.chatbot_response import ChatbotResponse

logger = logging.getLogger(__name__)


def ask_gamp(question: str) -> ChatbotResponse:
    """Business logic for the chatbot.

    - Non-exception issues (too long, invalid payload, empty reply) are returned as
      chat replies (should_append=True).
    - Exceptions are returned as toast errors (should_append=False).
    """
    # Non-exception validation -> append an exchange with an error reply (your preference)
    if len(question) > MAX_QUESTION_CHARS:
        return ChatbotResponse(
            should_append=True,
            reply=["Your message is too long to process. Please shorten it and try again."],
            sources=[],
        )

    # Prompt building exception -> toast only
    try:
        prompt = build_chatbot_prompt(question=question, gamp_context=GAMP_TEXT, fixed=PROMPT)
    except Exception as exc:
        logger.exception("Chatbot prompt building error: %s", exc)
        return ChatbotResponse(
            should_append=False,
            reply=[],
            sources=[],
            toast_error="Internal prompt preparation error.",
        )

    # AI call exception -> toast only
    try:
        payload = call_openai(prompt, MODEL, EFFORT, VERBOSITY, SYSTEM, INSTRUCTIONS, None)
    except OpenAIError as exc:
        logger.exception("Chatbot OpenAI call failed: %s", exc)
        return ChatbotResponse(
            should_append=False,
            reply=[],
            sources=[],
            toast_error="AI service unavailable. Please try again.",
        )

    if not isinstance(payload, dict):
        logger.error("Chatbot invalid AI payload type: %r", type(payload))
        return ChatbotResponse(
            should_append=True,
            reply=["AI returned invalid data."],
            sources=[],
        )

    reply_raw = payload.get("reply")
    sources_raw = payload.get("sources", [])

    reply_list, sources_list = normalize_reply_and_sources(reply_raw, sources_raw)

    if not reply_list:
        logger.error("Chatbot empty or invalid reply payload: %r", payload)
        return ChatbotResponse(
            should_append=True,
            reply=["Model produced no reply."],
            sources=[],
        )

    return ChatbotResponse(
        should_append=True,
        reply=reply_list,
        sources=sources_list,
        toast_error=None,
    )
