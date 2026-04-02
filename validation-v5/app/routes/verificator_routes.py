#app\routes\verificator_routes.py

"""
Verificator blueprint routes.

Handles document upload (PDF or DOCX), converts DOCX to PDF when needed,
sends the file to GPT-4o with a GAMP 5-grounded prompt, and renders the
analysis results.
"""

from __future__ import annotations

import json

from docx2pdf import convert
from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.config import Config
from app.control.ai_call_param.verificator_param import MODEL, EFFORT, VERBOSITY, SYSTEM, INSTRUCTIONS
from app.services.openai_api_call import call_openai
from app.services.verificator.prompt_builder_verificator import build_verificator_prompt
from app.util.paths import UPLOAD_DIR

# ---------------------------------------------------------------------------
# GAMP 5 reference text import.
#
# Your path comment shows:  #app\config\resources\gamp_text.py
# For this import to work, config/ must be a *package*, meaning these files
# must exist:
#   app/config/__init__.py            <- can be empty
#   app/config/resources/__init__.py  <- empty file
#   app/config/resources/gamp_text.py <- already exists
#
# If config is still a plain config.py file, two options:
#   Option A: convert config/ into a package (recommended, keeps structure)
#   Option B: move gamp_text.py to app/resources/gamp_text.py and change
#             this import to:  from app.resources.gamp_text import GAMP_TEXT
# ---------------------------------------------------------------------------
from app.control.resources.gamp_text import GAMP_TEXT

verificator_bp = Blueprint("verificator_bp", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    """Return True when *filename* carries a permitted extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@verificator_bp.route("/verificator")
def verificator_page():
    """Render the verificator upload page."""
    return render_template(
        "verificator/verificator.html",
        title="Verificator",
        active_page="verificator",
    )


@verificator_bp.route("/document_retrieval", methods=["POST"])
def document_retrieval():
    """
    Accept a document upload, run GAMP 5 analysis, and render results.

    Flow:
        1. Validate the uploaded file.
        2. Save to UPLOAD_DIR.
        3. Convert DOCX → PDF when necessary.
        4. Send PDF to GPT-4o via send_to_gpt().
        5. Clean up the local file (always, via finally).
        6. Render the results template.
    """
    file = request.files.get("document")

    if not file or file.filename == "":
        return redirect(url_for("verificator_bp.verificator_page"))

    if not allowed_file(file.filename):
        return redirect(url_for("verificator_bp.verificator_page"))
    
    
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = UPLOAD_DIR / filename
    file.save(file_path)

    # Convert DOCX → PDF so we always send a single format to GPT
    if str(file_path).endswith(".docx"):
        pdf_path = file_path.with_suffix(".pdf")
        convert(str(file_path), str(pdf_path))
        file_path = pdf_path

    try:
        result = call_openai(
            prompt=build_verificator_prompt(),
            model=MODEL,
            effort=EFFORT,
            verbosity=VERBOSITY,
            system=SYSTEM,
            instructions=INSTRUCTIONS,
            file_path=str(file_path),
        )
    except json.JSONDecodeError:
        return redirect(url_for("verificator_bp.verificator_page"))
    except Exception as exc:
        return redirect(url_for("verificator_bp.verificator_page"))
    finally:
        if file_path.exists():
            file_path.unlink()

    return render_template(
        "verificator/results.html",
        title="Résultats de l'analyse",
        active_page="verificator",
        results=result,
    )