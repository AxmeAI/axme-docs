# Gemini MCP Setup Runbook

## Integration Mode

- Mode: `provider-managed linking`.
- Gemini stores provider-side linking state.
- Axme stores session and assistant binding in `auth_sessions` and `assistant_links`.

## Prerequisites

- MCP endpoint is exposed via HTTPS.
- `mcp_server` and `gateway` pass health checks.
- JWT/JWKS validation is enabled in MCP and gateway.

## First-Link Flow

1. User enables Axme MCP connector in Gemini.
2. Gemini starts auth redirect to Axme.
3. User logs in (`nick + password`) and grants link.
4. Gemini calls MCP tools with bearer token.
5. Axme maps token claim to `owner_agent`.

Expected Axme state:

- active `auth_sessions` row for Gemini client;
- active `assistant_links` row with provider `gemini`.

## Lifecycle Scenarios

- `token-expired`: MCP responds `401`, Gemini requests re-auth.
- `refresh-failed`: old session chain is revoked, user must re-link.
- `account-switch`: link must bind to new Axme account; owner mismatch returns `403`.
- `unlink`: session revoke is visible in `/v1/auth/sessions` and `/v1/auth/assistant-links`.

## Verification Checklist

- Link + login completes with no manual backend actions.
- `axme.resolve_contact`, `axme.send_message`, `axme.reply` succeed.
- Multi-device profile continuity is preserved for same Gemini account.
- Unlinked or expired state consistently returns auth errors, not silent failures.
