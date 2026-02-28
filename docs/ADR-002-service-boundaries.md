# ADR-002: Service Boundaries for MVP

- Status: Accepted
- Date: 2026-02-20

## Context

Axme MVP includes multiple services that must evolve independently. Clear boundaries are needed to avoid coupling and accidental logic duplication.

## Decision

Define service boundaries as follows:

- `services/registry`
  - Identity resolution (`email/phone -> agent_address`)
  - Bind and resolve APIs
  - Audit trail for binding changes
- `services/agent_core`
  - Workflow lifecycle (`Plan -> Validate -> Execute`)
  - Intent/workflow state and event history
  - Retry/timeout/escalation orchestration
- `services/gateway` (to be added)
  - Public API for external assistants and partners
  - Auth, idempotency, rate limiting, audit envelope
  - Request normalization into canonical intent envelope
- `services/policy_engine` (to be added)
  - Access, risk, and consent policy decisions
  - Approval gating for risky operations
- `services/integrations` (to be added)
  - External systems (Calendar, Contacts, SMS fallback)
  - OAuth/token lifecycle and provider adapters
- `services/tool_registry` and `services/workflow_compiler` (to be added)
  - Typed action catalog
  - Declarative plan to executable graph compilation

## Consequences

- Business logic remains in Axme services, not in Matrix homeserver code.
- Teams can evolve services independently behind explicit API contracts.
- Integration and testing strategy can be organized per boundary.
