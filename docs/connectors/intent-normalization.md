# Intent Normalization for Channel Connectors

## Goal

Map channel-specific payloads from ChatGPT and Gemini into one canonical `IntentEnvelope` format.

## Adapter Endpoints

- ChatGPT: `POST /v1/adapt` in `connectors/chatgpt_action_adapter/main.py`
- Gemini: `POST /v1/adapt` in `connectors/gemini_extension_adapter/main.py`

## Canonical Fields

Both adapters output:

- `version` = `v1`
- `intent_type` = `intent.ask.v1` or `intent.reply.v1`
- `intent_id` UUID
- `correlation_id` UUID
- `created_at` RFC3339 timestamp
- `from_agent`, `to_agent`
- `payload` (intent-specific schema)
- optional `idempotency_key`
- optional `metadata`
  - includes `input_mode` (`text` or `voice`)

## Input Mapping

- ChatGPT:
  - `requester_agent -> from_agent`
  - `target_agent -> to_agent` (direct path)
  - `recipient_name -> to_agent` via `registry /contacts/resolve` (resolution path)
  - language-agnostic fuzzy alias matching (typo-tolerant)
  - `confirm_send=true` marks explicit user confirmation and updates server-side trusted mapping cache
  - `resolve_only=true` -> return resolution result without sending to gateway
  - `intent_name -> intent_type`
  - `payload -> payload`
  - `message -> payload.question` for ask or `payload.answer` for reply (flat free-form helper)
  - `workflow_macro_id`, `workflow_macro_params`, `workflow_owner_agent` are passed through into `payload.workflow` for gateway-side macro auto-compile
  - `input_mode -> metadata.input_mode`
- Gemini:
  - `sender_agent -> from_agent`
  - `recipient_agent -> to_agent` (direct path)
  - `recipient_name -> to_agent` via `registry /contacts/resolve` (resolution path)
  - language-agnostic fuzzy alias matching (typo-tolerant)
  - `confirm_send=true` marks explicit user confirmation and updates server-side trusted mapping cache
  - `resolve_only=true` -> return resolution result without sending to gateway
  - `intent -> intent_type`
  - `data -> payload`
  - `message -> payload.question` for ask or `payload.answer` for reply (flat free-form helper)
  - `workflow_macro_id`, `workflow_macro_params`, `workflow_owner_agent` are passed through into `payload.workflow` for gateway-side macro auto-compile
  - `input_mode -> metadata.input_mode`

## Validation

Adapters validate:

- Envelope against `schemas/protocol/intent.envelope.v1.json`
- Payload against intent-specific schema:
  - `intent.ask.v1.json`
  - `intent.reply.v1.json`

## Decision Contract

Server-driven decision shape:

```json
{
  "ok": true,
  "decision_mode": "sent|resolved|needs_confirmation|needs_disambiguation|contact_not_found",
  "resolution": {
    "resolved": true,
    "matched_alias": "Bob",
    "match_type": "memory|exact|fuzzy|smart_fuzzy|explicit"
  }
}
```

Adapters still use normalized `ok=false` errors for invalid input/schema/network failures.

## Confirmation Memory

- Confirmed recipient choices are persisted in registry via `POST /contacts/confirm`.
- Next resolve for the same owner and query can return `match_type=memory`, allowing direct send flow.

## Optional Delivery Receipt

Adapters can optionally submit normalized intents to gateway and return:

```json
{
  "delivery": {
    "submitted": true,
    "via": "gateway",
    "intent_id": "...",
    "status": "accepted|running|done|failed",
    "created_at": "..."
  }
}
```

## Two-Phase Confirmation Pattern

For safer UX in ambiguous human names:

1. Call adapter with `resolve_only=true` and `recipient_name`.
2. If `resolution.resolved=false` and candidates are returned, ask user to choose.
3. Call adapter again with clarified recipient and message (normal send path).
