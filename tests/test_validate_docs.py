from __future__ import annotations

from pathlib import Path

from scripts.validate_docs import validate_markdown_docs


def test_docs_validate_clean() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = validate_markdown_docs(root)
    assert errors == []
