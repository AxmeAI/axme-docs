# Claude MCP Setup Runbook

## Integration Mode

- Mode: `provider-managed linking` for Claude MCP integration.
- Claude manages provider-side auth state.
- Axme remains source of truth for sessions and owner isolation.

## Prerequisites

- Platform MCP server is deployed at `https://mcp.cloud.axme.ai`.
- `AXME_MCP_REQUIRE_AUTH=true` is set.
- JWT validation is configured (`JWKS` preferred in prod).

## First-Link Flow

1. User configures Axme MCP in Claude environment.
2. Claude completes auth handshake against Axme auth flow.
3. User logs in by `nick + password`.
4. Claude receives bearer and starts MCP `tools/call`.
5. Axme validates bearer and derives `owner_agent`.

Expected Axme state:

- one active `auth_sessions` record for Claude link;
- one active `assistant_links` record with provider `claude`.

## Lifecycle Scenarios

- `token-expired`: requests fail with `401`, re-auth is requested.
- `refresh-failed`: connector enters re-link state, revoked session chain is not reusable.
- `account-switch`: owner mismatch is blocked with `403`.
- `unlink`: revoke the corresponding session and assistant link.

## Verification Checklist

- Happy path: login → `axme.intents_send` → `axme.intents_trace` → `axme.tasks_approve`.
- All 48 platform tools available via `tools/list`.
- Owner isolation: cross-owner requests are denied.
- Re-link to same account restores profile continuity.
- Logout or revoke immediately invalidates subsequent tool calls.
