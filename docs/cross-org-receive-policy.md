# Cross-Org Receive Policy

Control which external organizations can send intents to your org and agents.

## Overview

Cross-org intent delivery is governed by a three-level access control chain:

1. **Org receive policy** — org-wide default for inbound cross-org intents
2. **Agent receive override** — per-agent exception to the org default
3. **Agent send policy** — per-agent control on who can send (existing, orthogonal)

Intra-org sends (same `org_id`) always bypass the receive policy — no enforcement.

## Org Receive Policy

Each organization has a receive policy that controls whether external senders can deliver intents to any agent in the org.

| Mode | Behavior |
|---|---|
| `closed` | Reject all cross-org inbound intents (default) |
| `allowlist` | Accept only from senders matching allowlist patterns |
| `open` | Accept cross-org intents from any sender |

Default is `closed` — no cross-org traffic is accepted until explicitly configured.

### API

#### Get org receive policy

```
GET /v1/organizations/{org_id}/receive-policy
```

**Response:**
```json
{
  "ok": true,
  "policy": {
    "policy_id": "orp_...",
    "org_id": "org_...",
    "policy_type": "closed",
    "entries": [],
    "created_at": "2026-03-21T...",
    "updated_at": "2026-03-21T..."
  }
}
```

#### Set org receive policy

```
PUT /v1/organizations/{org_id}/receive-policy
Content-Type: application/json

{ "policy_type": "allowlist" }
```

Valid values: `open`, `allowlist`, `closed`.

#### Add allowlist entry

```
POST /v1/organizations/{org_id}/receive-policy/entries
Content-Type: application/json

{ "sender_pattern": "agent://partner-org/prod/*" }
```

Patterns support exact match or trailing wildcard:
- `agent://acme-corp/prod/billing-bot` — exact agent
- `agent://acme-corp/prod/*` — all agents in workspace
- `agent://acme-corp/*` — all agents in top-level org scope

#### Remove allowlist entry

```
DELETE /v1/organizations/{org_id}/receive-policy/entries/{entry_id}
```

### CLI

```bash
axme org receive-policy get
axme org receive-policy set <open|allowlist|closed>
axme org receive-policy add <sender_pattern>
axme org receive-policy remove <entry_id>
```

## Agent Receive Override

Individual agents can override the org-level receive policy. This enables "public agents" — agents that accept cross-org intents even when the org is closed.

| Override | Behavior |
|---|---|
| `use_org_default` | Follow the org receive policy (default) |
| `open` | Accept cross-org intents regardless of org policy |
| `allowlist` | Accept only from agent-level allowlist entries |
| `closed` | Reject all cross-org intents regardless of org policy |

### API

#### Get agent receive override

```
GET /v1/agents/{address}/receive-override
```

**Response:**
```json
{
  "ok": true,
  "override": {
    "address": "agent://acme-corp/prod/public-api",
    "address_id": "addr_...",
    "override_type": "use_org_default",
    "entries": []
  }
}
```

#### Set agent receive override

```
PUT /v1/agents/{address}/receive-override
Content-Type: application/json

{ "override_type": "open" }
```

Valid values: `open`, `allowlist`, `closed`, `use_org_default`.

Setting `use_org_default` removes the override — the agent falls back to the org policy.

#### Add override allowlist entry

```
POST /v1/agents/{address}/receive-override/entries
Content-Type: application/json

{ "sender_pattern": "agent://vip-partner/prod/bot" }
```

#### Remove override entry

```
DELETE /v1/agents/{address}/receive-override/entries/{entry_id}
```

### CLI

```bash
axme agents receive-override get <address>
axme agents receive-override set <address> <open|allowlist|closed|use_org_default>
axme agents receive-override add <address> <sender_pattern>
axme agents receive-override remove <address> <entry_id>
```

## Enforcement

When an intent is submitted via `POST /v1/intents`:

1. **Intra-org check**: if sender and receiver are in the same org → always allowed, skip receive policy.
2. **Agent override**: if the target agent has an override other than `use_org_default` → apply override policy.
3. **Org policy**: otherwise apply the receiver org's receive policy.
4. **Default**: if no policy row exists → `closed` (reject).

### Error codes

| Code | Meaning |
|---|---|
| `receiver_org_closed` | Receiver org does not accept cross-org intents |
| `receiver_agent_closed` | Agent override rejects cross-org intents |
| `sender_not_in_receive_allowlist` | Sender not in org or agent allowlist |

All return HTTP 403.

## Access Control

Receive policy endpoints require `org_owner`, `org_admin`, or `platform_admin` role. `workspace_admin` cannot modify org-level receive policies.

## Billing

Cross-org intents count against the **sender's** quota, not the receiver's.

## Example: Public Agent in Closed Org

```bash
# Org is closed by default — no cross-org traffic
axme org receive-policy get
# Mode: closed

# Make one agent publicly accessible
axme agents receive-override set acme-corp/prod/public-api open

# External orgs can now send to this agent only
# All other agents in the org remain protected
```
