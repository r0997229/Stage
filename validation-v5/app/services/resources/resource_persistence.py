from __future__ import annotations

from pathlib import Path
import json
import tempfile
import os
from typing import Any, Dict


def persist_python_dict_constant(module_file: str, constant_name: str, data: Dict[str, Any]) -> None:
    path = Path(module_file).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Resource file not found: {path}")

    header = (
        '"""AUTO-GENERATED FILE.\n'
        "Updated by the template ingest workflow.\n"
        '"""\n\n'
    )

    json_text = json.dumps(data, indent=2, ensure_ascii=False)

    body = f"{constant_name} = {json_text}"

    new_content = header + body

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=path.stem + "_", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)