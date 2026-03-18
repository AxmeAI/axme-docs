# Delivery Bindings

AXME supports five delivery bindings that determine how intents reach their handler agent.

## Comparison

| Binding | Direction | Connection | Retry | Best for |
|---------|-----------|------------|-------|----------|
| **stream** | Push (gateway → agent) | Persistent SSE | Automatic reconnect | Real-time, always-on agents |
| **poll** | Pull (agent → gateway) | Periodic long-poll | Agent-controlled | Batch, cron, serverless |
| **http** | Push (gateway → agent) | POST to callback_url | 3 retries (30s, 120s, 600s) | Enterprise webhooks, external services |
| **inbox** | Push (gateway → initiator) | reply_to delivery | N/A | Disconnect-safe async |
| **internal** | None (agent-core) | In-process | Built-in | Built-in tools, orchestration |

## stream

Agent maintains a persistent SSE connection to `GET /v1/agents/{address}/intents/stream`. Gateway pushes intents in real time.

- SDK: `client.listen(address)` / `client.observe(intent_id)`
- Quota: limited by `sse_streams_max` per workspace
- Reconnect: clients resume with `since=<last_seq>` to replay missed events

## poll

Agent periodically connects to the same SSE endpoint with a `wait_seconds` parameter. Gateway blocks until an intent arrives or the timeout expires.

- SDK: `client.listen(address, { waitSeconds: 5 })`
- No persistent connection — agent controls polling interval
- Suitable for serverless or batch processing

## http

Gateway POSTs the intent to the agent's registered `callback_url`. Includes HMAC-SHA256 signature in `X-Axme-Signature` header for verification.

- Retry delays: 30s, 120s, 600s (3 attempts before dead-letter)
- Agent must respond with HTTP 2xx to acknowledge
- Best for external services that expose a webhook endpoint

## inbox

Completion result is delivered to the initiator's `reply_to` inbox address. The initiator polls their inbox via `GET /v1/inbox` or receives thread events.

- Thread-based: preserves conversation timeline
- Supports approve/reject/delegate operations on threads
- Used when the initiator disconnects after submission

## internal

No external delivery. Agent-core handles the step internally using built-in tools:
- `tool.approval.human_signoff` — pause for human approval
- `tool.internal.delay` — wait for a duration
- `tool.internal.notification` — send notification
- `tool.internal.escalation` — escalate to another actor

No SDK polling or streaming needed — everything runs inside the runtime.

## Setting the delivery mode

In a ScenarioBundle:
```json
{
  "agents": [
    { "role": "checker", "address": "my-agent", "delivery_mode": "stream" }
  ]
}
```

Via CLI: `axme agents register --name my-agent --delivery-mode stream --endpoint-url https://...`

## Examples

- `axme-examples/examples/delivery/stream/` — SSE stream delivery
- `axme-examples/examples/delivery/poll/` — Polling delivery
- `axme-examples/examples/delivery/http/` — Webhook delivery
- `axme-examples/examples/delivery/inbox/` — Inbox delivery
- `axme-examples/examples/internal/` — Internal runtime examples
