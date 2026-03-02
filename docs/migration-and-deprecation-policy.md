# Migration and Deprecation Policy

## Scope

This policy defines how Axme evolves public contracts and integration behavior across:

- `axme-spec` schemas (`schemas/protocol`, `schemas/public_api`)
- public API/OpenAPI artifacts
- documented integration flows in `axme-docs`

## Versioning Rules

- Breaking changes require a new major schema/API version.
- Backward-compatible additions (optional fields, additive enums where safe) stay within the same major.
- Existing released major versions are immutable in semantics.

Reference:

- `axme-spec/docs/schema-versioning-rules.md`

## Deprecation Lifecycle

1. **Announce**
   - Mark affected endpoint/schema/docs as deprecated in public docs and changelog.
   - Provide target replacement and migration steps.
2. **Overlap window**
   - Keep deprecated and replacement versions available together.
   - Collect compatibility feedback from SDKs and conformance checks.
3. **Sunset**
   - Remove deprecated version only after announced sunset date.
   - Publish final removal notice and version map.

## Compatibility Commitments

- Stable clients pinned to a supported major must continue to work through the overlap window.
- Deprecation notices include:
  - affected contract(s),
  - replacement contract(s),
  - earliest removal date,
  - required client-side actions.

## Intent `legacy_status` Deprecation Schedule

`legacy_status` on intent projections exists only as a migration bridge from legacy status values (`accepted|running|blocked|done|failed`) to canonical lifecycle status values.

Timeline:

1. **Phase A (current through 2026-06-30): dual projection**
   - `intent.status` is canonical and required for client logic.
   - `intent.legacy_status` remains enabled by default for compatibility.
2. **Phase B (from 2026-07-01): explicit opt-out**
   - Integrators should validate clients with `GATEWAY_INCLUDE_LEGACY_INTENT_STATUS=false`.
   - New integrations should ignore `legacy_status` and rely only on canonical lifecycle fields.
3. **Phase C (next major after overlap, earliest 2026-10-01): removal**
   - `legacy_status` is removed from public payloads in the next major API version.
   - SDKs and conformance contracts treat canonical `status` as the only supported lifecycle projection.

## Migration Expectations for Integrators

- Pin to explicit schema/API versions (do not depend on implicit latest behavior).
- Validate request/response payloads against published schemas.
- Track release notes for deprecations and scheduled removals.
- For enterprise auth migration details (shared key to scoped credentials), follow:
  - `docs/enterprise-scoped-credentials-migration-note.md`

## Enforcement

- Contract changes must pass schema validation and contract tests in CI.
- SDK and conformance updates are required for breaking-version adoption.
