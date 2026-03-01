# Integration Quickstart

## Goal

Build a minimal integration using public repositories only.

Canonical model for this guide:

- `AXP` is the Intent Protocol (durable execution layer).
- Integrations should use intent lifecycle semantics, not RPC-style remote calls.

## Inputs

- API contracts/schemas: `axme-spec`
- public integration docs: `axme-docs`
- SDK baseline repos: `axme-sdk-python`, `axme-sdk-typescript`

## Step 1: Review Public Contracts

- `axme-spec/docs/public-api-schema-index.md`
- `axme-spec/docs/schema-versioning-rules.md`
- `axme-spec/docs/protocol-error-status-model.md`
- `axme-spec/docs/idempotency-correlation-rules.md`
- `docs/public-api-families-d1-intents-inbox-approvals.md`
- `docs/public-api-families-d2-webhooks-capabilities.md`
- `docs/public-api-families-d3-users.md`
- `docs/public-api-families-d4-invites-media.md`
- `docs/public-api-families-d5-schemas.md`

## Step 2: Pick Integration Surface

- Direct HTTP integration using public API/OpenAPI contracts:
  - `docs/openapi/gateway.v1.json`
- Connector-specific contracts (if needed):
  - `docs/openapi/chatgpt-adapter.v1.json`
  - `docs/openapi/gemini-adapter.v1.json`

## Step 3: Implement Minimal Flow

Recommended baseline:

1. Submit intent (`POST /v1/intents`)
2. Poll/get intent status (`GET /v1/intents/{intent_id}`)
3. Read inbox (`GET /v1/inbox`)
4. Reply/delegate/decision on inbox thread as needed

## Step 4: Apply Auth, Limits, and Error Handling

- `docs/public-api-auth.md`
- `docs/supported-limits-and-error-model.md`
- `docs/migration-and-deprecation-policy.md`

## Step 5: Validate with Contract Discipline

- Validate payloads against `axme-spec/schemas/public_api/*.json`
- Use idempotency keys on retryable writes
- Capture request/trace identifiers in logs

## Outcome

If these steps pass in staging, external integrator onboarding is possible from public repositories without private context.
