# MCP API Reference

## Endpoint

```
POST https://mcp.cloud.axme.ai/mcp
Content-Type: application/json
Authorization: Bearer <account_session_token>
```

**Protocol:** JSON-RPC 2.0 (MCP 2024-11-05)

## Authentication

All `tools/call` requests require a Bearer JWT token obtained via the AXME login flow:

1. `POST /v1/auth/login-intent` → receive OTP by email
2. `POST /v1/auth/login-intent/{id}/verify` → receive `account_session_token` (15-min TTL)
3. `POST /v1/auth/refresh` → rotate token before expiry

Protocol methods (`initialize`, `tools/list`, `ping`) do not require auth.

## Protocol Methods

| Method | Description |
|---|---|
| `initialize` | MCP handshake — returns server info and capabilities |
| `tools/list` | List all 48 available tools with input schemas |
| `tools/call` | Execute a tool (requires auth) |
| `ping` | Health check |
| `resources/list` | Returns empty list (no resources exposed) |
| `prompts/list` | Returns empty list (no prompts exposed) |

## Tools (48 total)

### Status & Identity (3)

| Tool | Description |
|---|---|
| `axme.status` | Gateway health and connectivity |
| `axme.whoami` | Current identity, org, workspace |
| `axme.doctor` | Combined health + context diagnostics |

### Organizations (3)

| Tool | Description |
|---|---|
| `axme.org_list` | List organizations |
| `axme.org_receive_policy_get` | Get org receive policy |
| `axme.org_receive_policy_set` | Set org receive policy (`policy_type`) |

### Workspaces (3)

| Tool | Description |
|---|---|
| `axme.workspace_list` | List workspaces |
| `axme.workspace_use` | Select active workspace (`org_id`, `workspace_id`) |
| `axme.workspace_members_list` | List workspace members |

### Members (4)

| Tool | Description |
|---|---|
| `axme.member_list` | List members (`org_id`) |
| `axme.member_add` | Add member (`org_id`, `actor_id`, `role`) |
| `axme.member_update` | Update member role/status (`org_id`, `member_id`) |
| `axme.member_remove` | Remove member (`org_id`, `member_id`) |

### Agents (9)

| Tool | Description |
|---|---|
| `axme.agents_list` | List registered agents (`org_id`, `workspace_id`) |
| `axme.agents_show` | Show agent details (`address`) |
| `axme.agents_register` | Register new agent (`org_id`, `workspace_id`, `name`) |
| `axme.agents_delete` | Delete agent (`service_account_id`) |
| `axme.agents_keys_create` | Create API key (`service_account_id`) |
| `axme.agents_keys_revoke` | Revoke API key (`service_account_id`, `key_id`) |
| `axme.agents_policy_get` | Get agent send policy (`address`) |
| `axme.agents_policy_set` | Set agent send policy (`address`, `policy_type`) |
| `axme.agents_receive_override` | Get/set receive override (`address`, `action`) |

### Intents (10)

| Tool | Description |
|---|---|
| `axme.intents_send` | Send intent (`to_agent`, `intent_type`, `payload`) |
| `axme.intents_list` | List intents (optional `status`, `limit`) |
| `axme.intents_get` | Get intent details (`intent_id`) |
| `axme.intents_log` | Show lifecycle events (`intent_id`) |
| `axme.intents_cancel` | Cancel intent (`intent_id`, optional `reason`) |
| `axme.intents_resume` | Resume waiting intent (`intent_id`) — resubmits |
| `axme.intents_retry` | Retry failed intent (`intent_id`) — resubmits |
| `axme.intents_watch` | Lifecycle snapshot (`intent_id`) |
| `axme.intents_cleanup` | Cancel zombie intents (`older_than_hours`, `dry_run`) |
| `axme.intents_trace` | Concise timeline — intent summary + events |

### Tasks (8)

| Tool | Description |
|---|---|
| `axme.tasks_list` | List pending tasks assigned to current user |
| `axme.tasks_get` | Get task details (`intent_id`) |
| `axme.tasks_approve` | Approve task (`intent_id`, optional `comment`) |
| `axme.tasks_reject` | Reject task (`intent_id`, optional `comment`) |
| `axme.tasks_confirm` | Confirm task (`intent_id`) |
| `axme.tasks_assign` | Assign task (`intent_id`, optional `data`) |
| `axme.tasks_complete` | Complete manual task (`intent_id`) |
| `axme.tasks_submit` | Submit arbitrary outcome (`intent_id`, `outcome`) |

### Quota (2)

| Tool | Description |
|---|---|
| `axme.quota_show` | Show quota limits and usage (`org_id`, `workspace_id`) |
| `axme.quota_upgrade_request` | Request tier upgrade (`requester_actor_id`, `company_name`, `justification`) |

### Scenarios (4)

| Tool | Description |
|---|---|
| `axme.scenarios_list_templates` | List available macro templates |
| `axme.scenarios_validate` | Validate scenario bundle (`bundle`) |
| `axme.scenarios_apply` | Apply scenario — creates agents, submits intent (`bundle`) |
| `axme.scenarios_create` | Guided builder — returns macros and instructions |

### Sessions (2)

| Tool | Description |
|---|---|
| `axme.session_list` | List account sessions |
| `axme.session_revoke` | Revoke session (`session_id`) |

## Response Format

### Success

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "tool": "axme.intents_send",
    "data": { "intent_id": "..." },
    "message": "Intent submitted",
    "content": [{"type": "text", "text": "axme.intents_send: Intent submitted"}],
    "structuredContent": { ... }
  }
}
```

### Error

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "gateway error 404: intent not found",
    "data": {"ok": false, "error": "gateway_error", "message": "..."}
  }
}
```

### Error Codes

| Code | Meaning |
|---|---|
| `-32700` | Parse error (invalid JSON) |
| `-32600` | Invalid request |
| `-32601` | Method not found |
| `-32602` | Invalid params / tool error |
| `-32001` | Authentication required (401) |
| `-32004` | Rate limit exceeded (429) |

## Quick Start

```bash
# 1. Get a bearer token
curl -X POST https://api.cloud.axme.ai/v1/auth/login-intent \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
# → {"intent_id": "...", "delivery": "email"}

# 2. Verify OTP
curl -X POST https://api.cloud.axme.ai/v1/auth/login-intent/{id}/verify \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
# → {"account_session_token": "eyJ..."}

# 3. Call MCP tools
curl -X POST https://mcp.cloud.axme.ai/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"axme.whoami","arguments":{}}}'
```
