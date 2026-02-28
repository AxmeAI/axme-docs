# Axme Public API Auth and Reliability

## Transport-Level API Key

- Header: `x-api-key: <key>` for gateway and auth service calls.
- Missing or invalid key:
  - HTTP `401`
  - body: `{"detail":"invalid api key"}`

## Session Auth (`nick + password`)

Auth flow endpoints are exposed by gateway and proxied to `auth_service`:

- `POST /v1/auth/register-password`
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `POST /v1/auth/logout-all`
- `GET /v1/auth/sessions`
- `POST /v1/auth/sessions/revoke`
- `GET /v1/auth/assistant-links`

### OAuth Linking Page

- `GET /oauth/authorize` now supports both actions in one form:
  - `Sign in` for existing accounts
  - `Create account` for first-time users (`nick + password`)
- Create-account path writes `gateway_users`, `gateway_nicks`, and `gateway_auth_credentials`
  in the same auth database, then continues the OAuth code flow.
- This removes the dead-end during assistant linking where a new user could not register
  directly from the OAuth screen.

### Login / Token Model

- Login payload: `nick`, `password`, optional `client_type`, `device_label`.
- Password hash algorithm: `argon2id` only.
- Issued on login:
  - short-lived `access_token` (Bearer JWT)
  - long-lived `refresh_token` (opaque, stored server-side as hash)
- Refresh is one-time use with rotation.
- Logout revokes current session and refresh chain.
- Logout-all revokes all active sessions for the user.
- Session revoke endpoint revokes one selected session chain (`/v1/auth/sessions/revoke`).

### Multi-Device Session Visibility

- `GET /v1/auth/sessions` returns all sessions for the current bearer user.
- `GET /v1/auth/assistant-links` returns assistant/client links (`provider`, `device_label`, last seen).
- Both endpoints require:
  - gateway API key (`x-api-key`)
  - bearer access token (`authorization: Bearer ...`)
- Access token claims must include `scope=axme.api`.

### Password Policy v1

- Minimum length: `12`.
- Denylist of common passwords.
- Password cannot contain normalized nick.
- Optional breached-password check can be enabled via:
  - `AUTH_BREACHED_PASSWORD_CHECK_ENABLED=true`
  - `AUTH_BREACHED_PASSWORD_CHECK_URL=<service-url>`

### Auth Safety Controls

- Rate-limit on auth endpoints (`AUTH_RATE_LIMIT_PER_MINUTE`).
- Lockout after repeated failed logins:
  - `AUTH_LOCKOUT_THRESHOLD`
  - `AUTH_LOCKOUT_SECONDS`
- Auth audit events:
  - `login_success`
  - `login_failed`
  - `refresh_success`
  - `logout`
  - `logout_all`
  - `lockout_triggered`

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
