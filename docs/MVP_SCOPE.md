# Axme MVP Scope (v0.1)

## Goal

Deliver a closed beta where external assistants submit intents to Axme, Axme executes agent workflows, and users can reply or approve actions via mobile app (with web fallback when app is not installed).

## Product Layers

1. Protocol and Identity layer (`AXP + The Registry`)
2. Application layer (`Axme`)

These layers are developed as independent products with separate responsibilities.

## Canonical Protocol Name

- Canonical name: `AXP`
- Legacy protocol aliases in old notes are considered deprecated and must be replaced with `AXP`.
- Canonical concept: `AXP` is the Intent Protocol (durable execution layer).

## Agent Classes

- Interface LLM agents (ChatGPT, Gemini, other assistants)
- Cloud personal agents (long-running orchestration services)

## P0 Scenarios (In MVP)

- Async question and answer between agents
- Clarification loop
- Multi-party scheduling (majority + one priority participant)
- Conditional escalation (`no response -> remind -> owner notify`)
- In-app incoming intent with manual reply or delegation to cloud agent

## Explicit Non-Goals (Out of MVP v0.1)

- Full chat messenger UX (groups, media, reactions, typing indicators)
- Complex reputation/social mechanics UI
- Offline-first multi-device conflict resolution
- Integrations marketplace

## MVP Success Criteria

- External client can create intent and track final status
- Receiver with installed app can respond or delegate in-app
- One end-to-end workflow is recoverable after service restart/failure path
- Trace IDs exist for debugging failed workflows
- Inbox API foundation for client actions exists (`/v1/inbox` list/get/reply/delegate/approve/reject)
