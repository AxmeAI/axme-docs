# Public API Families D5: Schemas

This guide covers the fifth additive parity batch for family-level integration docs:

- `schemas.upsert`
- `schemas.get`

Use this guide together with:

- `docs/openapi/gateway.v1.json` (canonical endpoint surface)
- `axme-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md` and `docs/supported-limits-and-error-model.md`

## 1) Schemas Family

### Purpose and context

Schemas endpoints manage semantic contract registry entries used by message envelope validation and schema-aware tooling. Integrators upsert schema metadata/payload for a semantic type and retrieve active schema definitions for runtime validation and inspection.

### Endpoint mapping

- `POST /v1/schemas`
- `GET /v1/schemas/{semantic_type}`

### Canonical schemas

- `axme-spec/schemas/public_api/api.schemas.upsert.request.v1.json`
- `axme-spec/schemas/public_api/api.schemas.upsert.response.v1.json`
- `axme-spec/schemas/public_api/api.schemas.get.response.v1.json`

### Request example (`POST /v1/schemas`)

```json
{
  "semantic_type": "workflow.approval.request.v1",
  "schema_json": {
    "type": "object",
    "additionalProperties": false,
    "required": ["request_id", "title"],
    "properties": {
      "request_id": {
        "type": "string",
        "minLength": 1,
        "maxLength": 128
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 255
      }
    }
  },
  "compatibility_mode": "backward",
  "scope": "tenant",
  "active": true
}
```

### Response example (`GET /v1/schemas/{semantic_type}`)

```json
{
  "ok": true,
  "schema": {
    "semantic_type": "workflow.approval.request.v1",
    "schema_ref": "registry://agent://example/owner/workflow.approval.request.v1@f3f08b08f7a3",
    "schema_hash": "f3f08b08f7a35a4fd3570a45123ecf4f8de962fce8fbb7f4581ec7c5b4a68dd7",
    "compatibility_mode": "backward",
    "scope": "tenant",
    "owner_agent": "agent://example/owner",
    "active": true,
    "schema_json": {
      "type": "object",
      "additionalProperties": false,
      "required": ["request_id", "title"],
      "properties": {
        "request_id": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "title": {
          "type": "string",
          "minLength": 1,
          "maxLength": 255
        }
      }
    },
    "created_at": "2026-03-01T10:00:00Z",
    "updated_at": "2026-03-01T10:00:00Z"
  }
}
```

### Idempotency/retry/trace guidance

- `POST /v1/schemas` is an upsert keyed by `(semantic_type, owner_scope)` and can be safely retried with identical payload.
- Keep `schema_json` stable across retries to preserve deterministic `schema_hash` and avoid accidental schema drift.
- `GET /v1/schemas/{semantic_type}` is a safe retryable read.
- Include `X-Trace-Id` on upsert/get calls for schema governance audit correlation.

### Error and edge cases

- `400` when owner scope is missing for tenant upsert or when `schema_json` is not a valid JSON Schema document.
- `403` when upsert tries to write `scope=core` via tenant endpoint.
- `404` when requested `semantic_type` is not found among active tenant/core records.
- `422` for malformed body fields (invalid `semantic_type` pattern, unsupported enum values, type mismatches).
- `401`/`403` for auth and owner-scope policy failures.

### SDK call mapping

- Python GA:
  - `AxmeClient.upsert_schema(...)`
  - `AxmeClient.get_schema(...)`
- TypeScript GA:
  - `AxmeClient.upsertSchema(...)`
  - `AxmeClient.getSchema(...)`
- Beta SDKs (`Go/Java/.NET`):
  - kickoff baseline currently covers `users.*`; schema helpers are pending later beta expansion.

### Conformance expectation

- Covered by executable checks in `axme-conformance`:
  - `schemas_upsert`
  - `schemas_get`
