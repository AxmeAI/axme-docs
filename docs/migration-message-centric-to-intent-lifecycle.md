# Migration: Message-Centric to Intent Lifecycle

This guide helps teams move from message/RPC-centric integration patterns to the Intent Protocol lifecycle model.

## Before and After

- Before: "send request, wait synchronously, infer completion from transport success"
- After: "submit intent, track durable lifecycle until terminal state"

## Step 1: Replace Request-Coupled Completion

- Replace blocking request semantics with `intent_id` persistence.
- Store `intent_id`, correlation ID, and idempotency key in your job record.

## Step 2: Adopt Lifecycle Observation

- Add event polling with cursor:
  - `GET /v1/intents/{intent_id}/events?since=<seq>`
- Add stream observation where available:
  - `GET /v1/intents/{intent_id}/events/stream`
- Keep polling as mandatory fallback path.

## Step 3: Add Offline Continuation

- Provide `reply_to` during create when producer and consumer are decoupled.
- Consume completion from `reply_to` inbox for worker or batch-driven systems.

## Step 4: Normalize Terminal Handling

Treat terminal statuses as protocol truth:

- `COMPLETED`
- `FAILED`
- `CANCELED`

Do not derive terminal outcome from HTTP transport lifecycle.

## Step 5: Harden Retry and Recovery

- Use idempotency keys for all retryable writes.
- Reuse the same key only with byte-identical payload.
- Resume from last acknowledged `seq` after process restarts.

## Cutover Checklist

- [ ] submit path stores `intent_id`
- [ ] stream + polling parity verified
- [ ] `reply_to` path validated for offline completion
- [ ] terminal immutability tested (`second terminal transition -> conflict`)
- [ ] observability dashboards keyed by `intent_id` and `seq`
