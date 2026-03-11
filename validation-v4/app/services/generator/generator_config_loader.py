from __future__ import annotations

from typing import Any, Dict, Tuple

from ...control.resources.doc_output_structure import DOCUMENT_SCHEMA
from ...control.resources.doc_sections_template import DOC_SECTIONS_TEMPLATE


def get_doc_config(doc_type: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Fetch configuration objects for a doc type.

    Returns: (section_templates, schema)
    Raises: KeyError if missing.
    """
    section_templates = DOC_SECTIONS_TEMPLATE.get(doc_type)
    schema = DOCUMENT_SCHEMA.get(doc_type)

    if not section_templates:
        raise KeyError(f"Missing DOC_SECTIONS_TEMPLATE for doc_type={doc_type}")

    if not schema:
        raise KeyError(f"Missing DOCUMENT_SCHEMA for doc_type={doc_type}")

    return section_templates, schema
