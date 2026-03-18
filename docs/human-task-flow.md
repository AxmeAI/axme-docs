# Human Task Flow

AXME supports three paths for human-in-the-loop (HITL) task resolution: CLI, email, and structured form. All three integrate with the same workflow step model — `tool.approval.human_signoff` with a `human_task` configuration.

## CLI path

The simplest HITL flow. A workflow step pauses and the human resolves it using the AXME CLI.

**Workflow:**
1. Scenario is applied: `axme scenarios apply scenario.json --watch`
2. Agent step completes, workflow advances to the human approval step
3. Human lists pending tasks: `axme tasks list`
4. Human approves or rejects: `axme tasks approve <task_id>` or `axme tasks reject <task_id>`
5. Workflow resumes based on the decision

**Scenario configuration:**
```json
{
  "step_id": "ops_approval",
  "tool_id": "tool.approval.human_signoff",
  "assigned_to": "operator",
  "requires_approval": true,
  "step_deadline_seconds": 3600,
  "human_task": {
    "title": "Deployment approval — api-gateway v3.2.1 → staging",
    "description": "Review readiness check results and approve or reject."
  }
}
```

No `notify_email` or `form_schema` needed — the human uses `axme tasks list` to discover pending work.

**Example:** `axme-examples/examples/human/cli/`

## Email path

For approvers who are not CLI users. AXME sends an email with a magic link that allows one-click approve or reject.

**Workflow:**
1. Scenario is applied
2. Agent step completes, workflow advances to the human approval step
3. AXME sends an email to the `notify_email` address with:
   - Task title and description
   - Magic link with an embedded action token (7-day TTL)
   - One-click approve/reject buttons
4. Approver clicks the link — no login required
5. Workflow resumes based on the decision

**Scenario configuration:**
```json
{
  "step_id": "finance_approval",
  "tool_id": "tool.approval.human_signoff",
  "assigned_to": "approver",
  "requires_approval": true,
  "step_deadline_seconds": 86400,
  "human_task": {
    "title": "Budget approval — Q3 cloud infrastructure $32,000",
    "description": "Approve or reject the Q3 cloud infrastructure budget request.",
    "notify_email": "finance-approver@example.com"
  }
}
```

Adding `notify_email` triggers the email path. The magic link token is single-use and expires after 7 days or when the step deadline is reached, whichever comes first.

**Example:** `axme-examples/examples/human/email/`

## Form path

For tasks that require structured data beyond a simple approve/reject. The `form_schema` field defines a JSON Schema that the human must complete.

**Workflow:**
1. Scenario is applied
2. Agent step completes, workflow advances to the human approval step
3. If `notify_email` is set, AXME sends an email with a link to the form
4. Human fills in the form (via email link or CLI)
5. AXME validates the submission against `form_schema`
6. Workflow resumes with the form data as the step result

**Scenario configuration:**
```json
{
  "step_id": "security_signoff",
  "tool_id": "tool.approval.human_signoff",
  "assigned_to": "security_officer",
  "requires_approval": true,
  "step_deadline_seconds": 7200,
  "human_task": {
    "title": "Access grant approval — READ on prod-analytics-db",
    "description": "Grant or deny READ access. Complete all required form fields.",
    "notify_email": "security@example.com",
    "form_schema": {
      "type": "object",
      "required": ["approved", "grant_duration_days", "scope_confirmed"],
      "properties": {
        "approved": {
          "type": "boolean",
          "description": "Approve or reject the access request"
        },
        "grant_duration_days": {
          "type": "integer",
          "minimum": 1,
          "maximum": 90,
          "description": "Number of days to grant access (1-90)"
        },
        "scope_confirmed": {
          "type": "boolean",
          "description": "Confirm that READ-only scope is appropriate"
        },
        "notes": {
          "type": "string",
          "description": "Optional audit notes"
        }
      }
    }
  }
}
```

The `form_schema` follows standard JSON Schema. Required fields must be present in the submission. AXME validates types, ranges, and enums before accepting the response.

**Example:** `axme-examples/examples/human/form/`

## Reminders and escalation

All three HITL paths support automatic reminders and deadline enforcement.

| Field | Description |
|-------|-------------|
| `step_deadline_seconds` | Maximum time for the step. After this, the step transitions to `TIMED_OUT` |
| `remind_after_seconds` | Seconds after the step starts before the first reminder is sent |
| `remind_interval_seconds` | Seconds between subsequent reminders |
| `max_reminders` | Maximum number of reminders. After exhaustion, the step waits for the deadline or times out |

**Example with aggressive reminders (30-second intervals):**
```json
{
  "step_deadline_seconds": 300,
  "remind_after_seconds": 30,
  "remind_interval_seconds": 30,
  "max_reminders": 3
}
```

This sends reminders at 30s, 60s, and 90s after the step starts. If the human does not respond by 300s, the step times out.

Reminders are delivered via the same channel as the original notification:
- If `notify_email` is set, reminders go to the same email address
- If no email, reminders appear as events in the intent event stream (visible via `axme intents events <id>`)

**Example:** `axme-examples/examples/internal/reminder/`

## Allowed outcomes

By default, human tasks support `approved` and `rejected` outcomes. Use `allowed_outcomes` to customize:

```json
{
  "human_task": {
    "title": "Infrastructure change request",
    "allowed_outcomes": ["approved", "rejected", "deferred"]
  }
}
```

**Example:** `axme-examples/examples/internal/human_approval/`

## See also

- [ScenarioBundle Reference](scenario-bundle-reference.md) — full schema for scenario JSON files
- [Delivery Bindings](delivery-bindings.md) — how intents reach agents
- [Internal Runtime Model](internal-runtime-model.md) — built-in tools including `human_signoff`
