# Supported Limits and Error Model

## Scope

This document defines integration-facing operational limits and canonical HTTP/error behavior for public Axme APIs.

## Supported Limits (Current Defaults)

### Per-Request Limits

- API request rate limit (gateway): `180` requests/minute per API key.
- MCP tool rate limit: `120` calls/minute per `(owner, tool)` tuple.
- Message payload size (`POST /v1/intents`): `131072` bytes (128 KiB).
- Media file max size (`create-upload` flow): `104857600` bytes (100 MiB).

### Workspace Quota Dimensions

Workspace quotas are enforced server-side per `(org_id, workspace_id)`. The authoritative source is the `quota_counters` table — atomic, persistent, dialect-aware (PostgreSQL in production).

| Dimension | Default limit | Window | Type |
|---|---|---|---|
| `intents_per_day` | 500 | Calendar day UTC | Rate (counter resets daily) |
| `inbox_writes_per_day` | 200 | Calendar day UTC | Rate (counter resets daily) |
| `actors_total` | 20 | — | Gauge (live count) |
| `service_accounts_per_workspace` | 10 | — | Gauge (live count) |

To view current usage: `axme quota show`

To request higher limits: `axme quota upgrade-request --company "..." --justification "..."`

## Quota Enforcement and 429 Response

When a workspace quota is exceeded, the gateway returns `HTTP 429` with a structured body:

```json
{
  "error": {
    "code": "quota_exceeded",
    "message": "quota exceeded for intents_per_day",
    "details": {
      "dimension": "intents_per_day",
      "used": 501,
      "limit": 500,
      "reset_at": "2026-03-11T00:00:00Z"
    }
  },
  "detail": "quota exceeded for intents_per_day"
}
```

The CLI surfaces this as a human-readable message:

```
Quota exceeded: intents per day (used 501 of 500). Resets at 2026-03-11T00:00:00Z.
Run `axme quota show` to check your limits, or `axme quota upgrade-request` to request higher limits.
```

## Error Model

### Authentication and Authorization

- `401 Unauthorized`
  - invalid or missing API key
  - invalid/expired/revoked actor token
- `403 Forbidden`
  - valid identity but insufficient scope/owner permission

### Request and Contract Errors

- `400 Bad Request`
  - malformed/mutually conflicting parameters
- `409 Conflict`
  - idempotency-key reuse with different payload
- `413 Payload Too Large`
  - payload exceeds message/media limits
- `422 Unprocessable Entity`
  - schema/model validation failure

### Server-Side Errors

- `5xx`
  - unexpected platform/runtime failure
  - clients should retry only where operation is idempotent/safe

## Protocol Error Payload Guidance

For workflow-level status/error semantics, see canonical spec docs:

- `axme-spec/docs/protocol-error-status-model.md`
- `axme-spec/docs/idempotency-correlation-rules.md`

## Integrator Recommendations

- Always send idempotency keys for write operations that may be retried.
- Implement bounded retries with backoff for `429` and transient `5xx`.
- Log and propagate `request_id`/`trace_id` for incident diagnostics.
