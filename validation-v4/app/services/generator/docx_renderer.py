from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from docxtpl import DocxTemplate
from jinja2 import Environment


def flatten_sections_to_context(sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Flatten nested JSON into docxtpl context:
    context key format: '<section_key>_<field_key>'
    """
    context: Dict[str, Any] = {}
    for section_key, sec_data in sections.items():
        if not isinstance(sec_data, dict):
            continue
        for key, value in sec_data.items():
            context[f"{section_key}_{key}"] = value
    return context


def render_docx(template_path: Path, output_path: Path, sections: Dict[str, Dict[str, Any]]) -> None:
    """Render DOCX using docxtpl."""
    doc = DocxTemplate(str(template_path))
    context = flatten_sections_to_context(sections)
    jinja_env = Environment(autoescape=False)

    doc.render(context, jinja_env=jinja_env)
    doc.save(str(output_path))
