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

## Migration Expectations for Integrators

- Pin to explicit schema/API versions (do not depend on implicit latest behavior).
- Validate request/response payloads against published schemas.
- Track release notes for deprecations and scheduled removals.

## Enforcement

- Contract changes must pass schema validation and contract tests in CI.
- SDK and conformance updates are required for breaking-version adoption.
