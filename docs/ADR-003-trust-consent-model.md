# ADR-003: Trust and Consent Model (MVP)

- Status: Accepted
- Date: 2026-02-20

## Context

Axme automates communication and actions across multiple parties. MVP needs explicit trust and consent boundaries so automation remains predictable and safe.

## Decision

Adopt a default-deny trust model with explicit consent gates:

- Default mode:
  - Agents can process and relay intents
  - Agents cannot execute risky actions without explicit user consent
- Consent classes:
  - Auto-allowed: low-risk communication actions (ask, remind, summarize)
  - Approval-required: actions with user impact (external sends on behalf, scheduling commits, escalation to sensitive channels)
  - Blocked: actions violating policy or missing required context
- Decision recording:
  - Each policy/consent decision is persisted as an event in workflow trace
  - Reject/block responses include a machine-readable reason
- Delegation:
  - User may delegate handling of a thread
  - Delegation scope is bounded to the active thread and current policy version

## Consequences

- Risky actions are transparent and auditable.
- Product can ship MVP automation safely while preserving user control.
- Policy engine implementation has clear acceptance criteria.
