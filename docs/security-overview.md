# Security Overview

This document describes the public security model for AXME and AXME Cloud.

> **Alpha status:** controls are active and documented, but the platform is still in Alpha and may evolve.

## 1) Authentication model

AXME uses a two-layer authentication model for public APIs:

- **Platform credential** via `x-api-key` (service/workspace identity).
- **Actor context** via `Authorization: Bearer <actor_token>` (user/session/delegated context).

Route classes are explicit:

- **Platform routes:** require `x-api-key`.
- **Platform + actor routes:** require both `x-api-key` and `Authorization`.
- **Interactive/session routes:** require `Authorization`.

Authentication failures return structured error codes (for example: `missing_platform_api_key`, `missing_actor_token`, `invalid_actor_scope`) to make integration debugging deterministic.

## 2) Secrets management

- Secrets are never intended to be committed to repositories or embedded in client applications.
- Runtime services load secrets from environment/config providers backed by managed secret stores.
- Key and secret rotation is supported operationally; expired or revoked credentials are rejected fail-closed.
- Access to secret material should follow least-privilege IAM policies and auditable access paths.

## 3) Encryption and transport

- Public ingress uses HTTPS/TLS.
- Internal service-to-service communication is isolated and authenticated.
- Data at rest is encrypted by managed infrastructure controls.
- Outbound callback/webhook channels use request signing so consumers can verify authenticity.

Related diagrams:

- [`docs/diagrams/security/03-trust-boundary-dfd.svg`](diagrams/security/03-trust-boundary-dfd.svg)
- [`docs/diagrams/security/05-webhook-signature-verification.svg`](diagrams/security/05-webhook-signature-verification.svg)

## 4) Auditability and traceability

- Security-sensitive events (authentication, authorization, key lifecycle actions) are logged with timestamps and actor context.
- Intent and workflow lifecycle changes are recorded for post-incident analysis.
- Correlation identifiers are used to trace execution across API, runtime, and callback boundaries.

## 5) Tenant isolation and authorization boundaries

- Authorization is scoped by organization/workspace ownership boundaries.
- Role- and policy-based controls are evaluated before protected operations execute.
- Cross-tenant access is denied by default unless explicitly granted by policy.

Related diagram:

- [`docs/diagrams/security/01-authn-authz-enforcement-flow.svg`](diagrams/security/01-authn-authz-enforcement-flow.svg)

## 6) Incident response and disclosure

- Security reports and responsible disclosure: [hello@axme.ai](mailto:hello@axme.ai)
- High-risk credential events should trigger immediate rotation/revocation workflows.
- Incident handling includes containment, impact analysis, remediation, and follow-up hardening.

## 7) Compliance posture

AXME is currently in Alpha. Formal attestations/certifications may not be complete yet. The public documentation provides a control-oriented technical baseline to support enterprise security reviews during Alpha evaluation.

---

## Related documentation

- [`public-api-auth.md`](public-api-auth.md)
- [`supported-limits-and-error-model.md`](supported-limits-and-error-model.md)
- [`docs/diagrams/security/index.md`](diagrams/security/index.md)
