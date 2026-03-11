from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GeneratorResponse:
    """Returned by generator service to the controller."""
    ok: bool
    output_path: Optional[Path] = None
    json_error: Optional[str] = None
    status_code: int = 200
