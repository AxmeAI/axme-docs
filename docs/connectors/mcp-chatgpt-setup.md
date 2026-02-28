# ChatGPT MCP Setup Runbook

## Integration Mode

- Mode: `provider-managed linking`.
- ChatGPT manages provider-side OAuth/session state.
- Axme keeps its own user session state in `auth_sessions` and `assistant_links`.

## Prerequisites

- Public MCP endpoint is reachable over HTTPS.
- `mcp_server` is configured with:
  - `AXME_MCP_REQUIRE_AUTH=true`
  - `AXME_OWNER_CLAIM=owner_agent`
  - JWT validation config (`AXME_JWKS_URL` or `AUTH_JWT_SECRET`).
- Gateway and auth service are healthy.

## First-Link Flow

1. User adds/opens Axme MCP integration in ChatGPT.
2. ChatGPT initiates auth/link flow and obtains Axme bearer.
3. User logs in with `nick + password` in Axme auth page.
4. MCP `initialize` and `tools/list` succeed.
5. First `tools/call` with bearer succeeds and maps to Axme owner.

Expected Axme state:

- one active row in `auth_sessions` for this linked ChatGPT session;
- one active row in `assistant_links` with provider `chatgpt`.

## Lifecycle Scenarios

- `token-expired`: bearer rejected with `401`; user re-authenticates; new/rotated session appears.
- `refresh-failed`: link falls to re-link path; old session is revoked.
- `account-switch`: old owner scope is rejected, new link binds to new owner.
- `unlink`: provider unlink triggers Axme session revoke; subsequent tool calls fail with `401`.

## Verification Checklist

- Register/login works from ChatGPT flow.
- `axme.send_message` creates intent in gateway.
- `axme.list_inbox` and `axme.reply` work under same owner scope.
- `cross-owner` access returns `403`.
- Re-link restores access to same Axme profile for the same account.
