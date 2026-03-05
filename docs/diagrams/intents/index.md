# Intents Diagram Pack (Scaffold)

This folder contains first-pass Mermaid sources for intent lifecycle, control, policy, security, and runtime behavior.

## Files

- `01-intent-lifecycle-state-machine.mmd` - canonical status model and terminal paths.
- `02-create-and-control-sequence.mmd` - create + controls/policy/resume flow with CAS conflict branch.
- `03-policy-anatomy.mmd` - `workflow_control_policy` structure and mutable zones.
- `04-waiting-branches-and-wakeups.mmd` - WAITING reasons and wakeup triggers.
- `05-delivery-and-processing-pipeline.mmd` - submission and delivery pipeline, including transport crypto boundary.
- `06-internal-scheduler-loop.mmd` - scheduler/tick/retry/wakeup loop model.
- `07-access-control-matrix.mmd` - actor-role to operation mapping (creator/admin/delegate).
- `08-audit-trail-map.mmd` - mutation actions and audit event chain.
- `09-intent-payload-extensibility-and-semantic-schemas.mmd` - schema mode and payload compatibility path.
- `10-human-in-loop-approval-branches.mmd` - approval/reject branches for waiting human decisions.
- `11-resume-controls-policy-conflict-resolution.mmd` - control mutation conflict and CAS retry flow.

## Suggested placement

- `README` (short "How Intents work" section): diagrams `01`, `02`, `05`.
- Public API docs: diagrams `01`, `02`, `03`, `04`.
- Security and governance docs: diagrams `06`, `07`, `08`.

## Notes

- Diagrams are intentionally source-first (`.mmd`) so they can be rendered into SVG/PNG for docs site and repository pages.
- Keep status names and endpoint names aligned with `docs/openapi/gateway.v1.json` and runtime behavior in gateway implementation.
