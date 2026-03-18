# Agent Addressing Specification

## Overview

Every AXME agent is uniquely identified by an `agent://` URI. This address is the canonical identity used in intent routing (`from_agent`, `to_agent`), inbox ownership, send policies, and audit logs.

## URI Format

```
agent://{org_slug}/{workspace_slug}/{sa_name}
```

### Components

| Component | Description | Uniqueness scope |
|---|---|---|
| `org_slug` | Organization slug | Globally unique across all AXME tenants |
| `workspace_slug` | Workspace slug within the organization | Unique within the organization |
| `sa_name` | Service account name (the agent identity) | Unique within the workspace |

### Validation Regex

```
^agent://[a-z0-9][a-z0-9-]{1,61}[a-z0-9]/[a-z0-9][a-z0-9-]{1,61}[a-z0-9]/[a-z0-9][a-z0-9._-]{0,61}[a-z0-9]$
```

Character rules:

- `org_slug` and `workspace_slug`: lowercase alphanumeric and hyphens, 3-63 characters, must start and end with alphanumeric.
- `sa_name`: lowercase alphanumeric, hyphens, dots, and underscores, 2-63 characters, must start and end with alphanumeric.

## Examples

```
agent://acme-corp/production/approval-bot
agent://acme-corp/staging/change-validator
agent://globex-inc/default/invoice-processor
agent://globex-inc/default/hr-assistant
```

## Address Generation

Agent addresses are **automatically generated** when a service account is created. The mapping is deterministic:

1. The organization's slug, workspace's slug, and service account name are combined.
2. The resulting `agent://` URI is stored in the agent registry.
3. No manual address assignment is supported — the address is always derived from the service account's placement.

### Example

Creating a service account named `approval-bot` in workspace `production` of organization `acme-corp`:

```
POST /v1/service-accounts
{
  "name": "approval-bot",
  "workspace_id": "ws_abc123"
}
```

Automatically registers the agent address:

```
agent://acme-corp/production/approval-bot
```

## Auto-Derivation of `from_agent`

When an intent is submitted via `POST /v1/intents`, the `from_agent` field is **auto-derived** from the caller's API key:

1. The API key identifies the service account.
2. The service account's registered agent address is resolved.
3. That address is used as `from_agent` in the intent envelope.

In production, `from_agent` is never user-supplied — it is always resolved server-side from the authenticated credential. Any client-supplied `from_agent` value is overwritten by the server-derived address.

## Validation of `to_agent`

When an intent is submitted, `to_agent` is validated against the agent registry:

- The address must match the `agent://` URI format (see regex above).
- The address must resolve to a registered agent in the registry.
- If the address is malformed, the gateway returns `422 Unprocessable Entity` with error code `invalid_agent_address`.
- If the address is well-formed but does not match any registered agent, the gateway returns `404 Not Found` with error code `agent_not_found`.

### Backward Compatibility (Migration Period)

During the migration period from legacy addressing to the full `agent://` scheme, `to_agent` validation operates in **soft-fail mode**:

- Addresses that do not match a registered agent produce a warning in the response but do not block delivery.
- This allows existing integrations to continue functioning while adopting the new addressing scheme.
- Soft-fail mode will be removed in a future release once migration is complete.

## Agent Lookup

To resolve an agent address to its details:

```
GET /v1/agents/{address}
```

Where `{address}` is the URL-encoded `agent://` URI (e.g., `agent%3A%2F%2Facme-corp%2Fproduction%2Fapproval-bot`).

To list all agents in the caller's scope:

```
GET /v1/agents
```

See [public-api-families-d6-enterprise-governance.md](public-api-families-d6-enterprise-governance.md) for full endpoint documentation.

## Related Documents

- [public-api-families-d6-enterprise-governance.md](public-api-families-d6-enterprise-governance.md) — agent registry and send policy endpoints
- [public-api-families-d1-intents-inbox-approvals.md](public-api-families-d1-intents-inbox-approvals.md) — intent submission and `from_agent`/`to_agent` usage
- [public-api-auth.md](public-api-auth.md) — API key and actor token authentication model
- [supported-limits-and-error-model.md](supported-limits-and-error-model.md) — error codes for agent addressing failures
