from __future__ import annotations

from pathlib import Path


def validate_markdown_docs(root: Path) -> list[str]:
    errors: list[str] = []
    docs_root = root / "docs"
    for path in sorted(docs_root.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            errors.append(f"{path}: file is empty")
        if any("\u0400" <= ch <= "\u04FF" for ch in content):
            errors.append(f"{path}: contains Cyrillic characters")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_markdown_docs(root)
    if errors:
        print("docs validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("docs validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
