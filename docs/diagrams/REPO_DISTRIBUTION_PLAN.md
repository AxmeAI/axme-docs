# Diagram Distribution Plan By Repository

Use `axme-docs/docs/diagrams` as canonical staging.
During README rollout, copy required `.svg` assets into each repository under `docs/diagrams/`.

Reference matrix:
- `axme-docs/docs/diagrams/DIAGRAM_USAGE_MATRIX.md`

## Repository targeting (18 repos)

### Core docs and protocol

- `axme-docs`
  - canonical source and catalog for all diagram packs.
- `axme-spec`
  - protocol and API diagrams (envelope/versioning/idempotency/error/compatibility).

### Runtime and reliability

- `axme-control-plane`
  - intent lifecycle, controls/policy, scheduler, runtime container, delivery/security flow.
- `axme-infra`
  - release/rollback, DR, runbooks, capacity and infra-oriented operational diagrams.
- `axme-security-ops`
  - authn/authz, trust boundaries, crypto lifecycle, secrets, threat and incident diagrams.
- `axme-conformance`
  - conformance traceability, audit and control-conflict verification diagrams.

### CLI and SDKs

- `axme-cli`
  - control-sequence, quota/rate-limit, operator workflows.
- `axme-sdk-python`
  - API method map + idempotency/retry usage.
- `axme-sdk-typescript`
  - API method map + protocol envelope + idempotency.
- `axme-sdk-go`
  - API method map + retriable error model.
- `axme-sdk-java`
  - pagination/filtering/sorting + API method map.
- `axme-sdk-dotnet`
  - retriable error model + pagination/rate-limit references.

### Product surface and adoption repos

- `axme-cloud-landing`
  - system-context and interactive journey visual.
- `axme-reference-clients`
  - human-in-loop and enterprise workflow visuals.
- `axme-mobile`
  - human-in-loop / inbox-control path visuals.
- `axme-examples`
  - intent lifecycle + transport fallback + observability visuals.

### Internal/historical

- `axme-local-internal`
  - internal planning visuals (threat/runbook/change gates).
- `axme`
  - historical pointer-only references, no heavy active diagram maintenance.

## Promotion checklist

- Diagram names and statuses match current OpenAPI/runtime behavior.
- Per-repo copies use `docs/diagrams/*.svg` with relative links from README.
- `axme-docs/docs/diagrams` remains canonical source (`.mmd`, `.dot`, `.svg`, `.png`).
- Every diagram has at least one primary README/docs usage (tracked by matrix).
