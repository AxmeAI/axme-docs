# axme-docs

Public platform documentation and architecture guides for integrators.

## Status

Wave 1 extraction in progress.

## Included in Wave 1

- `docs/public-api-auth.md`
- `docs/connectors/intent-normalization.md`
- docs validation gate (no Cyrillic / non-empty markdown)

## Development

```bash
python -m pip install -e ".[dev]"
python scripts/validate_docs.py
pytest
```
