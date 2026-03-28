# Security Overview

This document describes the public security model for AXME and AXME Cloud.

> **Alpha status:** controls are active and documented, but the platform is still in Alpha and may evolve.

## 1) Authentication model

AXME uses a two-layer authentication model for public APIs:

- **Machine credential** via `x-api-key` (`AXME_API_KEY`, service/workspace identity).
- **Actor context** via `Authorization: Bearer <actor_token>` (user/session/delegated context).

For external usage, `AXME_API_KEY` is typically a service-account key (`axme_sa_...`) issued by AXME Cloud onboarding. Internal deployment secrets (`GATEWAY_API_KEY`, `AUTH_API_KEY`) remain infrastructure-only.

Route classes are explicit:

- **Machine routes:** require `x-api-key`.
- **Machine + actor routes:** require both `x-api-key` and `Authorization`.
- **Interactive/session routes:** require `Authorization`.

Authentication failures return structured error codes (for example: `missing_platform_api_key`, `missing_actor_token`, `invalid_actor_scope`) to make integration debugging deterministic.

### Token model (CLI / interactive sessions)

The actor context uses a **two-token model**:

| Token | Type | TTL | Notes |
|---|---|---|---|
| `account_session_token` | JWT (signed) | 15 minutes | Sent as `Authorization: Bearer` on every request |
| `refresh_token` | Opaque, one-time-use | 30 days | Rotated on each use; old token invalidated immediately |

- The CLI acquires both tokens via the **email OTP login flow** (`axme login`): no password, no API key copying — a one-time code is sent to the user's registered email.
- Tokens are stored in the OS-native keychain where available, or in a `~/.config/axme/secrets.json` (mode `0600`) on headless/server environments.
- The CLI **proactively refreshes** the access token when `exp − now < 60 seconds`, before the next API request. This avoids reactive 401 errors entirely in normal operation.
- If the refresh token expires (30 days of inactivity), the user re-authenticates via OTP — no password needed.

![Authentication and Authorization Enforcement Flow](https://raw.githubusercontent.com/AxmeAI/axme-docs/main/docs/diagrams/security/01-authn-authz-enforcement-flow.svg)

![Token Refresh Flow](https://raw.githubusercontent.com/AxmeAI/axme-docs/main/docs/diagrams/security/09-token-refresh-flow.svg)

For the full login and token lifecycle sequence, see [08-email-otp-login-and-token-refresh-flow](diagrams/security/08-email-otp-login-and-token-refresh-flow.mmd).

## 2) Secrets management

- Secrets are never intended to be committed to repositories or embedded in client applications.
- Runtime services load secrets from environment/config providers backed by managed secret stores.
- Key and secret rotation is supported operationally; expired or revoked credentials are rejected fail-closed.
- Access to secret material should follow least-privilege IAM policies and auditable access paths.
- CLI credentials (API key, access token, refresh token) are stored in the OS keychain or a `0600` file — never in plain `config.json`.

## 3) Encryption and transport

- Public ingress uses HTTPS/TLS.
- Internal service-to-service communication is isolated and authenticated.
- Data at rest is encrypted by managed infrastructure controls.
- Outbound callback/webhook channels use request signing so consumers can verify authenticity.

![Trust Boundary DFD](https://raw.githubusercontent.com/AxmeAI/axme-docs/main/docs/diagrams/security/03-trust-boundary-dfd.svg)

![Webhook Signature Verification](https://raw.githubusercontent.com/AxmeAI/axme-docs/main/docs/diagrams/security/05-webhook-signature-verification.svg)

## 4) Auditability and traceability

- Security-sensitive events (authentication, authorization, key lifecycle actions) are logged with timestamps and actor context.
- Intent and workflow lifecycle changes are recorded for post-incident analysis.
- Correlation identifiers are used to trace execution across API, runtime, and callback boundaries.

## 5) Tenant isolation and authorization boundaries

- Authorization is scoped by organization/workspace ownership boundaries.
- Role- and policy-based controls are evaluated before protected operations execute.
- Cross-tenant access is denied by default unless explicitly granted by policy.

## 6) Incident response and disclosure

- Security reports and responsible disclosure: [hello@axme.ai](mailto:hello@axme.ai)
- High-risk credential events should trigger immediate rotation/revocation workflows.
- Incident handling includes containment, impact analysis, remediation, and follow-up hardening.

## 7) Compliance posture

AXME is currently in Alpha. Formal attestations/certifications may not be complete yet. The public documentation provides a control-oriented technical baseline to support enterprise security reviews during Alpha evaluation.

---

## Security Diagrams

Trust boundary map - each enforcement point across the platform:

![Security Trust Boundary - DFD](diagrams/security/03-trust-boundary-dfd.svg)

Public-facing TLS terminates at the gateway. Internal service calls use mTLS. Data at rest is encrypted with AES-256-GCM. Webhook payloads carry HMAC-SHA256 signatures.

Authentication and authorization enforcement flow:

![Auth/Authz Enforcement](diagrams/security/01-authn-authz-enforcement-flow.svg)

API key verification -> JWT validation -> org/workspace scope check -> role-based access -> resource-level policy grant evaluation. All steps are audited.

## Related documentation

- [`public-api-auth.md`](public-api-auth.md) — full login flow, token semantics, session management endpoints
- [`supported-limits-and-error-model.md`](supported-limits-and-error-model.md)
- [`docs/diagrams/security/index.md`](diagrams/security/index.md) — all security diagrams
