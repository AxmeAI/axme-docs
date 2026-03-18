# Internal Runtime Model

AXME's agent-core is the server-side orchestrator that manages workflow execution. Some steps run inside agent-core without any external agent — these use the **internal** delivery model.

## Agent-core vs external agents

| Aspect | Agent-core (internal) | External agent |
|--------|----------------------|----------------|
| Where it runs | Inside AXME's server-side runtime | Your infrastructure (Cloud Run, EC2, Lambda, etc.) |
| Delivery | No delivery needed — in-process | `stream`, `poll`, `http`, or `inbox` |
| SDK required | No | Yes (`axme` Python/TypeScript/Go SDK) |
| Use case | Human gates, delays, notifications, escalation | Custom business logic, integrations |

## When does agent-core handle a step?

A step runs internally when:
1. The `tool_id` is a built-in tool (see below), OR
2. The step has no `assigned_to` agent, OR
3. The scenario has no `agents[]` array — pure internal execution

If a step's `tool_id` is `tool.agent.task.v1` and `assigned_to` references an entry in `agents[]`, the step is delivered externally using that agent's `delivery_mode`.

## Built-in tools

### tool.approval.human_signoff

Pauses the workflow for human approval. The step waits until a human approves, rejects, or the deadline expires.

- Assigned to a role from `humans[]`
- Supports CLI, email, and form-based resolution (see [Human Task Flow](human-task-flow.md))
- Configurable reminders and deadline enforcement

```json
{
  "step_id": "ops_approval",
  "tool_id": "tool.approval.human_signoff",
  "assigned_to": "operator",
  "requires_approval": true,
  "step_deadline_seconds": 3600,
  "remind_after_seconds": 600,
  "max_reminders": 3,
  "human_task": {
    "title": "Deployment approval required",
    "description": "Review and approve or reject."
  }
}
```

**Examples:**
- `axme-examples/examples/human/cli/` — CLI-based approval
- `axme-examples/examples/human/email/` — Email-based approval
- `axme-examples/examples/human/form/` — Form-based approval
- `axme-examples/examples/internal/human_approval/` — Pure internal approval (no agent preprocessing)

### tool.notification.notify_owner

Sends a notification to the designated owner and optionally waits for acknowledgement. Similar to `human_signoff` but semantically represents an alert rather than an approval gate.

```json
{
  "step_id": "notify_owner",
  "tool_id": "tool.notification.notify_owner",
  "assigned_to": "owner",
  "requires_approval": true,
  "step_deadline_seconds": 3600,
  "human_task": {
    "title": "Risk alert — api-gateway deployment risk: HIGH",
    "description": "Review the risk assessment and acknowledge."
  }
}
```

**Example:** `axme-examples/examples/internal/notification/`

### Step-level deadlines (timeout enforcement)

Every step can have a `step_deadline_seconds`. If the step is not completed within this window, it transitions to `TIMED_OUT`. This applies to both agent steps and human steps.

```json
{
  "step_id": "validate_window",
  "tool_id": "tool.agent.task.v1",
  "assigned_to": "validator",
  "step_deadline_seconds": 15
}
```

Run this scenario without a listening agent to observe the step timeout after 15 seconds.

**Example:** `axme-examples/examples/internal/timeout/`

### Reminder and escalation chains

Reminders are built into the runtime. When a step has `remind_after_seconds`, `remind_interval_seconds`, and `max_reminders`, agent-core automatically sends reminders on schedule. If `notify_email` is set in `human_task`, reminders go to that email address.

After `max_reminders` are exhausted without a response, the step continues to wait until `step_deadline_seconds` expires, at which point it transitions to `TIMED_OUT` — triggering an escalation event that downstream consumers can act on.

```json
{
  "step_deadline_seconds": 300,
  "remind_after_seconds": 60,
  "remind_interval_seconds": 60,
  "max_reminders": 3,
  "human_task": {
    "title": "Incident acknowledgement required — P2",
    "description": "SLA: 5 minutes. Reminders every 60 seconds."
  }
}
```

**Examples:**
- `axme-examples/examples/internal/reminder/` — Periodic reminders for pending tasks
- `axme-examples/examples/internal/escalation/` — SLA breach triggers reminder chain and timeout

### Step-level delay (deadline as SLA)

Use `step_deadline_seconds` on an agent step to enforce per-step SLAs. The agent must complete its work within the deadline. If it does not respond in time, the step transitions to `TIMED_OUT`.

**Example:** `axme-examples/examples/internal/delay/`

## Pure internal scenarios

Scenarios with no `agents[]` array run entirely inside agent-core. The `internal/human_approval` example demonstrates this — a single `tool.approval.human_signoff` step with no agent preprocessing:

```json
{
  "scenario_id": "internal.human_approval.v1",
  "title": "Direct human gate without agent preprocessing",

  "humans": [
    { "role": "approver", "display_name": "Direct Approver" }
  ],

  "workflow": {
    "steps": [
      {
        "step_id": "direct_approval",
        "tool_id": "tool.approval.human_signoff",
        "assigned_to": "approver",
        "requires_approval": true,
        "step_deadline_seconds": 3600,
        "human_task": {
          "title": "Infrastructure change request",
          "description": "No automated pre-checks — review the payload and decide.",
          "allowed_outcomes": ["approved", "rejected", "deferred"]
        }
      }
    ]
  },

  "intent": {
    "type": "intent.infra.direct_approval.v1",
    "payload": { "request_id": "INFRA-DA-001", "change_type": "network_acl_update" },
    "max_delivery_attempts": 3
  }
}
```

## See also

- [ScenarioBundle Reference](scenario-bundle-reference.md) — full schema for scenario JSON files
- [Human Task Flow](human-task-flow.md) — CLI, email, and form approval paths
- [Delivery Bindings](delivery-bindings.md) — external delivery modes
