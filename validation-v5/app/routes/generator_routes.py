"""
Routes for the GAMP-based document generator.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from ..control.general.generator_config import (
    DOC_TYPES,
    LOADING_MESSAGES,
    LOADING_MAX_TIME_SEC,
    LOADING_TERMINAL_COUNT,
)
from ..control.resources.doc_tables import DOC_TABLES, TABLE_META
from ..services.generator.generator_parsing import parse_table_data
from ..services.generator.generator_service import generate_document
from ..services.generator.generator_session import (
    ensure_generator_session,
    set_toast_error,
    get_common_fields,
    set_common_fields,
)
from ..util.paths import OUTPUT_DIR

generator_bp = Blueprint("generator_bp", __name__)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _json_error(message: str, status_code: int) -> Response:
    resp = jsonify({"error": message})
    resp.status_code = status_code
    return resp


def _safe_filename(filename: str) -> str:
    """Prevent path traversal by dropping any directory components."""
    return Path(filename).name


@generator_bp.route("/generator")
def generator_page():
    return render_template(
        "generator/generator.html",
        title="Generator",
        active_page="generator",
        doc_types=DOC_TYPES,
        toast_error=session.pop("toast_error", None),
    )


@generator_bp.route("/document_inputs", methods=["POST"])
def document_inputs():
    """Collect general fields, store in session, then show doc-specific tables."""
    ensure_generator_session()

    general: Dict[str, Any] = {
        "system_name": request.form.get("system_name", "").strip(),
        "system_version": request.form.get("system_version", "").strip(),
        "doc_type": request.form.get("doc_type", "").strip(),
        "system_type": request.form.get("system_type", "").strip(),
        "complexity": request.form.get("complexity", "").strip(),
        "gxp_impact": request.form.get("gxp_impact", "").strip(),
        "additional_info": request.form.get("additional_info", "").strip(),
    }

    set_common_fields(general)

    doc_type = general.get("doc_type", "")
    if not doc_type or doc_type not in DOC_TABLES:
        current_app.logger.warning("Invalid or missing doc_type submitted: %r", doc_type)
        _set_toast_error("Document type is required.")
        return render_template(
            "generator/generator.html",
            title="Generator",
            active_page="generator",
            doc_types=DOC_TYPES,
            toast_error=session.pop("toast_error", None),
        )

    return render_template(
        "generator/document_inputs.html",
        title="Document Specific Inputs",
        active_page="generator",
        tables=DOC_TABLES[doc_type],
        table_meta=TABLE_META[doc_type],
        doc_type=doc_type,
        toast_error=session.pop("toast_error", None),
        generator_ui_config={
            "loadingMessages": LOADING_MESSAGES,
            "loadingMaxTimeSec": LOADING_MAX_TIME_SEC,
            "loadingTerminalCount": LOADING_TERMINAL_COUNT,
        },
    )


@generator_bp.route("/initialize_document", methods=["POST"])
def initialize_document():
    """Generate the document (AJAX/POST) and return the done page with download link."""
    ensure_generator_session()

    table_data_raw = request.form.get("table_data")
    table_data, err, status = parse_table_data(table_data_raw)
    if err:
        return _json_error(err, status)

    general = get_common_fields()
    doc_type = str(general.get("doc_type") or "").strip()
    if not doc_type:
        return _json_error("Missing doc_type in session.", 400)

    result = generate_document(doc_type=doc_type, common_fields=general, table_data=table_data)
    if not result.ok or not result.output_path:
        return _json_error(result.json_error or "Unknown error.", result.status_code)

    return render_template(
        "generator/done.html",
        title="Done",
        active_page="generator",
        download_url=url_for("generator_bp.download_docx", filename=result.output_path.name),
    )


@generator_bp.route("/download/<filename>", methods=["GET"])
def download_docx(filename: str):
    """Download a generated DOCX from the output directory."""
    safe_name = _safe_filename(filename)
    file_path = OUTPUT_DIR / safe_name

    if not file_path.exists():
        return _json_error("File not found", 404)

    return send_file(str(file_path), as_attachment=True)