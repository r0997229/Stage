from __future__ import annotations

import json
from itertools import groupby

from docx2pdf import convert
from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.config import Config
from app.control.ai_call_param.verificator_param import MODEL, EFFORT, VERBOSITY, SYSTEM, INSTRUCTIONS
from app.control.resources.gamp_text import GAMP_TEXT
from app.crud.verificator.project_crud import ProjectCRUD
from app.crud.verificator.suggestion_crud import SuggestionCRUD
from app.crud.verificator.user_crud import UserCRUD
from app.services.openai_api_call import call_openai
from app.services.verificator.prompt_builder_verificator import build_verificator_prompt
from app.util.paths import UPLOAD_DIR

verificator_bp = Blueprint("verificator_bp", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@verificator_bp.route("/verificator")
def verificator_page():
    return render_template(
        "verificator/verificator.html",
        title="Verificator",
        active_page="verificator",
    )


@verificator_bp.route("/document_retrieval", methods=["POST"])
def document_retrieval():

    # --- 1. Bestand valideren ---
    file = request.files.get("document")
    if not file or file.filename == "":
        return redirect(url_for("verificator_bp.verificator_page"))

    if not allowed_file(file.filename):
        return redirect(url_for("verificator_bp.verificator_page"))

    # --- 2. Bestand opslaan ---
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = UPLOAD_DIR / filename
    file.save(file_path)

    # --- 3. DOCX → PDF ---
    if str(file_path).endswith(".docx"):
        pdf_path = file_path.with_suffix(".pdf")
        convert(str(file_path), str(pdf_path))
        file_path = pdf_path

    try:
        # --- 4. AI analyse ---
        result = call_openai(
            prompt=build_verificator_prompt(),
            model=MODEL,
            effort=EFFORT,
            verbosity=VERBOSITY,
            system=SYSTEM,
            instructions=INSTRUCTIONS,
            file_path=str(file_path),
        )

        # --- 5. Project aanmaken ---
        owner = UserCRUD.get_or_create_default()
        project = ProjectCRUD.create(
            title=filename,
            owner_id=owner.id,
        )

        # --- 6. Suggesties aanmaken vanuit AI resultaat ---
        # result verwacht: {"suggestions": [{"section": ..., "title": ..., "description": ...}]}
        suggestions_data = result.get("suggestions", [])

        for item in suggestions_data:
            SuggestionCRUD.create(
                section=item["section"],
                title=item["title"],
                description=item["description"],
                source=item["source"],                     # ← nieuw
                project_id=project.id,
            )

        # --- 7. Groeperen per sectie voor de template ---
        suggestions = SuggestionCRUD.list_by_project(project.id)
        grouped = {
            section: list(items)
            for section, items in groupby(suggestions, key=lambda s: s.section)
        }

    except json.JSONDecodeError as exc:
        flash(f"AI antwoord is geen geldige JSON: {exc}", "error")
        return redirect(url_for("verificator_bp.verificator_page"))

    except ValueError as exc:
        flash(f"Validatiefout: {exc}", "error")
        return redirect(url_for("verificator_bp.verificator_page"))

    except KeyError as exc:
        flash(f"Verwacht veld ontbreekt in AI antwoord: {exc}", "error")
        return redirect(url_for("verificator_bp.verificator_page"))

    except Exception as exc:
        flash(f"Onverwachte fout ({type(exc).__name__}): {exc}", "error")
        return redirect(url_for("verificator_bp.verificator_page"))
    finally:
        if file_path.exists():
            file_path.unlink()

    return render_template(
        "verificator/results.html",
        title="Résultats de l'analyse",
        active_page="verificator",
        project=project,
        grouped=grouped,
    )

@verificator_bp.route("/project/<uuid:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    ProjectCRUD.delete(project_id)
    return redirect(url_for("verificator_bp.verificator_page"))