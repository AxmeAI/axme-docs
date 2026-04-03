# Integration Quickstart

## CLI-first quickstart

The fastest way to see AXME in action is the CLI. Install with one command, log in with email OTP, and run a built-in example end-to-end: `axme examples run human/cli`. See the full CLI guide at [cloud.axme.ai/alpha/cli](https://cloud.axme.ai/alpha/cli).

## Goal

Build a minimal integration using public repositories only.

Canonical model for this guide:

- `AXP` is the Intent Protocol (durable execution layer).
- Integrations should use intent lifecycle semantics, not RPC-style remote calls.

## Inputs

- API contracts/schemas: `axp-spec`
- public integration docs: `axme-docs`
- SDK baseline repos: `axme-sdk-python`, `axme-sdk-typescript`
- example hub: `axme-examples` (cloud + protocol tracks)

## Step 1: Review Public Contracts

- `axp-spec/docs/public-api-schema-index.md`
- `axp-spec/docs/schema-versioning-rules.md`
- `axp-spec/docs/protocol-error-status-model.md`
- `axp-spec/docs/idempotency-correlation-rules.md`
- `docs/public-api-families-d1-intents-inbox-approvals.md`
- `docs/public-api-families-d2-webhooks-capabilities.md`
- `docs/public-api-families-d3-users.md`
- `docs/public-api-families-d4-invites-media.md`
- `docs/public-api-families-d5-schemas.md`
- `docs/axme-is-not-rpc.md`
- `docs/mcp-axme-continuation-pattern.md`
- `docs/migration-message-centric-to-intent-lifecycle.md`

## Step 2: Pick Integration Surface

- Direct HTTP integration using public API/OpenAPI contracts:
  - `docs/openapi/gateway.v1.json`
- Connector-specific contracts (if needed):
  - `docs/openapi/chatgpt-adapter.v1.json`
  - `docs/openapi/gemini-adapter.v1.json`

Pick example family:

- Cloud runtime scenarios: `axme-examples/cloud`
- AXP-only protocol scenarios: `axme-examples/protocol`

## Step 3: Implement Minimal Flow

Recommended baseline:

1. Submit intent (`POST /v1/intents`) with optional deadline:
   - `ttl_seconds: 3600` -- relative TTL (60s to 7 days)
   - `deadline_at: "2026-04-04T18:00:00Z"` -- absolute deadline
   - If neither is set, the server may apply a default TTL (configurable via `AXME_DEFAULT_INTENT_TTL_SECONDS`).
2. Observe continuation (primary stream):
   - `GET /v1/intents/{intent_id}/events/stream`
3. Keep polling fallback:
   - `GET /v1/intents/{intent_id}`
   - `GET /v1/intents/{intent_id}/events?since=<seq>`
4. Enable offline completion when needed:
   - set `reply_to` in `POST /v1/intents`
   - consume completion from `GET /v1/inbox?owner_agent=<reply_to>`
5. Reply/delegate/decision on inbox thread as needed
6. Handle `TIMED_OUT` as a terminal state -- intents that exceed their deadline are automatically closed by the gateway

## Step 4: Apply Auth, Limits, and Error Handling

- `docs/public-api-auth.md`
- `docs/supported-limits-and-error-model.md`
- `docs/migration-and-deprecation-policy.md`

## Step 5: Validate with Contract Discipline

- Validate payloads against `axp-spec/schemas/public_api/*.json`
- Use idempotency keys on retryable writes
- Capture request/trace identifiers in logs

## Protocol Reference

AXP wraps every intent in a signed envelope carrying the payload, sender identity, schema version, idempotency key, and a gateway-applied HMAC signature:

![AXP Protocol Envelope](diagrams/protocol/01-protocol-envelope.svg)

Idempotency and replay protection are first-class protocol features - duplicate requests bearing the same idempotency key return the cached response without re-executing:

![Idempotency and Replay Protection](diagrams/protocol/03-idempotency-and-replay-protection.svg)

## Outcome

If these steps pass in staging, external integrator onboarding is possible from public repositories without private context.
