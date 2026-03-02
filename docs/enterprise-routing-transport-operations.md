# Enterprise Routing and Transport Operations

This document captures Track F architecture alignment for naming/routing foundation (`F9`) and transport/operations readiness (`F10`, `F11`).

## Canonical Model

Four layers are treated independently:

1. `principal_id` (immutable subject)
2. alias (`max@ax`, `agent://<tenant>/<service>`)
3. transport projection (Matrix now, optional HTTP/Queue later)
4. endpoint routing metadata (route id, auth posture, placement, health)

## Runtime Baseline in Gateway

- Tenant placement metadata is resolved per request (`deployment_mode`, `cluster_id`, `region`).
- Intent submission writes routing metadata into lifecycle events and usage ledger.
- Usage events include transport and route attributes for later analytics and policy.
- Enterprise quota enforcement is performed before expensive write paths.

## Portal and Governance Surfaces

- Enterprise governance APIs (`organizations`, `workspaces`, `members`, `access_requests`, `quotas`, `usage`, `service_accounts`) are exposed on `/v1/*`.
- Portal backend-for-frontend endpoints:
  - `GET /v1/portal/enterprise/overview`
  - `GET /v1/portal/enterprise/access-requests`

## Transport Expansion Policy

- Matrix remains default managed transport.
- HTTP/Queue adapters remain optional and policy-gated.
- MCP is treated as integration protocol layer, not a routing-core transport identity.

## Observability and Replay Readiness

- Route and region metadata is persisted in `usage_ledger`.
- Daily rollups are available through `POST /v1/usage/rollups/daily`.
- Audit trail for enterprise admin actions is available via enterprise admin audit events.

## Operator Checklist

- Verify auth scope checks on all enterprise/portal endpoints.
- Validate quota policy behavior with hard block mode.
- Validate usage summary/timeseries consistency before billing/reporting workflows.
- Keep rollback-ready domain and WAF configs aligned with infra runbooks.
