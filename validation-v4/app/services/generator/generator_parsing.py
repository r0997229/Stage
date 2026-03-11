from __future__ import annotations

import json
from typing import Any, Dict, Tuple


def parse_table_data(raw: str | None) -> Tuple[Dict[str, Any], str | None, int]:
    """Parse the `table_data` JSON string from the form.

    Returns: (table_data, error_message, http_status)
    """
    if not raw:
        return {}, "Missing table_data", 400

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}, "Invalid JSON in table_data", 400

    if not isinstance(parsed, dict):
        return {}, "table_data must be a JSON object", 400

    return parsed, None, 200
