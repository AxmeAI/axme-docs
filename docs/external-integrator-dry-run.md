# External Integrator Dry-Run Checklist

## Purpose

Provide a repeatable public-only verification that a third-party integrator can implement a minimal Axme integration without private repository context.

## Required Public Inputs

- `axme-spec/docs/public-api-schema-index.md`
- `axme-spec/docs/schema-versioning-rules.md`
- `axme-spec/docs/protocol-error-status-model.md`
- `axme-spec/docs/idempotency-correlation-rules.md`
- `axme-docs/docs/public-api-auth.md`
- `axme-docs/docs/supported-limits-and-error-model.md`
- `axme-docs/docs/migration-and-deprecation-policy.md`
- `axme-docs/docs/openapi/gateway.v1.json`
- `axme-docs/docs/integration-quickstart.md`
- `axme-docs/docs/axme-is-not-rpc.md`
- `axme-docs/docs/mcp-axme-continuation-pattern.md`
- `axme-docs/docs/migration-message-centric-to-intent-lifecycle.md`

## Dry-Run Steps

1. Identify required auth headers and token/key semantics from `public-api-auth.md`.
2. Generate client request models from OpenAPI and/or JSON schemas.
3. Implement minimal API flow:
   - `POST /v1/intents`
   - `GET /v1/intents/{intent_id}/events/stream`
   - `GET /v1/intents/{intent_id}/events?since=<seq>`
   - `GET /v1/intents/{intent_id}`
   - `GET /v1/inbox`
4. Add retry/idempotency behavior for retryable write paths.
5. Implement error handling for `401`, `403`, `409`, `413`, `422`, `429`, and transient `5xx`.
6. Enforce version pinning and migration posture from the deprecation policy.

## Acceptance Criteria

- Integrator can complete minimal flow implementation using only public repositories.
- Request/response payloads validate against published public API schemas.
- Error handling and rate-limit handling behavior are explicitly implemented.
- No private repository files are required to understand contracts or baseline integration behavior.

## Evidence Capture Template

For each dry-run execution, capture:

- date and commit SHAs of `axme-spec` and `axme-docs`,
- implemented endpoints and payload contracts,
- validation result summary,
- observed issues/gaps and linked follow-up items (if any).
