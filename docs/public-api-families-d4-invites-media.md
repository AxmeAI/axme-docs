# Public API Families D4: Invites and Media

This guide covers the fourth additive parity batch for family-level integration docs:

- `invites.create`
- `invites.get`
- `invites.accept`
- `media.create_upload`
- `media.finalize_upload`
- `media.get`

Use this guide together with:

- `docs/openapi/gateway.v1.json` (canonical endpoint surface)
- `axme-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md` and `docs/supported-limits-and-error-model.md`

## 1) Invites Family

### Purpose and context

Invite endpoints provide controlled onboarding from an existing owner to a new participant. The flow is create invite, inspect invite status, then accept invite to provision the participant identity.

### Endpoint mapping

- `POST /v1/invites/create`
- `GET /v1/invites/{token}`
- `POST /v1/invites/{token}/accept`

### Canonical schemas

- `axme-spec/schemas/public_api/api.invites.create.request.v1.json`
- `axme-spec/schemas/public_api/api.invites.create.response.v1.json`
- `axme-spec/schemas/public_api/api.invites.get.response.v1.json`
- `axme-spec/schemas/public_api/api.invites.accept.request.v1.json`
- `axme-spec/schemas/public_api/api.invites.accept.response.v1.json`

### Request example (`POST /v1/invites/create`)

```json
{
  "owner_agent": "agent://example/owner",
  "recipient_hint": "Partner A",
  "ttl_seconds": 3600
}
```

### Response example (`POST /v1/invites/{token}/accept`)

```json
{
  "ok": true,
  "token": "invite-token-0001",
  "status": "accepted",
  "invite_owner_agent": "agent://example/owner",
  "user_id": "11111111-1111-4111-8111-111111111111",
  "owner_agent": "agent://user/11111111-1111-4111-8111-111111111111",
  "nick": "@partner.user",
  "public_address": "partner.user@ax",
  "accepted_at": "2026-03-01T10:00:00Z",
  "registry_bind_status": "propagated"
}
```

### Idempotency/retry/trace guidance

- Send `Idempotency-Key` on invite create and accept writes when retries are possible.
- Reuse idempotency keys only with byte-identical payloads.
- Include `X-Trace-Id` for create/get/accept to correlate onboarding actions.
- Polling `GET /v1/invites/{token}` is safe retryable read.

### Error and edge cases

- `404` for unknown invite token.
- `409` when accepting an already accepted or expired invite.
- `422` for invalid `nick`, `ttl_seconds`, or request body shape.
- `401`/`403` for auth or owner-scope violations.

### SDK call mapping

- Python GA:
  - `AxmeClient.create_invite(...)`
  - `AxmeClient.get_invite(...)`
  - `AxmeClient.accept_invite(...)`
- TypeScript GA:
  - `AxmeClient.createInvite(...)`
  - `AxmeClient.getInvite(...)`
  - `AxmeClient.acceptInvite(...)`
- Beta SDKs (`Go/Java/.NET`):
  - kickoff baseline currently covers `users.*`; invites helpers are pending later beta expansion.

### Conformance expectation

- Covered by executable checks in `axme-conformance`:
  - `invites_create`
  - `invites_get`
  - `invites_accept`

## 2) Media Family

### Purpose and context

Media endpoints manage upload lifecycle for binary payloads used in workflows. Integrators create upload metadata, upload bytes to signed URLs, finalize the upload, then query media state.

### Endpoint mapping

- `POST /v1/media/create-upload`
- `POST /v1/media/finalize-upload`
- `GET /v1/media/{upload_id}`

Related transport helpers in OpenAPI (outside `public_api` family contracts):

- `PUT /v1/media/upload/{upload_id}`
- `GET /v1/media/download/{upload_id}`
- `GET /v1/media/preview/{upload_id}`

### Canonical schemas

- `axme-spec/schemas/public_api/api.media.create_upload.request.v1.json`
- `axme-spec/schemas/public_api/api.media.create_upload.response.v1.json`
- `axme-spec/schemas/public_api/api.media.finalize_upload.request.v1.json`
- `axme-spec/schemas/public_api/api.media.finalize_upload.response.v1.json`
- `axme-spec/schemas/public_api/api.media.get.response.v1.json`

### Request example (`POST /v1/media/create-upload`)

```json
{
  "owner_agent": "agent://example/owner",
  "filename": "contract.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 12345,
  "sha256": "87bd29db36f41e4b1f4f7f6f45f00c3d131be6af8d0f8d96d7cf6f4a13fd2e2a"
}
```

### Response example (`GET /v1/media/{upload_id}`)

```json
{
  "ok": true,
  "upload": {
    "upload_id": "77777777-7777-4777-8777-000000000001",
    "owner_agent": "agent://example/owner",
    "bucket": "axme-media",
    "object_path": "agent-example-owner/contract.pdf",
    "mime_type": "application/pdf",
    "filename": "contract.pdf",
    "size_bytes": 12345,
    "sha256": "87bd29db36f41e4b1f4f7f6f45f00c3d131be6af8d0f8d96d7cf6f4a13fd2e2a",
    "status": "ready",
    "created_at": "2026-03-01T10:00:00Z",
    "expires_at": "2026-03-02T10:00:00Z",
    "finalized_at": "2026-03-01T10:02:00Z",
    "download_url": "https://media.example/download/77777777-7777-4777-8777-000000000001",
    "preview_url": "https://media.example/preview/77777777-7777-4777-8777-000000000001"
  }
}
```

### Idempotency/retry/trace guidance

- Send `Idempotency-Key` on create/finalize writes when retriable behavior is required.
- Keep payload stable for idempotent replay.
- Treat `GET /v1/media/{upload_id}` as safe retryable read.
- Include `X-Trace-Id` across create/upload/finalize/get to correlate file lifecycle.

### Error and edge cases

- `404` for unknown `upload_id`.
- `409` for invalid lifecycle transition (for example, finalize before upload bytes exist).
- `422` for invalid `size_bytes`, `sha256`, or MIME/filename constraints.
- `413` when uploaded bytes exceed size limits.

### SDK call mapping

- Python GA:
  - `AxmeClient.create_media_upload(...)`
  - `AxmeClient.finalize_media_upload(...)`
  - `AxmeClient.get_media_upload(...)`
- TypeScript GA:
  - `AxmeClient.createMediaUpload(...)`
  - `AxmeClient.finalizeMediaUpload(...)`
  - `AxmeClient.getMediaUpload(...)`
- Beta SDKs (`Go/Java/.NET`):
  - kickoff baseline currently covers `users.*`; media helpers are pending later beta expansion.

### Conformance expectation

- Covered by executable checks in `axme-conformance`:
  - `media_create_upload`
  - `media_get`
  - `media_finalize_upload`
