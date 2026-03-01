# AXME Is Not RPC

Canonical statement:

- **AXP is the Intent Protocol (durable execution layer).**

This means the API is modeled around durable intent lifecycle state, not synchronous call/return semantics.

## What This Changes

- `POST /v1/intents` records requested outcome and returns `intent_id`.
- Completion is discovered through lifecycle observation, not request blocking.
- Clients can disconnect and reconnect without losing completion visibility.
- Event ordering is protocol-level (`seq`) and replayable (`since`).

## Continuation Delivery (v1)

AXME supports three continuation mechanisms:

- Event stream: `GET /v1/intents/{intent_id}/events/stream`
- Polling: `GET /v1/intents/{intent_id}` and `GET /v1/intents/{intent_id}/events?since=<seq>`
- Deliver-to-inbox: pass `reply_to` on create and observe completion in that inbox

## Design Rules

- Do not model `create_intent` as "remote function call that must finish now".
- Do not rely on HTTP callbacks as the only completion path.
- Treat `intent_id` as the durable join key across retries, observability, and recovery.
- Use idempotency keys for retryable writes and preserve payload identity across replays.

## Anti-Pattern vs Pattern

- Anti-pattern: "submit intent, block until done, fail if socket closes"
- Pattern: "submit intent, persist `intent_id`, resume via stream/poll/inbox"
