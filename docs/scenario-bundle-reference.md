# ScenarioBundle Reference

A ScenarioBundle is a single JSON file that declares agents, humans, workflow steps, and an intent — everything needed to run an end-to-end scenario through AXME.

## Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scenario_id` | string | Yes | Unique identifier for this scenario (e.g. `human.cli.v1`) |
| `title` | string | No | Human-readable title |
| `description` | string | No | Longer description of what the scenario does |
| `agents` | array | No | Agent definitions. Omit for pure internal/human-only workflows |
| `humans` | array | No | Human participant definitions |
| `workflow` | object | No | Workflow with ordered steps |
| `intent` | object | Yes | Intent to submit when the scenario is applied |

## agents[]

Each entry declares an agent that participates in the workflow.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | Yes | Role name referenced by `assigned_to` in workflow steps |
| `address` | string | Yes | Agent address (short name, e.g. `deploy-readiness-checker`) |
| `display_name` | string | No | Human-readable name shown in UI and events |
| `delivery_mode` | string | No | One of `stream`, `poll`, `http`, `inbox`. See [Delivery Bindings](delivery-bindings.md) |
| `create_if_missing` | bool | No | If `true`, AXME auto-provisions the agent and its API key on apply |

## humans[]

Each entry declares a human participant.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | Yes | Role name referenced by `assigned_to` in workflow steps |
| `contact` | string | No | Contact identifier (e.g. email address) |
| `display_name` | string | No | Human-readable name shown in task assignments |

## workflow{}

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entry_step` | string | No | Step ID to start from (defaults to first step in array) |
| `macro_id` | string | No | Reference to a reusable workflow macro |
| `parameters` | object | No | Key-value parameters passed to macro |
| `steps` | array | Yes | Ordered list of workflow steps |

## workflow.steps[]

Each step represents one unit of work — either an agent task or a human action.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `step_id` | string | Yes | Unique step identifier within the workflow |
| `tool_id` | string | Yes | Tool to execute. `tool.agent.task.v1` for agent steps, `tool.approval.human_signoff` for human gates, `tool.notification.notify_owner` for notifications |
| `assigned_to` | string | No | Role name from `agents[]` or `humans[]` |
| `step_deadline_seconds` | int | No | Maximum time for this step before it transitions to `TIMED_OUT` |
| `input` | object | No | Key-value input passed to the step |
| `on_success` | string | No | Step ID to transition to on success |
| `on_failure` | string | No | Step ID to transition to on failure |
| `requires_approval` | bool | No | If `true`, step pauses for human approval before completing |
| `human_task` | object | No | Human task configuration (see below) |
| `remind_after_seconds` | int | No | Seconds after step starts before first reminder is sent |
| `remind_interval_seconds` | int | No | Seconds between subsequent reminders |
| `max_reminders` | int | No | Maximum number of reminders before the step times out |
| `escalate_to` | string | No | Role to escalate to if step times out |

## human_task{}

Configures the human-facing task within a step.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Task title shown to the human |
| `description` | string | No | Detailed description of what the human should do |
| `task_type` | string | No | Category of the task |
| `allowed_outcomes` | array | No | List of valid outcomes (e.g. `["approved", "rejected", "deferred"]`) |
| `notify_email` | string | No | Email address to send task notification. Includes a magic link for one-click action |
| `form_schema` | object | No | JSON Schema defining a structured form the human must fill in. See [Human Task Flow](human-task-flow.md) |

## intent{}

The intent submitted when the scenario is applied.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Intent type identifier (e.g. `intent.deployment.approval.v1`) |
| `payload` | object | No | Arbitrary JSON payload delivered to the handler |
| `deadline_at` | string | No | ISO 8601 timestamp for intent-level deadline |
| `remind_after_seconds` | int | No | Seconds before first intent-level reminder |
| `remind_interval_seconds` | int | No | Seconds between intent-level reminders |
| `max_reminders` | int | No | Maximum intent-level reminders |
| `escalate_to` | string | No | Role to escalate to on intent timeout |
| `max_delivery_attempts` | int | No | Maximum delivery attempts before dead-letter (default: 3) |

## CLI commands

| Command | Description |
|---------|-------------|
| `axme scenarios apply <file.json> [--watch]` | Submit the scenario. `--watch` streams events in real time |
| `axme scenarios validate <file.json>` | Validate the bundle without submitting |
| `axme scenarios create <file.json>` | Create the scenario (register agents, provision keys) without submitting the intent |
| `axme scenarios list-templates` | List built-in scenario templates |

## Full example

Below is the `human/cli` scenario — an agent checks deployment readiness, then pauses for human approval via CLI:

```json
{
  "scenario_id": "human.cli.v1",
  "title": "Human approval via CLI — deployment readiness check",
  "description": "An automated agent checks deployment readiness. If checks pass, the workflow pauses for a human operator to approve or reject via axme tasks approve / axme tasks reject.",

  "agents": [
    {
      "role": "checker",
      "address": "deploy-readiness-checker",
      "display_name": "Deploy Readiness Checker",
      "delivery_mode": "stream",
      "create_if_missing": true
    }
  ],

  "humans": [
    {
      "role": "operator",
      "display_name": "Operations Team"
    }
  ],

  "workflow": {
    "steps": [
      {
        "step_id": "readiness_check",
        "tool_id": "tool.agent.task.v1",
        "assigned_to": "checker",
        "step_deadline_seconds": 60
      },
      {
        "step_id": "ops_approval",
        "tool_id": "tool.approval.human_signoff",
        "assigned_to": "operator",
        "requires_approval": true,
        "step_deadline_seconds": 3600,
        "remind_after_seconds": 600,
        "remind_interval_seconds": 600,
        "max_reminders": 3,
        "human_task": {
          "title": "Deployment approval — api-gateway v3.2.1 → staging",
          "description": "Review readiness check results and approve or reject the deployment."
        }
      }
    ]
  },

  "intent": {
    "type": "intent.deployment.approval.v1",
    "payload": {
      "deploy_id":    "deploy-20260314-001",
      "service":      "api-gateway",
      "version":      "3.2.1",
      "environment":  "staging",
      "image":        "gcr.io/axme-prod/api-gateway:3.2.1",
      "rollback_tag": "3.1.9",
      "requested_by": "ci/cd-pipeline"
    },
    "max_delivery_attempts": 3
  }
}
```

## See also

- [Delivery Bindings](delivery-bindings.md) — how intents reach agents
- [Human Task Flow](human-task-flow.md) — CLI, email, and form approval paths
- [Internal Runtime Model](internal-runtime-model.md) — built-in tools and agent-core
