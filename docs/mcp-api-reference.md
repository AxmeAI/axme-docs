# AXME MCP API Reference

The AXME MCP server exposes 28 tools over JSON-RPC 2.0. Any MCP-enabled AI assistant (Claude, ChatGPT, Gemini) can connect to invoke these tools.

## Protocol

| Property | Value |
|---|---|
| Protocol | JSON-RPC 2.0 |
| MCP version | 2024-11-05 |
| Endpoint | `POST /mcp` |
| Batch requests | Supported |
| Transport | HTTP |

### Example request

```http
POST /mcp
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "axme.send_message",
    "arguments": {
      "recipient": "alice",
      "message": "Hello"
    }
  }
}
```

### Response envelope

All tool responses follow this shape:

```json
{
  "ok": true,
  "tool": "axme.tool_name",
  "status": "completed",
  "owner_agent": "agent://owner_address",
  "data": {},
  "content": [{"type": "text", "text": "..."}]
}
```

Possible `status` values: `completed`, `pending_upload`, `needs_clarification`, `contact_not_found`, `disabled`, `not_implemented`.

### Error codes

| Code | Meaning |
|---|---|
| -32600 | Parse error |
| -32601 | Method not found |
| -32602 | Invalid parameters |
| -32001 | Authentication required |
| -32002 | Owner agent required |
| -32003 | Owner mismatch |
| -32004 | Rate limit exceeded |
| -32010 | Gateway error |
| -32011 | Resolution error |

---

## Authentication

### Bearer token (primary)

```http
Authorization: Bearer <jwt_token>
```

- JWT issued by the AXME auth service
- 15-minute TTL
- Required claims: `sub`, `sid`, `owner_agent`
- Scope required: `axme.api`

### Service account key (server-to-server)

```http
x-api-key: <GATEWAY_API_KEY>
```

### Public methods (no auth required)

`initialize`, `tools/list`, `ping`, `axme.check_nick`, `axme.register_nick`, `axme.check_invite_status`

---

## Rate limits

- **120 calls/minute** per `(owner_agent, tool_name)` pair
- Exceeded: HTTP 429 / RPC code -32004

---

## Non-tool methods

| Method | Description |
|---|---|
| `initialize` | Returns server info and protocol version |
| `tools/list` | Lists available tools for the authenticated profile |
| `tools/call` | Invokes a tool (see below) |
| `ping` | Echo — returns `{pong: true}` |
| `resources/list` | Returns empty array |
| `prompts/list` | Returns empty array |

---

## Tools

### Account

#### `axme.register_nick`

Create a new account with a nick.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `nick` | string | ✅ | Unique short identifier |
| `display_name` | string | — | Human-readable name |
| `phone` | string | — | Phone number |
| `email` | string | — | Email address |

**Response:** Profile object with `owner_agent`.

> Note: hidden in assistant-facing profiles by default (`AXME_MCP_EXPOSE_ACCOUNT_TOOLS=false`).

---

#### `axme.check_nick`

Check nick availability before registration. No auth required.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `nick` | string | ✅ | Nick to check |

**Response:** Availability result.

---

#### `axme.rename_nick`

Rename or update account profile.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `nick` | string | ✅ | New nick |
| `display_name` | string | — | New display name |
| `phone` | string | — | New phone |
| `email` | string | — | New email |

**Response:** Updated profile.

---

#### `axme.get_profile`

Get the current user's public profile.

No parameters.

**Response:** Profile object.

---

#### `axme.update_profile`

Update profile fields without changing nick.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `nick` | string | — | New nick |
| `display_name` | string | — | New display name |
| `phone` | string | — | New phone |
| `email` | string | — | New email |

**Response:** Updated profile.

---

### Contacts

#### `axme.resolve_contact`

Resolve a nick or address to a canonical agent address.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ | Nick, email, or agent address (min length 1) |

**Response:** Canonical agent address with resolution metadata.

---

### Messaging

#### `axme.send_message`

Send a text message to a recipient.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `recipient` | string | ✅ | Nick, email, or agent address |
| `message` | string | — | Message text (alias: `text`) |
| `text` | string | — | Message text (alias: `message`) |
| `idempotency_key` | string | — | Deduplication key |
| `attachments` | array | — | Array of `{upload_id: string}` |

**Response:**
```json
{
  "ok": true,
  "status": "accepted",
  "intent_id": "uuid",
  "data": {
    "delivery": "...",
    "resolution": "...",
    "recipient_agent": "agent://..."
  }
}
```

---

#### `axme.send`

Universal send with extended content kinds and delivery semantics.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `to` | string | ✅ | Recipient (alias for `recipient`) |
| `message` | string | — | Text content |
| `content_kind` | enum | — | `text`, `intent`, `media`, `system` |
| `intent` | object | — | Intent payload (when `content_kind=intent`) |
| `semantic_type` | string | — | e.g. `intent.ask.v1` |
| `schema_ref` | string | — | Schema reference URL |
| `schema_mode` | enum | — | `none`, `warn`, `enforce` |
| `chat_file` | object | — | `{download_url, file_id, filename, mime_type}` — auto-uploaded |
| `ack` | enum | — | `accepted`, `delivered`, `read`, `processed` |
| `idempotency_key` | string | — | Deduplication key |
| `attachments` | array | — | Array of `{upload_id: string}` |

> When `chat_file` is provided, the file is automatically downloaded and uploaded to AXME media storage before sending.

**Response:** Extended delivery response with `intent_id` for tracking.

---

#### `axme.confirm_send`

Optional confirmation step for a pending send.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `intent_id` | string | ✅ | Intent ID from `send` or `send_message` |
| `confirm` | boolean | ✅ | Confirm or cancel |

**Response:** `{ok: true, status: "not_implemented"}` — stub, not yet active.

---

### Dialogs

#### `axme.list_dialogs`

List messenger-style dialogs grouped by counterparty.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `unread_only` | boolean | — | Filter to unread dialogs only |
| `limit` | integer | — | 1–100, default 20 |

**Response:** Dialog list with unread counts. Rendered as IRC-style plain text with attachment indexes.

---

#### `axme.open_dialog`

Open a dialog and retrieve message history.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dialog_id` | string | — | Dialog ID |
| `with` | string | — | Nick or agent address of counterparty |
| `limit` | integer | — | 1–50, default 10 |
| `before_message_id` | string | — | Cursor for pagination |
| `mark_read` | boolean | — | Auto-mark as read, default `true` |

> Provide either `dialog_id` or `with`, not both.

**Response:** Dialog with message history.

---

#### `axme.list_threads` (alias: `axme.list_inbox`)

List inbox threads with optional status filter.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `status` | enum | — | `unread`, `read`, `pending`, `active`, `done` |

**Response:** `{ok: true, status: "completed", data: {threads: []}}`

---

#### `axme.get_thread`

Get full thread details including file download links.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `thread_id` | string | ✅ | Thread ID |

**Response:** Thread details with `file_markdown` array of direct download links.

---

### Message operations

#### `axme.reply`

Reply to an existing thread.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `thread_id` | string | ✅ | Thread ID |
| `message` | string | ✅ | Reply text |

**Response:** Updated thread with new message.

---

#### `axme.mark_read`

Mark a thread as read.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `thread_id` | string | ✅ | Thread ID |

**Response:** Updated thread status.

---

#### `axme.delete_messages`

Delete messages from a thread.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `thread_id` | string | ✅ | Thread ID |
| `mode` | enum | — | `self` (own side only) or `both` (all parties), default `self` |
| `message_ids` | array | — | Specific message IDs to delete |
| `last_n` | integer | — | Delete last N messages (1–100) |

> Provide either `message_ids` or `last_n`, not both.

**Response:** Updated thread after deletion.

---

### Invites

#### `axme.generate_invite_link`

Generate a one-time invite link.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `recipient_hint` | string | — | Optional hint (shown to invitee) |
| `ttl_seconds` | integer | — | 60–1209600 (up to 14 days) |

**Response:**
```json
{
  "ok": true,
  "status": "completed",
  "data": {
    "invite_token": "...",
    "link": "https://..."
  }
}
```

---

#### `axme.check_invite_status`

Check invite status. No auth required.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `token` | string | ✅ | Invite token |

**Response:** Invite status and metadata.

---

### Media uploads

#### `axme.media_create_upload`

Initiate a resumable upload and receive a pre-signed upload URL.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filename` | string | ✅ | Original filename |
| `mime_type` | string | ✅ | MIME type |
| `size_bytes` | integer | ✅ | File size in bytes (1–2147483648) |
| `sha256` | string | — | SHA-256 hex digest (64 chars) for integrity check |
| `ttl_seconds` | integer | — | 60–604800 (up to 7 days) |

**Response:**
```json
{
  "ok": true,
  "status": "pending_upload",
  "data": {
    "upload_url": "https://...",
    "upload_id": "uuid"
  }
}
```

After receiving `upload_url`, PUT the file bytes directly to that URL, then call `axme.media_finalize_upload`.

---

#### `axme.media_upload_inline`

Upload a file inline as base64. Use when direct PUT to `upload_url` is blocked.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filename` | string | ✅ | Original filename |
| `mime_type` | string | ✅ | MIME type |
| `content_base64` | string | ✅ | Base64-encoded file content |

**Response:** `{ok: true, status: "ready", data: {upload_id, ...}}`

---

#### `axme.media_finalize_upload`

Finalize after a direct PUT upload.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `upload_id` | string | ✅ | Upload ID from `media_create_upload` |
| `size_bytes` | integer | ✅ | Actual uploaded size (1–2147483648) |
| `sha256` | string | — | SHA-256 hex digest for integrity verification |

**Response:** `{ok: true, status: "ready", data: {upload_id, ...}}`

---

#### `axme.media_get_upload`

Get current upload status.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `upload_id` | string | ✅ | Upload ID |

**Response:** `{ok: true, status: "completed", data: upload_status}`

---

## MCP + AXME continuation pattern

MCP defines **what** your agent can do. AXME defines **how long** it takes and what happens next.

```
AI assistant
    │ MCP tools/call
    ▼
AXME MCP server          ← tools exposed here
    │ POST /v1/intents
    ▼
AXME intent lifecycle    ← durable execution here
    │ stream / poll / reply_to
    ▼
Terminal event (completed / failed / canceled)
```

**Minimal pattern:**

```python
# 1. Use MCP tool to send or trigger intent
result = mcp.call("axme.send", {"to": "agent://target", "message": "process this"})
intent_id = result["intent_id"]

# 2. Observe via AXME SDK (survives disconnects)
for event in axme.observe(intent_id, since=last_seq):
    persist(event.seq)   # save cursor for reconnect
    if event.status in {"completed", "failed", "canceled"}:
        break
```

See the full [Continuation pattern guide](./mcp-axme-continuation-pattern.md) for polling, SSE stream, and offline worker patterns.

---

## Dialog rendering

Dialog messages are rendered as IRC-style plain text:

```
[10:32] alice: Hello, can you review this PR?
[10:33] you: Sure, sending it now.
  [1] attachment: pr-diff.patch (12.4 KB) — [Download]
```

Inline images are rendered as markdown image blocks when `AXME_MCP_INLINE_IMAGE_BLOCKS=true` (default).

---

## Limits

| Limit | Value |
|---|---|
| Rate limit | 120 calls/min per (owner, tool) |
| Max file size | 2 GB (2147483648 bytes) |
| Upload TTL max | 7 days (604800 seconds) |
| Invite TTL max | 14 days (1209600 seconds) |
| Gateway timeout | 10 seconds |
| Registry timeout | 10 seconds |
| JWT clock skew | 60 seconds |
| JWT TTL | 15 minutes |
