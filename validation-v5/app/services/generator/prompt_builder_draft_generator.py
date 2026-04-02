# app/services/prompt_builder_draft_generator.py

"""Prompt builder for the Draft Generator assistant.

The draft generator must:
- Return JSON only
- Match the schema EXACTLY (keys, nesting, ordering)
- Leave array/table fields empty [] (tables are handled by the normalizer)
"""

from __future__ import annotations

import json
from typing import Any, Dict, Mapping


# ============================================================
# Helpers
# ============================================================
def _json_block(data: Any) -> str:
    """Render python objects as formatted JSON for prompt clarity."""
    return json.dumps(data, indent=2, ensure_ascii=False)
    

# ============================================================
# Generator Prompt Builder
# ============================================================
def build_draft_prompt(
    doc_type: str,
    common_fields: Dict[str, Any],
    doc_specific_fields: Dict[str, Any],
    section_templates: Mapping[str, Any],
    output_structure: Mapping[str, Any],
    gamp_context: str,
    fixed: str,
) -> str:
    """Build the prompt used to generate the draft JSON.

    Args:
        doc_type: Document type key (VP, RA, VR).
        common_fields: General form inputs stored in session.
        doc_specific_fields: Table inputs submitted by the user.
        section_templates: Narrative templates per section.
        output_structure: Authoritative output structure for draft (same keys as final).
        gamp_context: GAMP excerpts used for framing language.

    Returns:
        Prompt string.
    """
    schema_block = _json_block(output_structure)
    templates_block = _json_block(section_templates)
    general_block = _json_block(common_fields)
    tables_block = _json_block(doc_specific_fields)

    prompt = f"""
You are a pharmaceutical validation expert specialized in GAMP 5 Second Edition.

Generate a COMPLETE DRAFT of a {doc_type} document.

{fixed}

OUTPUT STRUCTURE (DRAFT SCHEMA)
{schema_block}

SECTION TEMPLATES 
{templates_block}

GAMP 5 CONTEXT
{gamp_context}

GENERAL INFORMATION 
{general_block}

DOCUMENT SPECIFIC INFORMATION (TABLES) 
{tables_block}

Now generate the DRAFT JSON.
"""
    return prompt.strip()