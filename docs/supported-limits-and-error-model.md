# Supported Limits and Error Model

## Scope

This document defines integration-facing operational limits and canonical HTTP/error behavior for public Axme APIs.

## Supported Limits (Current Defaults)

- API request rate limit (gateway): `120` requests/minute per API key per endpoint.
- MCP tool rate limit: `120` calls/minute per `(owner, tool)` tuple.
- Message payload size (`POST /v1/intents`): `131072` bytes (128 KiB).
- Media file max size (`create-upload` flow): `104857600` bytes (100 MiB).

These defaults may be adjusted by plan or deployment profile; integrators should rely on response headers and documented configuration contracts.

## Rate-Limit Signaling

Responses may include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

When exceeded:

- HTTP `429 Too Many Requests`
- `Retry-After` header

## Error Model

### Authentication and Authorization

- `401 Unauthorized`
  - invalid or missing API key
  - invalid/expired/revoked bearer token
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
