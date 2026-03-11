"""
gamp_query.py

Purpose
-------
Read the persisted ChromaDB GAMP collection and return a text context filtered by document type.

Current status
--------------
This module is not used yet in the current app flow.
It is planned for a future improvement: reduce the amount of GAMP context injected into prompts
by retrieving only the chunks relevant to the document type (VP, RA, VR, etc.).

Why this matters
----------------
Prompt size impacts:
- cost
- speed
- answer quality (too much context can reduce relevance)

By filtering chunks using metadata ("used_for"), we can:
- provide only the relevant excerpts
- keep prompts smaller and more targeted

Important note (current implementation)
---------------------------------------
This code fetches the full collection via `col.get(..., limit=10**9)` and filters in Python.
This works for small datasets but is not ideal for scaling.
A future improvement would use Chroma query/filtering features directly (where supported),
or maintain a separate index.

"""

from __future__ import annotations

from typing import Any, List

import chromadb

from .paths import CHROMA_DIR

COLLECTION_NAME = "GAMP5"


def used_for_contains(used_for_value: Any, doc_type: str) -> bool:
    """
    Determine whether a chunk metadata "used_for" field includes a given doc type token.

    Parameters
    ----------
    used_for_value : Any
        The metadata field stored for each chunk.
        Expected formats:
        - "VA,VP"
        - ["VA", "VP"]
        - None
    doc_type : str
        A short code representing the target document type, e.g.:
        - "VP" (Validation Plan)
        - "RA" (Risk Assessment)
        - "VR" (Validation Report)
        Input is normalized using .strip().upper().

    Returns
    -------
    bool
        True if doc_type is present as an exact token, else False.

    Notes
    -----
    - Exact token match: "VP" should not match "SVP" by substring.
    """
    dt = doc_type.strip().upper()
    if not dt or used_for_value is None:
        return False

    if isinstance(used_for_value, list):
        tokens = [str(x).strip().upper() for x in used_for_value if str(x).strip()]
    else:
        s = str(used_for_value).strip().upper()
        tokens = [t.strip() for t in s.split(",") if t.strip()]

    return dt in tokens


def get_gamp_context_by_doctype(doc_type: str) -> str:
    """
    Retrieve concatenated chunk texts from ChromaDB filtered by doc_type.

    Parameters
    ----------
    doc_type : str
        Target document type code (e.g. "VP", "RA", "VR").
        The filtering uses the chunk metadata field "used_for".

    Returns
    -------
    str
        A single large text block containing the matching chunks.
        Each chunk is preceded by a header showing:
        - chunk number
        - chapter title
        - chunk type (chapter_body/table)
        - used_for tokens

        If doc_type is empty or no chunk matches, returns "".

    Current limitation (important)
    ------------------------------
    This function currently loads *all* documents and metadatas and filters in Python:
        res = col.get(include=["documents", "metadatas"], limit=10**9)

    This is acceptable for small datasets but not scalable.
    Future improvement should perform metadata filtering directly in the database if possible.

    Usage example (future)
    ----------------------
    context = get_gamp_context_by_doctype("VP")
    prompt = build_draft_prompt(..., gamp_context=context)
    """
    dt = doc_type.strip().upper()
    if not dt:
        return ""

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col = client.get_collection(COLLECTION_NAME)

    # Practical "no limit": request a very large number
    res = col.get(include=["documents", "metadatas"], limit=10**9)

    docs = res.get("documents", []) or []
    metas = res.get("metadatas", []) or []

    parts: List[str] = []
    n = 0

    for doc, meta in zip(docs, metas):
        if used_for_contains(meta.get("used_for"), dt):
            n += 1
            parts.append(
                f"--- Chunk {n} | {meta.get('chapter_title','?')} | {meta.get('chunk_type','?')} | used_for={meta.get('used_for','')} ---\n"
                f"{doc}\n"
            )

    return "\n".join(parts)
