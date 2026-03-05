# Axme Visualization Program

This directory is the temporary single source of truth for architecture and protocol diagrams.

## Current storage policy

- Keep all diagram sources in `axme-docs/docs/diagrams/**` during active design.
- Use Mermaid source-first (`.mmd`) for easy reviews and batch export to SVG/PNG.
- Move or mirror finalized diagrams into individual repositories during README pass.

## Domain packs

- `intents/` - lifecycle, controls/policy, scheduler, access, audit.
- `platform/` - system context and runtime containers.
- `api/` - method families and error/retry model.
- `protocol/` - envelope, versioning, idempotency/replay handling.
- `security/` - trust boundaries, authz, crypto/key lifecycle.
- `operations/` - release/rollback, backup/restore, observability.
- `website/` - interactive web assets and visual explainers.

## Governance

- Keep one diagram focused on one question.
- Include at least one happy path and two failure branches for critical flows.
- Align names with OpenAPI and runtime behavior before promotion to README/site.

## Next step

Track execution in `VISUALIZATION_BACKLOG.md` and distribute finalized diagrams by repository using `REPO_DISTRIBUTION_PLAN.md`.
