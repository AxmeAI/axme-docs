# axme-docs

Public platform documentation and architecture guides for integrators.

## Status

Track B extraction in progress.

## OpenAPI artifacts

Canonical OpenAPI specifications live under `docs/openapi/`:
- `gateway.v1.json`
- `chatgpt-adapter.v1.json`
- `gemini-adapter.v1.json`

## Included through Track B batches

- Core public docs:
  - `docs/public-api-auth.md`
  - `docs/integration-quickstart.md`
  - `docs/migration-and-deprecation-policy.md`
  - `docs/supported-limits-and-error-model.md`
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
