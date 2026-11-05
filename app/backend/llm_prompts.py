"""Read inherited reference prompt files for LLM parsing."""

import os
from pathlib import Path

# app/backend/llm_prompts.py -> up 3 levels = repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_REFERENCES_DIR = _REPO_ROOT / "backend" / "c2vsdx" / "references"


def _read_reference(rel_path: str) -> str:
    path = _REFERENCES_DIR / rel_path
    if not path.is_file():
        raise FileNotFoundError(f"Reference file not found: {path}")
    return path.read_text(encoding="utf-8")


def text_prompt(diagram_type: str) -> str:
    """Prompt for parsing text into a specific diagram type."""
    return _read_reference(os.path.join("parse-prompts", f"{diagram_type}.txt"))


def image_prompt() -> str:
    """Prompt for analyzing a diagram image into JSON."""
    return _read_reference("image-schema.md")


def auto_type_prompt() -> str:
    """Prompt for choosing a diagram type from a text description."""
    return _read_reference("diagram-types.md")
