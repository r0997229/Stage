#app\util\paths.py
"""
paths.py

Centralized filesystem paths for the application.

Why this exists
---------------
The application generates runtime data:
- server-side sessions
- generated DOCX files
- local ChromaDB persistence

These are not application code, so they belong outside the Python package
folder (`app/`) and should be grouped for easier backups/cleanup.

This module provides a single source of truth for all such paths.
"""

from __future__ import annotations

from pathlib import Path

# Absolute paths
APP_ROOT = Path(__file__).resolve().parents[1]        # .../<project>/app
PROJECT_ROOT = APP_ROOT.parent                       # .../<project>

# Runtime storage folder (all generated files)
STORAGE_ROOT = PROJECT_ROOT / "storage"

# Subfolders (runtime)
SESSIONS_DIR = STORAGE_ROOT / "sessions"
OUTPUT_DIR = STORAGE_ROOT / "output"
UPLOAD_DIR = STORAGE_ROOT / "upload"
CHROMA_DIR = STORAGE_ROOT / "chroma_db"