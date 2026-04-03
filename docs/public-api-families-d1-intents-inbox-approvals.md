# Public API Families D1: Intents, Inbox, Approvals

This guide covers the first additive parity batch for family-level integration docs:

- `intents.create`
- `intents.get`
- `intents.events`
- `intents.events.stream`
- `intents.resolve`
- `intents.resume`
- `intents.controls`
- `intents.policy`
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
- `axp-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md` and `docs/supported-limits-and-error-model.md`
- `docs/diagrams/README.md` (diagram program index)
- `docs/diagrams/intents/index.md` (intent-focused diagram pack)

## 1) Intents Family

### Purpose and context

Intents are the primary write/read entry for assistant-integrator workflows. Integrators submit normalized intent envelopes and track canonical lifecycle status by intent ID.

### Endpoint mapping

- `POST /v1/intents` -> create intent
- `GET /v1/intents/{intent_id}` -> read intent
- `GET /v1/intents/{intent_id}/events` -> list lifecycle events
- `GET /v1/intents/{intent_id}/events/stream` -> stream lifecycle events (SSE)
- `POST /v1/intents/{intent_id}/resolve` -> append terminal lifecycle event
- `POST /v1/intents/{intent_id}/resume` -> resume a blocked/waiting workflow step with control CAS
- `POST /v1/intents/{intent_id}/controls` -> patch workflow control parameters (`controls_patch`)
- `POST /v1/intents/{intent_id}/policy` -> patch delegated grants and envelope policy (`grants_patch`, `envelope_patch`)
- `POST /v1/intents/bulk-cancel` -> batch cancel stale/zombie intents by filter

### Continuation semantics (v1)

- Stream transport for `/events/stream` is `text/event-stream` (SSE).
- Polling (`/events?since=`) and streaming are both expected to surface newly synced lifecycle progress without requiring a side-effect `GET /v1/intents/{intent_id}` call first.
- `intent.waiting` events carry `waiting_reason` with one of:
  - `WAITING_FOR_HUMAN`
  - `WAITING_FOR_TOOL`
  - `WAITING_FOR_TIME`
  - `WAITING_FOR_AGENT`

### Canonical schemas

- `axp-spec/schemas/public_api/api.intents.create.request.v1.json`
- `axp-spec/schemas/public_api/api.intents.create.response.v1.json`
- `axp-spec/schemas/public_api/api.intents.get.response.v1.json`
- `axp-spec/schemas/public_api/api.intents.events.list.response.v1.json`
- `axp-spec/schemas/public_api/api.intents.resolve.request.v1.json`
- `axp-spec/schemas/public_api/api.intents.resolve.response.v1.json`
- OpenAPI request/response components for:
  - `POST /v1/intents/{intent_id}/resume`
  - `POST /v1/intents/{intent_id}/controls`
  - `POST /v1/intents/{intent_id}/policy`

### Agent addressing

Intent routing uses `agent://` addresses for both sender and recipient identification:

- **`from_agent`** — auto-derived from the caller's service account API key. The gateway resolves the API key to its associated service account and fills in the corresponding `agent://` address server-side. Any client-supplied value is overwritten. See [agent-addressing.md](agent-addressing.md) for the full specification.

- **`to_agent`** — must be a valid `agent://` URI referencing a registered agent in the agent registry. The gateway validates this field on intent submission:
  - If the URI format is malformed, the gateway returns `422` with error code `invalid_agent_address`.
  - If the URI is well-formed but does not match a registered agent, the gateway returns `404` with error code `agent_not_found`.

To look up agent details before sending an intent, use `GET /v1/agents/{address}` (see [public-api-families-d6-enterprise-governance.md](public-api-families-d6-enterprise-governance.md)).

### Deadline and TTL

Intents support optional deadline enforcement. If an intent is not resolved before its deadline, the gateway automatically transitions it to `TIMED_OUT`.

- **`deadline_at`** (optional, ISO 8601) -- absolute point in time when the intent expires.
- **`ttl_seconds`** (optional, integer, 60-604800) -- relative TTL in seconds from creation time. Converted to `deadline_at` server-side. Mutually exclusive with `deadline_at` (422 if both provided).

If neither is set and the server has `AXME_DEFAULT_INTENT_TTL_SECONDS` configured, the server applies a default deadline automatically.

When an intent times out:
- Status transitions to `TIMED_OUT` (terminal).
- A `intent.timed_out` webhook event is emitted.
- Any pending reminders and scheduled jobs are canceled.

### Request example (`POST /v1/intents`)

Minimal:

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

With relative TTL (expires in 1 hour):

```json
{
  "intent_type": "intent.task.v1",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "from_agent": "agent://alice",
  "to_agent": "agent://bob",
  "ttl_seconds": 3600,
  "payload": {
    "task": "Review PR #42"
  }
}
```

With absolute deadline:

```json
{
  "intent_type": "intent.approval.v1",
  "correlation_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "from_agent": "agent://alice",
  "to_agent": "agent://bob",
  "deadline_at": "2026-04-04T18:00:00Z",
  "payload": {
    "approval": "Budget sign-off"
  }
}
```

### Response example (`POST /v1/intents`)

```json
{
  "ok": true,
  "intent_id": "7d0bcf7e-6d94-4a78-9232-1491db2a545b",
  "status": "DELIVERED",
  "created_at": "2026-02-21T11:00:00Z"
}
```

### Idempotency/retry/trace guidance

- Always send `Idempotency-Key` for create retries.
- Reuse the same key only for byte-identical request payloads.
- Send `X-Trace-Id` on each request and propagate it to logs.
- Retry policy: retry only transient transport/`429`/`5xx` failures with backoff.

### Error and edge cases

- `404` with `agent_not_found` when `to_agent` references an unregistered agent address.
- `422` with `invalid_agent_address` when `to_agent` URI format is malformed.
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
  - `AxmeClient.resume_intent(...)`
  - `AxmeClient.update_intent_controls(...)`
  - `AxmeClient.update_intent_policy(...)`
- TypeScript GA:
  - `AxmeClient.sendIntent(...)`
  - `AxmeClient.listIntentEvents(...)`
  - `AxmeClient.observe(...)`
  - `AxmeClient.waitFor(...)`
  - `AxmeClient.resolveIntent(...)`
  - `AxmeClient.resumeIntent(...)`
  - `AxmeClient.updateIntentControls(...)`
  - `AxmeClient.updateIntentPolicy(...)`

### Bulk cancel (`POST /v1/intents/bulk-cancel`)

Cancel multiple non-terminal intents matching filter criteria. Useful for cleaning up stale or zombie intents.

```json
{
  "older_than_hours": 24,
  "status_filter": ["IN_PROGRESS", "WAITING", "DELIVERED"],
  "dry_run": true,
  "reason": "cleanup stale intents",
  "limit": 500
}
```

- `older_than_hours` (float, min 0.1, default 24) -- only cancel intents with no activity for this long.
- `status_filter` (list of strings, default: DELIVERED, WAITING, IN_PROGRESS, SUBMITTED) -- which non-terminal statuses to target.
- `dry_run` (bool, default true) -- preview mode. Returns `would_cancel` count without acting.
- `reason` (string) -- recorded in the lifecycle event audit trail.
- `limit` (int, 1-5000, default 500) -- max intents to process.

Dry-run response:

```json
{
  "ok": true,
  "dry_run": true,
  "would_cancel": 12,
  "intent_ids": ["...", "..."]
}
```

Execute response:

```json
{
  "ok": true,
  "dry_run": false,
  "canceled": 12,
  "intent_ids": ["...", "..."]
}
```

### Conformance expectation

- Existing executable checks:
  - `intent_create`
  - `intent_create_idempotency`
  - `intents_get`
  - `intents_events`
  - `intents_stream_resume`
  - `intents_continuation_autonomy`
  - `intents_resolve`
  - `intents_resume_control`
  - `intents_controls_policy`
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
- `POST /v1/inbox/{thread_id}/messages/delete`

### Canonical schemas

- `axp-spec/schemas/public_api/api.inbox.list.response.v1.json`
- `axp-spec/schemas/public_api/api.inbox.thread.response.v1.json`
- `axp-spec/schemas/public_api/api.inbox.changes.response.v1.json`
- `axp-spec/schemas/public_api/api.inbox.reply.request.v1.json`
- `axp-spec/schemas/public_api/api.inbox.delegate.request.v1.json`
- `axp-spec/schemas/public_api/api.inbox.decision.request.v1.json`
- `axp-spec/schemas/public_api/api.inbox.messages.delete.request.v1.json`
- `axp-spec/schemas/public_api/api.inbox.messages.delete.response.v1.json`

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
- Executable checks include `inbox.thread`, `inbox.delegate`, `inbox.decision`, and `inbox.messages.delete` (already in conformance suite).

## 3) Approvals Family

### Purpose and context

Approvals provide explicit workflow decision points for external assistants and owners. This is the canonical endpoint for approval status transitions.

### Endpoint mapping

- `POST /v1/approvals/{approval_id}/decision`

### Canonical schemas

- `axp-spec/schemas/public_api/api.approvals.decision.request.v1.json`
- `axp-spec/schemas/public_api/api.approvals.decision.response.v1.json`

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

---

## Intent Lifecycle State Machine

Every intent progresses through a well-defined state machine: all states, transitions, and terminal outcomes.

![Intent Lifecycle State Machine](diagrams/intents/01-intent-lifecycle-state-machine.svg)

Key states: `PENDING -> PROCESSING -> WAITING_* -> DELIVERED -> RESOLVED`. Any intent can be cancelled or expire at most transition points. Retry loops are bounded by the policy envelope.
