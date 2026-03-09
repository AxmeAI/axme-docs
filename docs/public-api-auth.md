# Axme Public API Auth and Reliability

## Authentication Layers

AXME uses a two-layer auth model:

- **Machine credential**: `x-api-key: <AXME_API_KEY>`
  - Required for gateway routes by default.
  - Intended for SDKs, backend integrations, CI/CD, and automation.
  - External value is a workspace/service-account key (`axme_sa_...`) issued by AXME Cloud onboarding.
- **Actor token** (user/session context): `authorization: Bearer <access_token>`
  - Adds user/session context and scoped claims (`org_id`, `workspace_id`, `actor_id`, `roles`).
  - Required on routes that operate in user or enterprise scoped context.

`GATEWAY_API_KEY` and `AUTH_API_KEY` are internal infrastructure credentials and are not customer-facing.

## Route Classes

To reduce ambiguity, public routes are grouped into three auth classes:

- **Machine routes**
  - Require only `x-api-key`.
  - Typical use: service-to-service automation and machine-driven runtime APIs.
- **Machine + actor routes**
  - Require both `x-api-key` and actor token (`authorization: Bearer ...`).
  - Typical use: enterprise/admin operations where platform identity and actor identity are both required.
- **Interactive/session routes**
  - Require actor token only.
  - Typical use: user-session and delegated interactive flows.

## Structured Auth Errors

Auth failures return a structured body:

```json
{
  "error": {
    "code": "missing_platform_api_key",
    "message": "missing platform api key",
    "details": {
      "header": "x-api-key"
    }
  },
  "detail": "missing platform api key"
}
```

`detail` is kept for compatibility. `error.code` is the canonical machine-readable contract.
`missing_platform_api_key` and `invalid_platform_api_key` are backward-compatible error code names for missing/invalid `x-api-key` values (including service-account key usage).

Common auth error codes:

- `missing_platform_api_key`
- `invalid_platform_api_key`
- `missing_actor_token`
- `invalid_actor_token`
- `invalid_actor_scope`
- `rate_limit_exceeded`

## Alpha Bootstrap Key Issuance

For cloud alpha onboarding, AXME Cloud form at `https://cloud.axme.ai/alpha` calls:

- `POST /v1/alpha/bootstrap`

Request body:

- `email` (required)
- `use_case` (required)
- `company` (optional)

Response includes a real bootstrap service-account key:

- `key.token` in format `axme_sa_<service_account_id>_<secret>`
- This value is used by customers as `AXME_API_KEY` and sent as `x-api-key`.

The endpoint is controlled by `GATEWAY_ALLOW_UNCONTROLLED_ACCOUNT_BOOTSTRAP`:

- production default: `false` (fail-closed)
- non-production default: `true`

## Scoped-Only Enterprise Bypass

Actor-token-only access for enterprise routes is now explicit opt-in.

- Flag: `AXME_ALLOW_ENTERPRISE_SCOPED_ONLY_AUTH`
- Default: `false`
- When enabled, selected enterprise routes may accept actor token without `x-api-key`.

Without opt-in, enterprise routes require both:

- `x-api-key`
- `authorization: Bearer <actor_token>`

## Session Auth — Email OTP (Passwordless)

The primary user authentication flow is CLI-native, email-based, and requires no browser or password.

### Login Intent Flow

```
POST /v1/auth/login-intent
  → { intent_id, expires_in: 300, delivery: "email" }

POST /v1/auth/login-intent/{id}/verify
  body: { "code": "123456" }
  → { ok, api_key, account_session_token, refresh_token, org_id, workspace_id }

GET /v1/auth/login-intent/{id}/callback?token=<magic_token>
  → same completion path as verify (magic-link alternative)
```

- `POST /v1/auth/login-intent`: creates a login intent, generates a 6-digit OTP (sha256-hashed), sends email with OTP + magic link. Requires `x-api-key`.
- `POST /v1/auth/login-intent/{id}/verify`: validates OTP, issues `account_session_token` (JWT) + `refresh_token` + `api_key`. OTP is single-use; the intent transitions to `verified` state.
- `GET  /v1/auth/login-intent/{id}/callback`: magic-link alternative to OTP entry — same completion path, uses `secrets.compare_digest` for timing-safe token comparison.

On first login for a new email, the platform automatically provisions:
- An organization (`org_...`)
- A default sandbox workspace (`ws_...`)
- An `email_verified` quota tier (500 intents/day, 20 actors, 10 service accounts)

### Token Model

- `account_session_token`: short-lived Bearer JWT, `exp = iat + 900s` (15 minutes).
- `refresh_token`: opaque, one-time-use with rotation, 30-day TTL.
- Clients (CLI) should proactively refresh when `exp - now < 60s` to avoid reactive 401 round-trips.
- Refresh endpoint: `POST /v1/auth/refresh` — returns new `access_token` + new `refresh_token`.
- Refresh token is rotated on every use; the previous token is invalidated immediately.

### Session Management Endpoints

- `POST /v1/auth/refresh` — exchange `refresh_token` for new `access_token` + `refresh_token`
- `POST /v1/auth/logout` — revoke current session
- `POST /v1/auth/logout-all` — revoke all sessions for the actor
- `GET  /v1/auth/sessions` — list active sessions (requires `x-api-key` + `Authorization: Bearer`)
- `POST /v1/auth/sessions/revoke` — revoke one selected session

### Auth Safety Controls

- Rate-limit on auth endpoints (`AUTH_RATE_LIMIT_PER_MINUTE`).
- OTP expires after 5 minutes (`LOGIN_INTENT_TTL_SECONDS=300`).
- Login intent is single-use: second verify attempt on the same intent returns HTTP `409 Conflict`.
- Auth audit events: `login_success`, `login_failed`, `refresh_success`, `logout`, `logout_all`, `lockout_triggered`.

## Legacy Session Auth (`nick + password`)

Password-based login is supported for backward compatibility and internal tooling:

- `POST /v1/auth/register-password`
- `POST /v1/auth/login`
- `GET  /v1/auth/assistant-links`

Password policy: minimum length 12, argon2id hash, common-password denylist.

## MCP Bearer Handling

- `mcp_server` validates JWT signature and claims (`iss`, `aud`, `exp`, `iat`, `jti`, `sid`, `scope`).
- Validation mode:
  - `AXME_JWKS_URL` set -> JWKS-based verification (supports key rotation).
  - otherwise -> HS256 verification via `AUTH_JWT_SECRET` (dev/local compatibility).
- Optional online session check:
  - `AXME_INTROSPECTION_ENABLED=true` and `AXME_AUTH_SERVICE_URL` set
  - uses `POST /v1/auth/introspect` after local signature validation.
- Owner scope is derived from claim configured by `AXME_OWNER_CLAIM` (default `owner_agent`).

## JWT/JWKS Validation Policy

- Required claims: `sub`, `iss`, `aud`, `exp`, `iat`, `jti`, `sid`.
- Required scope: `AXME_REQUIRED_SCOPE` (default `axme.api`).
- Clock skew tolerance: `AXME_JWT_CLOCK_SKEW_SECONDS` (default `60`).
- `nbf` in the future is rejected (with configured clock skew).
- JWKS cache/fallback:
  - `AXME_JWKS_CACHE_TTL_SECONDS`
  - `AXME_JWKS_STALE_TTL_SECONDS`
  - if JWKS endpoint is unavailable, last-known keys are used only for limited stale TTL; after that validation fails closed.
- Local denylist hooks (for immediate revoke propagation):
  - `AXME_REVOKED_JTI_SET` (comma-separated)
  - `AXME_REVOKED_SID_SET` (comma-separated)
- Error semantics:
  - `401` for invalid/expired/not-active/revoked token
  - `403` for scope mismatch or owner scope mismatch

## Inbox Owner Scope

- Inbox endpoints support owner scoping via:
  - header: `x-owner-agent: agent://...`
  - or query: `?owner_agent=agent://...`
- If both are provided they must match, otherwise HTTP `400`.
- Optional strict mode:
  - env: `GATEWAY_ENFORCE_INBOX_OWNER_SCOPE=true`
  - when enabled, owner scope is required on all inbox endpoints.
- Optional bearer enforcement for owner-scoped inbox routes:
  - env: `GATEWAY_REQUIRE_BEARER_AUTH=true`
  - when enabled, valid bearer is required and owner is derived from JWT claim.
- Access to a thread outside the provided owner scope returns HTTP `403`.

## Production Hardening and Scoped Credential Migration

Production profile defaults and migration controls:

- `AXME_DEPLOYMENT_PROFILE=production` enables fail-closed defaults for:
  - `GATEWAY_REQUIRE_BEARER_AUTH=true`
  - `GATEWAY_ENFORCE_INBOX_OWNER_SCOPE=true`
  - `GATEWAY_ALLOW_UNCONTROLLED_ACCOUNT_BOOTSTRAP=false`
- Scoped credential transition flags:
  - `AXME_FEATURE_SCOPED_CREDENTIALS`
  - `AXME_SCOPED_CREDENTIALS_ALLOW_LEGACY_OWNER`

Detailed rollout phases and compatibility window behavior:

- `docs/enterprise-scoped-credentials-migration-note.md`

## Idempotency (`POST /v1/intents`)

- Header: `idempotency-key: <client-generated-key>`
- Same key + same payload:
  - returns original accepted result (no duplicate workflow)
- Same key + different payload:
  - HTTP `409`
  - body: `{"detail":"idempotency key reused with different payload"}`

## Message Size Limits

- `POST /v1/intents`: text payload fields are validated by UTF-8 byte size.
- Default hard limit: `GATEWAY_MESSAGE_MAX_BYTES=131072` (128 KiB).
- Oversized payload returns HTTP `413`.

## Media Upload Flow

Media binary is stored in object storage; DB keeps metadata only.

- `POST /v1/media/create-upload`
  - creates upload session + object path metadata
  - validates max file size (`GATEWAY_MEDIA_MAX_FILE_BYTES`)
  - returns `upload_url` (signed when `GATEWAY_MEDIA_SIGNED_URL_MODE=gcs_v4`)
- `POST /v1/media/finalize-upload`
  - marks uploaded object as `ready`
  - validates expected size/hash
- `GET /v1/media/{upload_id}`
  - returns metadata and download URL when status is `ready`

Signed URL modes:

- `direct` (default for local/dev): returns direct object URL.
- `gcs_v4`: attempts Google Cloud Storage V4 signed URL generation.
  - optional env for explicit signer identity:
    - `GATEWAY_GCS_SIGNING_SERVICE_ACCOUNT_FILE`
    - `GATEWAY_GCS_SIGNING_SERVICE_ACCOUNT_JSON`

## Rate Limiting

- Gateway default: `120` requests/minute per API key per endpoint (`GATEWAY_RATE_LIMIT_PER_MINUTE`).
- MCP tool-level default: `120` calls/minute per `(owner/tool)` (`AXME_MCP_TOOL_RATE_LIMIT_PER_MINUTE`).
- Response headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
- Exceeded limit:
  - HTTP `429`
  - header `Retry-After`

## Audit Trail

Gateway and auth service record audit events with:

- event id and timestamp
- `request_id` / `trace_id`
- endpoint and method
- action name
- status code
- latency (`latency_ms`)
- hashed API key fingerprint (gateway)
- request-specific details (for example intent id / session id)

Request correlation:

- Incoming `x-request-id` is propagated through `mcp_server -> gateway -> auth_service`.
- If absent, service generates one and returns it in response headers.
