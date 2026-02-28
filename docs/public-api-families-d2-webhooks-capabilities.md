# Public API Families D2: Webhooks and Capabilities

This guide covers the second additive parity batch for family-level integration docs:

- `webhooks.subscriptions`
- `webhooks.events`
- `webhooks.events.replay`
- `capabilities.get`

Use this guide together with:

- `docs/openapi/gateway.v1.json` (canonical endpoint surface)
- `axme-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md` and `docs/supported-limits-and-error-model.md`

## 1) Webhooks Subscriptions Family

### Purpose and context

Webhook subscriptions define how Axme pushes event notifications to external integrators. This family manages subscription upsert, list, and revoke lifecycle.

### Endpoint mapping

- `POST /v1/webhooks/subscriptions`
- `GET /v1/webhooks/subscriptions`
- `DELETE /v1/webhooks/subscriptions/{subscription_id}`

### Canonical schemas

- `axme-spec/schemas/public_api/api.webhooks.subscriptions.upsert.request.v1.json`
- `axme-spec/schemas/public_api/api.webhooks.subscriptions.response.v1.json`
- `axme-spec/schemas/public_api/api.webhooks.subscriptions.list.response.v1.json`
- `axme-spec/schemas/public_api/api.webhooks.subscriptions.delete.response.v1.json`

### Request example (`POST /v1/webhooks/subscriptions`)

```json
{
  "callback_url": "https://integrator.example/webhooks/axme",
  "event_types": ["inbox.thread_created", "inbox.reply_received"],
  "secret": "webhook-signing-secret-2026",
  "active": true,
  "description": "Primary production subscription"
}
```

### Idempotency/retry/trace guidance

- For upsert writes, include `Idempotency-Key` if caller may retry.
- Keep payload byte-identical when replaying the same idempotency key.
- Always propagate `X-Trace-Id` and log it in delivery pipelines.

### Error and edge cases

- `422` for invalid callback URL or unsupported event types.
- `404` on delete for unknown `subscription_id`.
- `409` for conflicting subscription state transitions.

### SDK call mapping

- Python GA:
  - `AxmeClient.upsert_webhook_subscription(...)`
  - `AxmeClient.list_webhook_subscriptions(...)`
  - `AxmeClient.delete_webhook_subscription(...)`
- TypeScript GA:
  - `AxmeClient.upsertWebhookSubscription(...)`
  - `AxmeClient.listWebhookSubscriptions(...)`
  - `AxmeClient.deleteWebhookSubscription(...)`

### Conformance expectation

- Covered by `webhooks_subscriptions` executable contract check in `axme-conformance`.

## 2) Webhooks Events Family

### Purpose and context

Events endpoints ingest outgoing webhook events and expose replay behavior for delivery recovery.

### Endpoint mapping

- `POST /v1/webhooks/events`
- `POST /v1/webhooks/events/{event_id}/replay`

### Canonical schemas

- `axme-spec/schemas/public_api/api.webhooks.events.request.v1.json`
- `axme-spec/schemas/public_api/api.webhooks.events.response.v1.json`
- `axme-spec/schemas/public_api/api.webhooks.events.replay.response.v1.json`

### Request example (`POST /v1/webhooks/events`)

```json
{
  "event_type": "inbox.thread_created",
  "source": "chatgpt",
  "payload": {
    "thread_id": "7d0bcf7e-6d94-4a78-9232-1491db2a545b"
  }
}
```

### Response expectation

- Responses include delivery counters:
  - `queued_deliveries`
  - `processed_deliveries`
  - `delivered`
  - `pending`
  - `dead_lettered`

### Idempotency/retry/trace guidance

- Use `Idempotency-Key` for event publish and replay calls.
- Retry transient failures (`429`, `5xx`) with bounded backoff.
- Preserve `X-Trace-Id` from ingress call into internal delivery telemetry.

### Error and edge cases

- `404` on replay for unknown event IDs.
- `409` on replay when event lifecycle blocks replay in current state.
- `422` on invalid event payload shape.

### SDK call mapping

- Python GA:
  - `AxmeClient.publish_webhook_event(...)`
  - `AxmeClient.replay_webhook_event(...)`
- TypeScript GA:
  - `AxmeClient.publishWebhookEvent(...)`
  - `AxmeClient.replayWebhookEvent(...)`

### Conformance expectation

- Covered by `webhooks_events` executable contract check in `axme-conformance`.

## 3) Capabilities Family

### Purpose and context

Capabilities provide a machine-readable contract for what the runtime currently supports (feature and intent type surface).

### Endpoint mapping

- `GET /v1/capabilities`

### Canonical schema

- `axme-spec/schemas/public_api/api.capabilities.get.response.v1.json`

### Response example (`GET /v1/capabilities`)

```json
{
  "ok": true,
  "capabilities": ["intent.submit", "intent.status.read"],
  "supported_intent_types": ["intent.ask.v1", "intent.reply.v1"]
}
```

### Idempotency/retry/trace guidance

- Read-only endpoint: safe to retry on transport errors and transient server statuses.
- Include `X-Trace-Id` so capability snapshots can be correlated during incident analysis.

### Error and edge cases

- `401`/`403` when caller lacks auth or scope.
- `5xx` on runtime degradation (caller should retry with backoff).

### SDK call mapping

- Python GA: dedicated helper not yet shipped (use direct HTTP path until parity batch closes the gap).
- TypeScript GA: dedicated helper not yet shipped (use direct HTTP path until parity batch closes the gap).
- Beta SDKs (`Go/Java/.NET`): parity pending.

### Conformance expectation

- No dedicated capabilities check yet in `axme-conformance`.
- Track C conformance expansion should add `capabilities.get` shape and non-empty capability list validation.
