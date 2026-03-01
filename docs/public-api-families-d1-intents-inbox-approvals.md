# Public API Families D1: Intents, Inbox, Approvals

This guide covers the first additive parity batch for family-level integration docs:

- `intents.create`
- `intents.get`
- `intents.events`
- `intents.events.stream`
- `intents.resolve`
- `inbox.list`
- `inbox.thread`
- `inbox.reply`
- `inbox.changes`
- `inbox.decision`
- `inbox.delegate`
- `inbox.messages.delete`
- `approvals.decision`

Use this guide together with:

- `docs/openapi/gateway.v1.json` (canonical endpoint surface)
- `axme-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md` and `docs/supported-limits-and-error-model.md`

## 1) Intents Family

### Purpose and context

Intents are the primary write/read entry for assistant-integrator workflows. Integrators submit normalized intent envelopes and track the accepted intent by ID.

### Endpoint mapping

- `POST /v1/intents` -> create intent
- `GET /v1/intents/{intent_id}` -> read intent
- `GET /v1/intents/{intent_id}/events` -> list lifecycle events
- `GET /v1/intents/{intent_id}/events/stream` -> stream lifecycle events (SSE)
- `POST /v1/intents/{intent_id}/resolve` -> append terminal lifecycle event

### Canonical schemas

- `axme-spec/schemas/public_api/api.intents.create.request.v1.json`
- `axme-spec/schemas/public_api/api.intents.create.response.v1.json`
- `axme-spec/schemas/public_api/api.intents.get.response.v1.json`
- `axme-spec/schemas/public_api/api.intents.events.list.response.v1.json`
- `axme-spec/schemas/public_api/api.intents.resolve.request.v1.json`
- `axme-spec/schemas/public_api/api.intents.resolve.response.v1.json`

### Request example (`POST /v1/intents`)

```json
{
  "intent_type": "intent.ask.v1",
  "correlation_id": "dc08f261-195e-4a38-8de8-4f7755070f91",
  "from_agent": "agent://alice",
  "to_agent": "agent://bob",
  "payload": {
    "question": "Can we sync tomorrow at 10?"
  }
}
```

### Response example (`POST /v1/intents`)

```json
{
  "ok": true,
  "intent_id": "7d0bcf7e-6d94-4a78-9232-1491db2a545b",
  "status": "accepted",
  "created_at": "2026-02-21T11:00:00Z"
}
```

### Idempotency/retry/trace guidance

- Always send `Idempotency-Key` for create retries.
- Reuse the same key only for byte-identical request payloads.
- Send `X-Trace-Id` on each request and propagate it to logs.
- Retry policy: retry only transient transport/`429`/`5xx` failures with backoff.

### Error and edge cases

- `409` on idempotency replay with a mutated payload.
- `400`/`422` on schema or semantic validation failures.
- `401`/`403` for auth failures.
- `429`/`5xx` for throttling or server-side transient issues.

### SDK call mapping

- Python GA: `AxmeClient.create_intent(...)`
- TypeScript GA: `AxmeClient.createIntent(...)`
- Python GA:
  - `AxmeClient.send_intent(...)`
  - `AxmeClient.list_intent_events(...)`
  - `AxmeClient.observe(...)`
  - `AxmeClient.wait_for(...)`
  - `AxmeClient.resolve_intent(...)`
- TypeScript GA:
  - `AxmeClient.sendIntent(...)`
  - `AxmeClient.listIntentEvents(...)`
  - `AxmeClient.observe(...)`
  - `AxmeClient.waitFor(...)`
  - `AxmeClient.resolveIntent(...)`

### Conformance expectation

- Existing executable checks:
  - `intent_create`
  - `intent_create_idempotency`
  - `intents_get`
  - `intents_events`
  - `intents_stream_resume`
  - `intents_resolve`
  - `intent_completion_delivery`

## 2) Inbox Family

### Purpose and context

Inbox endpoints expose owner-scoped threads and allow actioning those threads (reply/delegate/decision/delete) while preserving workflow timeline semantics.

### Endpoint mapping

- `GET /v1/inbox`
- `GET /v1/inbox/{thread_id}`
- `GET /v1/inbox/changes`
- `POST /v1/inbox/{thread_id}/reply`
- `POST /v1/inbox/{thread_id}/delegate`
- `POST /v1/inbox/{thread_id}/approve`
- `POST /v1/inbox/{thread_id}/reject`
- `DELETE /v1/inbox/{thread_id}/messages`

### Canonical schemas

- `axme-spec/schemas/public_api/api.inbox.list.response.v1.json`
- `axme-spec/schemas/public_api/api.inbox.thread.response.v1.json`
- `axme-spec/schemas/public_api/api.inbox.changes.response.v1.json`
- `axme-spec/schemas/public_api/api.inbox.reply.request.v1.json`
- `axme-spec/schemas/public_api/api.inbox.delegate.request.v1.json`
- `axme-spec/schemas/public_api/api.inbox.decision.request.v1.json`
- `axme-spec/schemas/public_api/api.inbox.messages.delete.request.v1.json`
- `axme-spec/schemas/public_api/api.inbox.messages.delete.response.v1.json`

### Request example (`POST /v1/inbox/{thread_id}/reply`)

```json
{
  "message": "Approved, please proceed."
}
```

### Response example (`GET /v1/inbox/changes`)

```json
{
  "ok": true,
  "changes": [
    {
      "cursor": "1700000000000000:7d0bcf7e-6d94-4a78-9232-1491db2a545b",
      "thread": {
        "thread_id": "7d0bcf7e-6d94-4a78-9232-1491db2a545b",
        "intent_id": "7d0bcf7e-6d94-4a78-9232-1491db2a545b",
        "status": "pending",
        "owner_agent": "agent://bob",
        "from_agent": "agent://alice",
        "to_agent": "agent://bob",
        "created_at": "2026-02-21T11:00:00Z",
        "updated_at": "2026-02-21T11:00:00Z",
        "timeline": [
          {
            "event_id": "9fa15366-b768-48c2-b37d-2254b09168b7",
            "event_type": "intent_received",
            "actor": "system",
            "at": "2026-02-21T11:00:00Z",
            "details": {
              "intent_type": "intent.ask.v1"
            }
          }
        ]
      }
    }
  ],
  "next_cursor": "1700000000000000:7d0bcf7e-6d94-4a78-9232-1491db2a545b",
  "has_more": false
}
```

### Idempotency/retry/trace guidance

- Treat read operations (`GET`) as safe retryable operations.
- For actioning writes (`reply`, `delegate`, `approve`, `reject`, `messages.delete`), include `Idempotency-Key` when retries are possible.
- Send `X-Trace-Id` on polling and write calls to correlate workflow transitions.
- For `inbox/changes`, use cursor-based pagination; when `has_more=true`, continue with `next_cursor`.

### Error and edge cases

- `404` on unknown thread ID or owner/thread mismatch.
- `409` on invalid state transition (for example, actioning a terminal thread).
- `422` on invalid request body shape (`message`, `delegate_to`, `mode`, or decision fields).
- `429` and `5xx` should be retried with backoff.

### SDK call mapping

- Python GA:
  - `AxmeClient.list_inbox(...)`
  - `AxmeClient.get_inbox_thread(...)`
  - `AxmeClient.list_inbox_changes(...)`
  - `AxmeClient.reply_inbox_thread(...)`
- TypeScript GA:
  - `AxmeClient.listInbox(...)`
  - `AxmeClient.getInboxThread(...)`
  - `AxmeClient.listInboxChanges(...)`
  - `AxmeClient.replyInboxThread(...)`
- Gap to close in Track C parity:
  - `delegate`, `approve`, `reject`, and `messages.delete` helpers in GA SDKs.

### Conformance expectation

- Existing executable checks:
  - `inbox_list`
  - `inbox_reply`
  - `inbox_changes_pagination`
- Track C expansion should add checks for `inbox.thread`, `inbox.delegate`, `inbox.decision`, and `inbox.messages.delete`.

## 3) Approvals Family

### Purpose and context

Approvals provide explicit workflow decision points for external assistants and owners. This is the canonical endpoint for approval status transitions.

### Endpoint mapping

- `POST /v1/approvals/{approval_id}/decision`

### Canonical schemas

- `axme-spec/schemas/public_api/api.approvals.decision.request.v1.json`
- `axme-spec/schemas/public_api/api.approvals.decision.response.v1.json`

### Request example (`POST /v1/approvals/{approval_id}/decision`)

```json
{
  "decision": "approved",
  "reason": "Meets budget and policy constraints."
}
```

### Response example (`POST /v1/approvals/{approval_id}/decision`)

```json
{
  "ok": true,
  "approval_id": "7d0bcf7e-6d94-4a78-9232-1491db2a545b",
  "status": "approved",
  "decided_at": "2026-02-24T10:00:00Z"
}
```

### Idempotency/retry/trace guidance

- Use `Idempotency-Key` on approval decision writes.
- Keep decision payload stable across retries for the same key.
- Propagate `X-Trace-Id` to tie approval changes back to the originating workflow.

### Error and edge cases

- `404` if approval does not exist for the scoped owner.
- `409` if a terminal approval is already decided and cannot be re-decided.
- `422` when `decision` is invalid for the contract.

### SDK call mapping

- Python GA: `AxmeClient.decide_approval(...)`
- TypeScript GA: `AxmeClient.decideApproval(...)`
- Beta SDKs (`Go/Java/.NET`): parity pending.

### Conformance expectation

- Executable check: `approvals_decision`.
