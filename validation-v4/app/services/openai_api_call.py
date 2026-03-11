#app\services\openai_api_call.py

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from flask import current_app

from openai import OpenAIError
from .openai_client import get_openai_client

def call_openai(
    prompt: str,
    model: str,
    effort: str,
    verbosity: str,
    system: str,
    instructions: str,
) -> Optional[Dict[str, Any]]:
    """
    Call the OpenAI API with structured input data and return a parsed JSON response.

    This function sends input data to the OpenAI model and applies system-level
    instructions and generation constraints to produce a structured JSON output.

    Args:
        prompt:
            The input data sent to the model. This parameter contains the raw
            information or data on which the instructions will be applied.

        model:
            The OpenAI model used to generate the response.

        effort:
            Controls the reasoning effort applied by the model during response
            generation.

        verbosity:
            Controls the verbosity level of the generated response.

        system:
            System-level prompt defining the global behavior and role of the model.

        instructions:
            High-level instructions that define how the model should process
            the input data provided in the prompt.

    Returns:
        Optional[Dict[str, Any]]:
            A dictionary parsed from the model JSON response if parsing succeeds,
            otherwise None.

    Raises:
        OpenAIError:
            If the OpenAI API call fails.
    """
    client = get_openai_client()

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    if effort:
        payload["reasoning"] = {"effort": effort}

    if verbosity:
        payload["text"] = {"verbosity": verbosity}

    if instructions:
        payload["instructions"] = instructions

    try:
        response = client.responses.create(**payload)
    except OpenAIError as exc:
        current_app.logger.exception(
            "OpenAI API error in GAMP assistant: %s", exc
        )
        raise

    raw = getattr(response, "output_text", None)
    return _parse_json_dict(raw)


def _parse_json_dict(raw: Any) -> Optional[Dict[str, Any]]:
    """
    Parse a JSON dictionary from a raw OpenAI text response.

    This function attempts to extract and parse a valid JSON object from a raw
    text response returned by the OpenAI API. It supports multiple response
    formats, including:
    - Plain JSON strings
    - JSON wrapped in Markdown code blocks
    - JSON embedded within additional text

    The function is designed to be tolerant to formatting inconsistencies
    commonly produced by language models.

    Args:
        raw (Any):
            Raw output returned by the OpenAI API. This value is expected to be
            a string but may contain extra text or formatting.

    Returns:
        Optional[Dict[str, Any]]:
            A parsed JSON dictionary if extraction and parsing succeed,
            otherwise None.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None

    text = raw.strip()

    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass

    if text.startswith("```"):
        text = text.strip("`").replace("json", "", 1).strip()

    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        obj = json.loads(text[start : end + 1])
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None