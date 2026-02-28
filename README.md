# axme-docs

Public platform documentation and architecture guides for integrators.

## Status

Wave 2 extraction in progress.

## Included through Wave 2

- Core public docs:
  - `docs/public-api-auth.md`
  - `docs/MVP_SCOPE.md`
  - `docs/B2B_FEATURES.md`
  - `docs/ADR-002-service-boundaries.md`
- Connector and integration docs:
  - `docs/connectors/intent-normalization.md`
  - `docs/connectors/mcp-chatgpt-setup.md`
  - `docs/connectors/mcp-gemini-setup.md`
  - `docs/connectors/mcp-claude-setup.md`
  - `docs/connectors/mcp-siri-bridge-setup.md`
  - `docs/connectors/mcp-android-bridge-setup.md`
- Docs validation gate (no Cyrillic / non-empty markdown)

## Development

```bash
python -m pip install -e ".[dev]"
python scripts/validate_docs.py
pytest
```
