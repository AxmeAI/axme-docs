# MCP + AXME Continuation Pattern

Use MCP and AXME together with clear role separation:

- MCP: capability and tool invocation surface.
- AXME: durable continuation and completion observation surface.

## Why Split Responsibilities

- MCP calls can be short-lived and capability-focused.
- Intent execution can be long-lived, stateful, and human-in-the-loop.
- AXME gives a stable continuation contract when initiators disconnect.

## Reference Flow

1. A client or service chooses tool/capability through MCP.
2. The same client submits execution via `POST /v1/intents`.
3. The client tracks lifecycle with one of:
   - stream: `/v1/intents/{intent_id}/events/stream`
   - polling: `/v1/intents/{intent_id}/events?since=<seq>`
   - inbox continuation: `reply_to` on create
4. Terminal event (`intent.completed`, `intent.failed`, `intent.canceled`) closes loop.

## Operational Guidance

- Persist `intent_id` and latest seen `seq`.
- Resume on reconnect with `since=<last_seq>`.
- Keep polling as compatibility fallback when stream transport is unavailable.
- Keep `reply_to` for offline/worker scenarios where persistent stream is not practical.

## Minimal Pseudocode

```text
intent_id = axme.create_intent(...)
for event in axme.observe(intent_id, since=last_seq):
    persist(event.seq)
    if event.status in {COMPLETED, FAILED, CANCELED}:
        break
```
