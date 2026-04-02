"""
gamp_loader.py

Purpose
-------
This script ingests a curated GAMP 5 JSON knowledge base into a persistent ChromaDB collection.
It transforms the JSON structure into "chunks" (small searchable text blocks) and stores them
with metadata to support future retrieval and filtering.

Why this exists
---------------
The application uses GAMP excerpts to answer questions and generate validation documents.
Instead of storing the full book text as one large blob, we split it into chapters and tables:
- Chapter body text -> one chunk per chapter
- Table content      -> one chunk per table

This makes future search more precise and allows filtering by:
- document type usage (e.g., VP, RA, VR, ...)
- chapter/table metadata

Input JSON format (expected)
----------------------------
gamp.json should look like:

{
  "document_title": "GAMP 5 ...",
  "chapters": [
    {
      "chapter_title": "Chapter name",
      "body_text": "Full text ...",
      "used_for": ["VP", "RA"],  # or "VP, RA"
      "tables": [
        {
          "table_id": "T1",
          "table_title": "Some table",
          "markdown": "| ... |",     # OR
          "rows": [ {..}, {..} ],    # OR
          "text": "free text table"
        }
      ]
    }
  ]
}

Important:
- used_for is optional; if missing, the chunk will have used_for="".
- tables are optional.

Output (ChromaDB)
-----------------
A ChromaDB persistent collection containing:
- documents: chunk text
- metadatas: chunk attributes (chapter_title, chunk_type, table_id, used_for, ...)

This collection can later be queried to retrieve only the relevant chunks for a specific document type.

How to run (developer)
----------------------
python -m app.util.gamp_loader

This will:
- delete the existing collection if present
- create a fresh collection
- ingest the JSON

"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import chromadb
from chromadb.utils import embedding_functions

from .paths import APP_ROOT, CHROMA_DIR

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

# Input GAMP JSON file location.
JSON_PATH = APP_ROOT / "resources" / "gamp.json"

# Name of the Chroma collection that will store GAMP chunks.
COLLECTION_NAME = "GAMP5"

# Embedding model used by Chroma.
EMBED_MODEL = "all-MiniLM-L6-v2"


def normalize_used_for(value: Any) -> str:
    """
    Normalize the `used_for` attribute into a CSV uppercase string (e.g. "VA,VP").

    The source JSON may provide used_for in multiple formats:
    - None
    - ["VA", "VP"]
    - "VA, VP"

    Returns
    -------
    str
        A comma-separated list of uppercase tokens, in a stable order, with duplicates removed.
        If input is None or invalid, returns an empty string "".

    Examples
    --------
    normalize_used_for(["va", "VP"]) -> "VA,VP"
    normalize_used_for("VA, VP")     -> "VA,VP"
    normalize_used_for(None)         -> ""
    """
    if value is None:
        return ""

    if isinstance(value, list):
        tokens = [str(x).strip().upper() for x in value if str(x).strip()]
    elif isinstance(value, str):
        tokens = [t.strip().upper() for t in value.split(",") if t.strip()]
    else:
        return ""

    seen = set()
    out: List[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)

    return ",".join(out)


def table_to_text(table_obj: Dict[str, Any]) -> str:
    """
    Convert a table object from the JSON into a text representation.

    Supported input formats
    -----------------------
    1) Markdown string:
       table_obj["markdown"] = "| A | B | ... |"
    2) Rows format:
       table_obj["rows"] = [ {"col1": "...", "col2": "..."}, ... ]
       -> converted to a simple markdown table for readability
    3) Free-form text:
       table_obj["text"] = "..."

    Parameters
    ----------
    table_obj : Dict[str, Any]
        Table object extracted from the JSON.

    Returns
    -------
    str
        Normalized table text. Returns "" if no supported content was found.
    """
    md = table_obj.get("markdown")
    if isinstance(md, str) and md.strip():
        return md.strip()

    txt = table_obj.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt.strip()

    rows = table_obj.get("rows")
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        headers = list(rows[0].keys())
        lines: List[str] = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for r in rows:
            vals = [str(r.get(h, "")).replace("\n", " ").strip() for h in headers]
            lines.append("| " + " | ".join(vals) + " |")

        return "\n".join(lines).strip()

    return ""


def build_chunks(root: Dict[str, Any]) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Transform the root JSON into chunk lists for Chroma ingestion.

    Chunk strategy
    --------------
    - One chunk for each chapter body_text (if non-empty)
    - One chunk for each table (if convertible to text)

    Returns
    -------
    Tuple[List[str], List[str], List[Dict[str, Any]]]
        ids   : stable unique chunk identifiers
        docs  : chunk text
        metas : metadata dictionaries aligned with ids/docs

    Notes
    -----
    Each chunk includes "used_for" metadata (CSV string).
    This enables future filtering (e.g., load only chunks relevant for VP).
    """
    doc_title = root.get("document_title", "GAMP")
    chapters = root.get("chapters", []) or []

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    for ch_i, ch in enumerate(chapters, start=1):
        chapter_title = (ch.get("chapter_title") or f"Chapter {ch_i}").strip()
        body_text = (ch.get("body_text") or "").strip()
        ch_used_for = normalize_used_for(ch.get("used_for"))

        if body_text:
            ids.append(f"ch::{ch_i}::body")
            docs.append(body_text)
            metas.append(
                {
                    "doc_title": doc_title,
                    "chapter_index": ch_i,
                    "chapter_title": chapter_title,
                    "chunk_type": "chapter_body",
                    "used_for": ch_used_for,
                }
            )

        for t_i, t in enumerate(ch.get("tables", []) or [], start=1):
            table_id = (t.get("table_id") or f"T{t_i}").strip()
            table_title = (t.get("table_title") or "").strip()

            table_text = table_to_text(t)
            if not table_text:
                continue

            ids.append(f"ch::{ch_i}::table::{table_id}")
            docs.append(f"{chapter_title}\n{table_title}\n\n{table_text}".strip())
            metas.append(
                {
                    "doc_title": doc_title,
                    "chapter_index": ch_i,
                    "chapter_title": chapter_title,
                    "chunk_type": "table",
                    "table_id": table_id,
                    "table_title": table_title,
                    "used_for": ch_used_for,
                }
            )

    return ids, docs, metas


def ingest() -> None:
    """
    Ingest the GAMP JSON into a ChromaDB persistent collection.

    What this function does
    -----------------------
    1) Read gamp.json
    2) Convert it to chunks (chapter bodies + tables)
    3) Create (or recreate) a ChromaDB collection
    4) Embed and store all chunk documents + metadata

    Side effects
    ------------
    - Deletes the existing collection named COLLECTION_NAME if it exists.
      This means re-running ingest() rebuilds the entire knowledge base.

    Raises
    ------
    FileNotFoundError
        If gamp.json is missing.
    ValueError
        If no chunks are generated (e.g., JSON contains no body_text/tables).
    """
    print("🚀 Starting GAMP loader...")
    print(f"📄 JSON_PATH:   {JSON_PATH}")
    print(f"📦 CHROMA_PATH: {CHROMA_DIR}")
    print(f"🧠 EMBED_MODEL: {EMBED_MODEL}")
    print(f"📚 COLLECTION:  {COLLECTION_NAME}")
    print("-" * 60)

    if not JSON_PATH.exists():
        raise FileNotFoundError(f"JSON not found: {JSON_PATH}")

    print("🔎 Reading JSON...")
    root = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    chapters = root.get("chapters", []) or []
    print(f"📘 Chapters found: {len(chapters)}")

    print("🧩 Building chunks (chapter bodies + tables)...")
    ids, docs, metas = build_chunks(root)

    if not ids:
        raise ValueError("No chunks produced. Check body_text/tables in JSON.")

    n_body = sum(1 for m in metas if m.get("chunk_type") == "chapter_body")
    n_tables = sum(1 for m in metas if m.get("chunk_type") == "table")
    used_for_nonempty = sum(1 for m in metas if (m.get("used_for") or "").strip())

    print(f"✅ Chunks built: {len(ids)} (body={n_body}, tables={n_tables})")
    print(f"🏷️  Chunks with used_for set: {used_for_nonempty}/{len(ids)}")

    print("📂 Initializing Chroma persistent client...")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    print("🧹 Resetting collection (if exists)...")
    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f" ↳ Deleted existing collection '{COLLECTION_NAME}'")
    else:
        print("  ↳ No existing collection to delete")

    print("🧠 Loading embedding function...")
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    print("📚 Creating collection...")
    col = client.create_collection(name=COLLECTION_NAME, embedding_function=embedder)

    print("⬆️  Adding documents to Chroma (this can take a moment)...")
    col.add(ids=ids, documents=docs, metadatas=metas)

    print("-" * 60)
    print(f"🎉 Done! Ingested {len(ids)} chunks into '{COLLECTION_NAME}'")
    print(f"📂 JSON:   {JSON_PATH}")
    print(f"📂 Chroma: {CHROMA_DIR}")


if __name__ == "__main__":
    ingest()