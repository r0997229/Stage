from __future__ import annotations

import json

from flask import current_app
from ..openai_client import get_openai_client
from app.resources.instructions.template_instructions import INSTRUCTIONS

def parse_template_to_dict(template_text: str) -> str:
    """Normalize a payload to the authoritative schema.

    Args:
        prompt: Normalizer prompt containing authoritative schema, tables, and draft.

    Returns:
        Final JSON as python dict.

    Raises:
        OpenAIError: If API request fails.
        ValueError: If output cannot be parsed as JSON dict.
    """
    client = get_openai_client()

    response = client.responses.create(
        model="gpt-4o",
        instructions=INSTRUCTIONS,
        input=template_text,
    )

    return getattr(response, "output_text", None)