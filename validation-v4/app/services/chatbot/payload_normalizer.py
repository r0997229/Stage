from __future__ import annotations

from typing import Any, Dict, List, Tuple


def normalize_reply_and_sources(reply: Any, sources: Any) -> Tuple[List[str], List[Dict[str, str]]]:
    """Normalize model payload fields to the UI contract.

    Args:
        reply: Model reply payload. Expected list[str] but may be str.
        sources: Model sources payload. Expected list[dict].

    Returns:
        Tuple (reply_list, sources_list)
    """
    # Normalize reply -> list[str]
    if isinstance(reply, str):
        reply_list = [reply.strip()] if reply.strip() else []
    elif isinstance(reply, list):
        reply_list = [p.strip() for p in reply if isinstance(p, str) and p.strip()]
    else:
        reply_list = []

    # Normalize sources -> list[{"source": str, "proof": str}]
    sources_list: List[Dict[str, str]] = []
    if isinstance(sources, list):
        for s in sources:
            if not isinstance(s, dict):
                continue
            src = str(s.get("source", "")).strip()
            proof = str(s.get("proof", "")).strip()
            if src and proof:
                sources_list.append({"source": src, "proof": proof})

    return reply_list, sources_list