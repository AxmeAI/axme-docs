# Siri Bridge MCP Setup Runbook

## Integration Mode

- Mode: `API-managed MCP connector` (bridge-controlled lifecycle).
- Siri bridge is responsible for Axme session refresh lifecycle.
- Axme still enforces JWT scope, owner scope, and session validity.

## Prerequisites

- iOS bridge endpoint is deployed and can call Axme MCP.
- Bridge stores secrets/tokens in secure storage (Keychain/KMS-backed backend).
- MCP/gateway JWT policy is enabled with fail-closed behavior.

## First-Link Flow

1. User starts "Connect Axme" from Siri shortcut/app intent.
2. Bridge opens Axme login page (`nick + password`).
3. Axme issues access/refresh session for this bridge client.
4. Bridge associates link with user device/account.
5. Siri request triggers bridge -> MCP tool call under linked owner.

Expected Axme state:

- active `auth_sessions` row (`client_type=mobile` or bridge-specific type);
- active `assistant_links` row associated with this session.

## Lifecycle Scenarios

- `token-expired`: bridge refreshes token; if refresh fails, force re-link.
- `refresh-failed`: revoke session chain and clear local bridge token cache.
- `account-switch`: previous link is unbound; new owner link must be explicit.
- `unlink`: bridge sends revoke, clears local tokens, and reports disconnected state.

## Verification Checklist

- Voice shortcut can send via `axme.send_message`.
- User can fetch/reply in same owner scope.
- Re-link after revoke restores access to same Axme profile.
- Cross-owner access attempts fail with `403`.
