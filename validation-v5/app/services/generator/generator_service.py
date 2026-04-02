from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from openai import OpenAIError

from ...control.ai_call_param import generator_draft_param as draft_cfg
from ...control.ai_call_param import generator_normalizer_param as norm_cfg
from ...control.resources.gamp_text import GAMP_TEXT
from ...util.paths import APP_ROOT, OUTPUT_DIR
from ...models.generator_response import GeneratorResponse
from ..openai_api_call import call_openai
from .generator_config_loader import get_doc_config
from .docx_renderer import render_docx
from ..generator.prompt_builder_draft_generator import build_draft_prompt
from ..generator.prompt_builder_normalizer_generator import build_normalizer_prompt


def generate_document(doc_type: str, common_fields: Dict[str, Any], table_data: Dict[str, Any]) -> GeneratorResponse:
    """Generate and render a DOCX document.

    Returns GeneratorResponse with either output_path or a json_error.
    """
    # Load per-doc config
    try:
        section_templates, schema = get_doc_config(doc_type)
    except KeyError as exc:
        return GeneratorResponse(ok=False, json_error=str(exc), status_code=400)

    # Build draft prompt
    draft_prompt = build_draft_prompt(
        doc_type=doc_type,
        common_fields=common_fields,
        doc_specific_fields=table_data,
        section_templates=section_templates,
        output_structure=schema,
        gamp_context=GAMP_TEXT,
        fixed=draft_cfg,
    )

    # Call 1: draft
    try:
        draft_payload = call_openai(
            draft_prompt,
            draft_cfg.MODEL,
            draft_cfg.EFFORT,
            draft_cfg.VERBOSITY,
            draft_cfg.SYSTEM,
            draft_cfg.INSTRUCTIONS,
        )
        if draft_payload is None:
            return GeneratorResponse(ok=False, json_error="AI draft returned invalid JSON.", status_code=502)
    except OpenAIError:
        return GeneratorResponse(ok=False, json_error="AI draft generation failed", status_code=502)

    # Build normalizer prompt
    normalizer_prompt = build_normalizer_prompt(
        fixed=norm_cfg.PROMPT,
        draft=draft_payload,
        output_structure=schema,
        tables=table_data,
    )

    # Call 2: normalize
    try:
        final_payload = call_openai(
            normalizer_prompt,
            norm_cfg.MODEL,
            norm_cfg.EFFORT,
            norm_cfg.VERBOSITY,
            norm_cfg.SYSTEM,
            norm_cfg.INSTRUCTIONS,
        )
        if final_payload is None:
            return GeneratorResponse(ok=False, json_error="AI normalizer returned invalid JSON.", status_code=502)
    except OpenAIError:
        return GeneratorResponse(ok=False, json_error="AI normalization failed", status_code=502)

    # Render DOCX
    template_path = APP_ROOT / "control" / "templates_docx" / f"{doc_type}_Template.docx"
    if not template_path.exists():
        return GeneratorResponse(ok=False, json_error=f"Template not found: {template_path.name}", status_code=404)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = uuid4().hex[:8]
    output_path = OUTPUT_DIR / f"{doc_type}_{run_id}.docx"

    try:
        render_docx(template_path=template_path, output_path=output_path, sections=final_payload)
    except Exception:
        return GeneratorResponse(ok=False, json_error="DOCX rendering failed", status_code=500)

    return GeneratorResponse(ok=True, output_path=output_path, status_code=200)
