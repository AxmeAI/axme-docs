# Public API Families D3: Users

This guide covers the third additive parity batch for family-level integration docs:

- `users.check_nick`
- `users.register_nick`
- `users.rename_nick`
- `users.profile.get`
- `users.profile.update`

Use this guide together with:

- `docs/openapi/gateway.v1.json` (canonical endpoint surface)
- `axme-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md` and `docs/supported-limits-and-error-model.md`

## 1) Nick Registration and Availability Family

### Purpose and context

These endpoints handle the public identity lifecycle for end users: availability check, first registration, and rename updates. Integrators typically call availability first, then register, and use rename for controlled profile changes.

### Endpoint mapping

- `GET /v1/users/check-nick`
- `POST /v1/users/register-nick`
- `POST /v1/users/rename-nick`

### Canonical schemas

- `axme-spec/schemas/public_api/api.users.check_nick.response.v1.json`
- `axme-spec/schemas/public_api/api.users.register_nick.request.v1.json`
- `axme-spec/schemas/public_api/api.users.register_nick.response.v1.json`
- `axme-spec/schemas/public_api/api.users.rename_nick.request.v1.json`
- `axme-spec/schemas/public_api/api.users.rename_nick.response.v1.json`

### Request example (`POST /v1/users/register-nick`)

```json
{
  "nick": "@partner.user",
  "display_name": "Partner User",
  "phone": "+12025550100",
  "email": "partner.user@example.com"
}
```

### Response example (`GET /v1/users/check-nick`)

```json
{
  "ok": true,
  "nick": "@partner.user",
  "normalized_nick": "partner.user",
  "public_address": "partner.user@ax",
  "available": true
}
```

### Idempotency/retry/trace guidance

- Treat `check-nick` as a safe retryable read.
- Send `Idempotency-Key` on `register-nick` and `rename-nick` when retries are possible.
- Reuse the same idempotency key only with byte-identical payloads.
- Send `X-Trace-Id` on read and write calls for identity audit correlation.

### Error and edge cases

- `409` when target nick is already registered by another owner.
- `404` when rename references unknown `owner_agent`.
- `422` for invalid nick shape or malformed body fields.
- `401`/`403` for missing auth or scope violations.

### SDK call mapping

- Python GA:
  - `AxmeClient.check_nick(...)`
  - `AxmeClient.register_nick(...)`
  - `AxmeClient.rename_nick(...)`
- TypeScript GA:
  - `AxmeClient.checkNick(...)`
  - `AxmeClient.registerNick(...)`
  - `AxmeClient.renameNick(...)`
- Beta kickoff:
  - Go: `Client.CheckNick(...)`, `Client.RegisterNick(...)`, `Client.RenameNick(...)`
  - Java: `AxmeClient.checkNick(...)`, `AxmeClient.registerNick(...)`, `AxmeClient.renameNick(...)`
  - .NET: `AxmeClient.CheckNickAsync(...)`, `AxmeClient.RegisterNickAsync(...)`, `AxmeClient.RenameNickAsync(...)`

### Conformance expectation

- Covered by executable checks in `axme-conformance`:
  - `users_check_nick`
  - `users_register_nick`
  - `users_rename_nick`

## 2) User Profile Family

### Purpose and context

Profile endpoints return and update canonical user profile fields attached to `owner_agent`. They are the source of truth for display metadata exposed to integrators.

### Endpoint mapping

- `GET /v1/users/profile`
- `POST /v1/users/profile/update`

### Canonical schemas

- `axme-spec/schemas/public_api/api.users.profile.get.response.v1.json`
- `axme-spec/schemas/public_api/api.users.profile.update.request.v1.json`
- `axme-spec/schemas/public_api/api.users.profile.update.response.v1.json`

### Request example (`POST /v1/users/profile/update`)

```json
{
  "owner_agent": "agent://user/11111111-1111-4111-8111-111111111111",
  "display_name": "Partner User Updated",
  "phone": "+12025550101",
  "email": "partner.updated@example.com"
}
```

### Response example (`GET /v1/users/profile`)

```json
{
  "ok": true,
  "user_id": "11111111-1111-4111-8111-111111111111",
  "owner_agent": "agent://user/11111111-1111-4111-8111-111111111111",
  "nick": "@partner.user",
  "normalized_nick": "partner.user",
  "public_address": "partner.user@ax",
  "display_name": "Partner User",
  "phone": "+12025550100",
  "email": "partner.user@example.com",
  "updated_at": "2026-03-01T10:00:00Z"
}
```

### Idempotency/retry/trace guidance

- Treat profile reads (`GET`) as safe retryable operations.
- Send `Idempotency-Key` on profile updates when caller retry is possible.
- Keep update payload stable across idempotent retries.
- Propagate `X-Trace-Id` for profile update audit traces.

### Error and edge cases

- `404` when `owner_agent` profile does not exist.
- `409` when profile update collides with nick uniqueness constraints.
- `422` when field lengths/types violate schema.
- `429`/`5xx` should be retried with bounded backoff.

### SDK call mapping

- Python GA:
  - `AxmeClient.get_user_profile(...)`
  - `AxmeClient.update_user_profile(...)`
- TypeScript GA:
  - `AxmeClient.getUserProfile(...)`
  - `AxmeClient.updateUserProfile(...)`
- Beta kickoff:
  - Go: `Client.GetUserProfile(...)`, `Client.UpdateUserProfile(...)`
  - Java: `AxmeClient.getUserProfile(...)`, `AxmeClient.updateUserProfile(...)`
  - .NET: `AxmeClient.GetUserProfileAsync(...)`, `AxmeClient.UpdateUserProfileAsync(...)`

### Conformance expectation

- Covered by executable checks in `axme-conformance`:
  - `users_profile_get`
  - `users_profile_update`
