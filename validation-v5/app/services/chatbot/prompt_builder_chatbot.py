# app/services/chatbot/prompt_builder_chatbot.py
"""Prompt construction utilities for the GAMP chatbot.

This prompt assembles the user question and the provided GAMP context
into a single input string that will be sent to the language model.
"""

from __future__ import annotations


def build_chatbot_prompt(question: str, gamp_context: str, fixed: str) -> str:
    """Build a structured prompt for the GAMP chatbot.

    Args:
        question: User's question.
        gamp_context: Grounding context text (GAMP excerpts).

    Returns:
        A single string containing the question and the related GAMP context.
    """
    prompt = f"""
{fixed}

------------------------------------------------------------------------------

USER QUESTION:
{question}

------------------------------------------------------------------------------

GAMP CONTEXT:
{gamp_context}

------------------------------------------------------------------------------

Now answer the question(s)
"""
    return prompt.strip()