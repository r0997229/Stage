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


def build_prompt() -> str:
    """
    Compose the full prompt sent to GPT-4o.

    The GAMP 5 reference text is prepended as grounding context so the model
    can only draw conclusions anchored in ISPE GAMP 5 Second Edition.
    """
    return (
        "You are a pharmaceutical IT validation expert. "
        "You must base every suggestion exclusively on the GAMP 5 Second Edition "
        "reference text provided below. Do not use any external knowledge.\n\n"
        "=== GAMP 5 REFERENCE TEXT (start) ===\n"
        f"{GAMP_TEXT}\n"
        "=== GAMP 5 REFERENCE TEXT (end) ===\n\n"
        "Analyze the attached document against the GAMP 5 principles above.\n\n"
        "For each section of the document, provide actionable suggestions to improve "
        "its compliance with GAMP 5.\n\n"
        "Output format requirements:\n"
        "- The response must be valid JSON only — no markdown, no prose outside the JSON.\n"
        "- Each key must be the exact section title found in the document.\n"
        "- Each value must be a list of suggestion strings for that section.\n"
        "- If a section has no suggestions, return an empty list as its value.\n\n"
        'Example: {"1 Introduction": ["Add a GxP impact statement."], "2 Scope": []}'
    )


def send_to_gpt(file_path: str) -> dict:
    """
    Upload *file_path* to the OpenAI Files API and request a GAMP 5 analysis.

    Returns:
        Parsed JSON dict of {section_title: [suggestions]}.

    Raises:
        json.JSONDecodeError: If the model returns non-JSON text.
        openai.OpenAIError: On any API-level error.
    """
    from openai import OpenAI

    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    with open(file_path, "rb") as f:
        uploaded_file = client.files.create(file=f, purpose="user_data")

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": uploaded_file.id},
                    {"type": "input_text", "text": build_prompt()},
                ],
            }
        ],
    )

    client.files.delete(uploaded_file.id)

    return json.loads(response.output_text)


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
        result = send_to_gpt(str(file_path))
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