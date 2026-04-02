# app/services/prompt_builder_normalizer_generator.py

from __future__ import annotations

import json
from typing import Any, Dict, Mapping


# ============================================================
# Helpers
# ============================================================
def _json_block(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)

# ============================================================
# Normalizer Prompt Builder
# ============================================================
def build_normalizer_prompt(
    fixed: str,
    draft: Dict[str, Any],
    output_structure: Mapping[str, Any],
    tables: Dict[str, Any],
) -> str:
    schema_block = _json_block(output_structure)
    tables_block = _json_block(tables)
    draft_block = _json_block(draft)

    prompt = f"""
{fixed}

------------------------------------------------------------------------------

OUTPUT JSON STRUCTURE (AUTHORITATIVE)
{schema_block}


TABLES (AUTHORITATIVE FOR ARRAYS)
{tables_block}


DRAFT (AUTHORITATIVE FOR NARRATIVE TEXT)
{draft_block}

----------------------------------------------------------------------------

IMPORTANT:
Do not begin generating the JSON until you have fully parsed:
1) OUTPUT_STRUCTURE
2) TABLES
3) DRAFT

------------------------------------------------------------------------------

Now produce the final structured JSON.
"""
    return prompt.strip()