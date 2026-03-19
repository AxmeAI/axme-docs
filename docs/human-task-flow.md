# Human Task Flow

AXME supports four paths for human-in-the-loop (HITL) task resolution: CLI, email, web page, and structured form. All four integrate with the same workflow step model — `tool.approval.human_signoff` with a `human_task` configuration.

## Task types

AXME defines seven task types that control default outcomes and UI behavior:

| Type | Purpose | Default outcomes |
|------|---------|-----------------|
| `approval` | Binary yes/no gate | `approved`, `rejected` |
| `review` | Verify work, approve or request changes | `approved`, `changes_requested`, `rejected` |
| `clarification` | Provide information or data | `provided`, `rejected` |
| `manual_action` | Perform a real-world action | `completed`, `failed` |
| `confirmation` | Confirm an external action happened | `confirmed`, `rejected` |
| `assignment` | Designate responsible party | `assigned`, `declined` |
| `override` | Explicit exception to policy | `override_approved`, `rejected` |

Set `task_type` in the `human_task` configuration. If `allowed_outcomes` is explicitly set, it takes precedence over the type defaults.

## CLI path

The simplest HITL flow. A workflow step pauses and the human resolves it using the AXME CLI.

**Workflow:**
1. Scenario is applied: `axme scenarios apply scenario.json --watch`
2. Agent step completes, workflow advances to the human approval step
3. Human lists pending tasks: `axme tasks list`
4. Human approves or rejects: `axme tasks approve <task_id>` or `axme tasks reject <task_id>`
5. Workflow resumes based on the decision

**CLI commands per task type:**

| Task type | Commands |
|-----------|----------|
| `approval` | `axme tasks approve <id>`, `axme tasks reject <id>` |
| `review` | `axme tasks approve <id>`, `axme tasks submit <id> --outcome changes_requested --comment "..."` |
| `clarification` | `axme tasks submit <id> --outcome provided --data-json '{...}'` |
| `manual_action` | `axme tasks complete <id>`, `axme tasks submit <id> --outcome failed` |
| `confirmation` | `axme tasks confirm <id>`, `axme tasks reject <id>` |
| `assignment` | `axme tasks assign <id> --data assignee=user@example.com` |
| `override` | `axme tasks submit <id> --outcome override_approved --comment "..."` |

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

## Email + web page path

For approvers who are not CLI users. AXME sends an email with a link to a web page where the human can view task details and take action.

**Workflow:**
1. Scenario is applied
2. Agent step completes, workflow advances to the human task step
3. AXME sends an email to the `notify_email` address with:
   - Task title and description
   - A link to the web task page with an embedded token
4. Human opens the link — sees task details, action buttons, and form fields (if applicable)
5. Human clicks an action button (e.g., Approve) and confirms
6. Workflow resumes based on the decision

**Email format:**
```
You have a new task assigned: Budget approval — Q3 cloud infrastructure $32,000

Approve or reject the Q3 cloud infrastructure budget request.

Task type: approval
Intent ID: 1a6d9b75-aef5-406d-b3d9-495d162611d4

View task details and APPROVED / REJECTED:
https://cloud.axme.ai/app/tasks/1a6d9b75-aef5-406d-b3d9-495d162611d4?token=...

This link expires in 168 hours.
```

**Web page features:**
- Task title, description, and metadata
- Action buttons styled per task type (Approve/Reject, Confirm/Deny, etc.)
- Form fields rendered from `form_schema` (text, number, boolean, select)
- Comment textarea (required or optional depending on task config)
- Evidence field when `evidence_required: true`
- Confirmation modal before every action ("Are you sure you want to APPROVE?")
- Error states: expired token, already resolved, network error

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

Adding `notify_email` triggers the email + web page path. The token is single-use and expires after 7 days or when the step deadline is reached, whichever comes first.

**Example:** `axme-examples/examples/human/email/`

## Form path

For tasks that require structured data beyond a simple approve/reject. The `form_schema` field defines a JSON Schema that the human must complete.

**Workflow:**
1. Scenario is applied
2. Agent step completes, workflow advances to the human approval step
3. If `notify_email` is set, AXME sends an email with a link to the web page
4. Human fills in the form (via web page or CLI)
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

The `form_schema` follows standard JSON Schema. Required fields must be present in the submission. AXME validates types, ranges, and enums before accepting the response. The web task page renders form fields automatically from the schema.

**Example:** `axme-examples/examples/human/form/`

## Task type examples

### Review

Three-way decision: approve, request changes, or reject.

```json
{
  "human_task": {
    "title": "Review PR #847 — Add retry logic to payment service",
    "task_type": "review",
    "notify_email": "reviewer@example.com"
  }
}
```

Default outcomes: `approved`, `changes_requested`, `rejected`.

**Example:** `axme-examples/examples/human/review/`

### Clarification

Request structured data from a human. Typically paired with `form_schema`.

```json
{
  "human_task": {
    "title": "Clarification needed — Customer ABC Corp onboarding",
    "task_type": "clarification",
    "notify_email": "cs-rep@example.com",
    "form_schema": {
      "type": "object",
      "required": ["billing_contact_email"],
      "properties": {
        "billing_contact_email": { "type": "string" }
      }
    }
  }
}
```

Default outcomes: `provided`, `rejected`.

**Example:** `axme-examples/examples/human/clarification/`

### Manual action

Perform a real-world action and report back. Often paired with `evidence_required`.

```json
{
  "human_task": {
    "title": "Inspect server rack B-14 — elevated temperature alert",
    "task_type": "manual_action",
    "evidence_required": true,
    "notify_email": "dc-ops@example.com"
  }
}
```

Default outcomes: `completed`, `failed`.

**Example:** `axme-examples/examples/human/manual-action/`

### Confirmation

Confirm that an external action has been completed.

```json
{
  "human_task": {
    "title": "Confirm DNS propagation — api.example.com CNAME update",
    "task_type": "confirmation",
    "notify_email": "netops@example.com"
  }
}
```

Default outcomes: `confirmed`, `rejected`.

**Example:** `axme-examples/examples/human/confirmation/`

### Assignment

Designate a responsible party. Typically paired with `form_schema` for the assignee field.

```json
{
  "human_task": {
    "title": "Assign incident commander — P1: Payment processing outage",
    "task_type": "assignment",
    "notify_email": "oncall-manager@example.com",
    "form_schema": {
      "type": "object",
      "required": ["assignee_email"],
      "properties": {
        "assignee_email": { "type": "string" }
      }
    }
  }
}
```

Default outcomes: `assigned`, `declined`.

**Example:** `axme-examples/examples/human/assignment/`

### Override

Explicit exception to policy. Always requires a comment.

```json
{
  "human_task": {
    "title": "Override — deploy api-gateway v3.5.0 outside change window",
    "task_type": "override",
    "required_comment": true,
    "notify_email": "senior-ops@example.com"
  }
}
```

Default outcomes: `override_approved`, `rejected`.

**Example:** `axme-examples/examples/human/override/`

## Reminders and escalation

All HITL paths support automatic reminders and deadline enforcement.

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

By default, outcomes are derived from `task_type`. Use `allowed_outcomes` to override:

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
