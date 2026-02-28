# Android Bridge MCP Setup Runbook

## Integration Mode

- Mode: `API-managed MCP connector` (bridge/app-managed refresh lifecycle).
- Android assistant bridge controls Axme refresh/re-link behavior.
- Axme controls authorization, owner mapping, and session revocation.

## Prerequisites

- Android bridge service/app can call Axme MCP endpoint.
- Secure token storage is enabled (EncryptedSharedPreferences/Keystore or backend vault).
- JWT/JWKS validation is active in MCP and gateway.

## First-Link Flow

1. User starts Axme link from Android assistant/app action.
2. Bridge opens Axme auth (`nick + password`).
3. Bridge receives Axme session tokens for the linked owner.
4. Bridge stores token material securely and starts MCP calls.
5. First tool call confirms owner-scoped access.

Expected Axme state:

- active `auth_sessions` record for Android bridge;
- active `assistant_links` record for this session.

## Lifecycle Scenarios

- `token-expired`: bridge attempts refresh; on failure user is prompted to re-link.
- `refresh-failed`: session chain is revoked and cannot be reused.
- `account-switch`: old owner link is invalidated; new link must re-authenticate.
- `unlink`: bridge revokes Axme session and clears local token cache.

## Verification Checklist

- `resolve -> send -> list -> get -> reply` flow succeeds from bridge path.
- Token expiration handling is deterministic and observable in logs.
- Owner mismatch is rejected with `403`.
- Unlinked state returns `401` and triggers relink UX.
