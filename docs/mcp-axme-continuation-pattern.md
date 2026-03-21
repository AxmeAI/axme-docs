# MCP + AXME Continuation Pattern

Use MCP and AXME together with clear role separation:

- **MCP**: capability and tool invocation surface — 48 tools at `mcp.cloud.axme.ai`.
- **AXME**: durable continuation and completion observation surface.

## Why Split Responsibilities

- MCP calls can be short-lived and capability-focused.
- Intent execution can be long-lived, stateful, and human-in-the-loop.
- AXME gives a stable continuation contract when initiators disconnect.

## Platform MCP Server

The Platform MCP server exposes the full AXME CLI as MCP tools. AI assistants can manage the entire platform — agents, intents, tasks, scenarios, organizations — through `tools/call`.

**Endpoint:** `https://mcp.cloud.axme.ai/mcp`
**Protocol:** JSON-RPC 2.0 (MCP 2024-11-05)
**Auth:** `Authorization: Bearer <account_session_token>`

Tool groups: `axme.status`, `axme.agents_*`, `axme.intents_*`, `axme.tasks_*`, `axme.scenarios_*`, `axme.org_*`, `axme.workspace_*`, `axme.member_*`, `axme.quota_*`, `axme.session_*`.

## Reference Flow

1. AI assistant discovers tools via MCP `tools/list`.
2. Assistant submits intent via `axme.intents_send` tool.
3. Assistant tracks lifecycle via `axme.intents_trace` or `axme.intents_log`.
4. When intent reaches WAITING (human approval), assistant uses `axme.tasks_approve` or `axme.tasks_reject`.
5. Terminal state (`COMPLETED`, `FAILED`, `CANCELED`) closes loop.

```text
# Via MCP tools/call
tools/call axme.intents_send {to_agent, intent_type, payload}
  → intent_id

tools/call axme.intents_trace {intent_id}
  → status: WAITING, pending_with: human

tools/call axme.tasks_approve {intent_id, comment: "LGTM"}
  → status: COMPLETED
```

## Operational Guidance

- Use `axme.intents_trace` for a compact lifecycle view (intent + events in one call).
- Use `axme.intents_log` for detailed event history with `since` parameter.
- Use `axme.scenarios_apply` for multi-step workflows with agents and human approval gates.
- Persist `intent_id` for cross-session continuation.
- All 48 tools mirror CLI commands 1:1 — anything you can do in `axme` CLI, you can do via MCP.
