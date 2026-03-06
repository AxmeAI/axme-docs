# Public API Families D6: Enterprise Governance and Routing

This guide documents the enterprise governance and routing surface published after the core D1-D5 family batches.

Families covered:

- `organizations.*`
- `organizations.workspaces.*`
- `organizations.members.*`
- `access_requests.*`
- `quotas.*`
- `usage.summary.get`
- `usage.timeseries.get`
- `usage.rollups.daily` (OpenAPI-exposed operational surface; schema disposition note below)
- `billing.plan.*`
- `billing.invoices.*`
- `service_accounts.*`
- `service_accounts.keys.*`
- `portal.enterprise.*` (OpenAPI-exposed BFF operational surface; schema disposition note below)
- `portal.personal.*` (OpenAPI-exposed BFF operational surface; schema disposition note below)
- `principals.*`
- `aliases.*`
- `routing.*`
- `transports.bindings.*`
- `deliveries.*`

Use this guide with:

- `docs/openapi/gateway.v1.json` (current canonical public operation surface)
- `docs/openapi/gateway.track-f-sprint1.v1.json` (historical phased snapshot)
- `axp-spec/schemas/public_api/*.json` (canonical schema contracts; current repository path remains `axme-spec` during transition)
- `axp-spec/docs/public-api-schema-index.md` (schema-to-operation mapping; current repository path remains `axme-spec` during transition)
- `docs/public-api-auth.md`
- `docs/supported-limits-and-error-model.md`
- `docs/enterprise-runtime-model-and-placement.md`

## 1) OpenAPI Operation Publication

Enterprise operation groups currently published on `gateway.v1.json`:

- organization lifecycle:
  - `POST /v1/organizations`
  - `GET /v1/organizations/{org_id}`
  - `PATCH /v1/organizations/{org_id}`
- workspace lifecycle:
  - `POST /v1/organizations/{org_id}/workspaces`
  - `GET /v1/organizations/{org_id}/workspaces`
  - `PATCH /v1/organizations/{org_id}/workspaces/{workspace_id}`
- member lifecycle:
  - `GET /v1/organizations/{org_id}/members`
  - `POST /v1/organizations/{org_id}/members`
  - `PATCH /v1/organizations/{org_id}/members/{member_id}`
  - `DELETE /v1/organizations/{org_id}/members/{member_id}`
- request access:
  - `POST /v1/access-requests`
  - `GET /v1/access-requests`
  - `GET /v1/access-requests/{access_request_id}`
  - `POST /v1/access-requests/{access_request_id}/review`
- quota and usage:
  - `GET /v1/quotas`
  - `PATCH /v1/quotas`
  - `GET /v1/usage/summary`
  - `GET /v1/usage/timeseries`
  - `POST /v1/usage/rollups/daily`
- billing:
  - `PATCH /v1/billing/plan`
  - `GET /v1/billing/plan`
  - `GET /v1/billing/invoices`
  - `GET /v1/billing/invoices/{invoice_id}`
- service accounts:
  - `POST /v1/service-accounts`
  - `GET /v1/service-accounts`
  - `GET /v1/service-accounts/{service_account_id}`
  - `POST /v1/service-accounts/{service_account_id}/keys`
  - `POST /v1/service-accounts/{service_account_id}/keys/{key_id}/revoke`
- naming/routing/transports/deliveries:
  - `POST /v1/principals`
  - `GET /v1/principals/{principal_id}`
  - `POST /v1/aliases`
  - `GET /v1/aliases`
  - `POST /v1/aliases/{alias_id}/revoke`
  - `GET /v1/aliases/resolve`
  - `POST /v1/routing/endpoints`
  - `GET /v1/routing/endpoints`
  - `PATCH /v1/routing/endpoints/{route_id}`
  - `DELETE /v1/routing/endpoints/{route_id}`
  - `POST /v1/routing/resolve`
  - `POST /v1/transports/bindings`
  - `GET /v1/transports/bindings`
  - `DELETE /v1/transports/bindings/{binding_id}`
  - `POST /v1/deliveries`
  - `GET /v1/deliveries`
  - `GET /v1/deliveries-operations`
  - `GET /v1/deliveries/{delivery_id}`
  - `POST /v1/deliveries/reconcile`
  - `POST /v1/deliveries/{delivery_id}/replay`
- portal backend-for-frontend:
  - `GET /v1/portal/enterprise/navigation`
  - `GET /v1/portal/enterprise/overview`
  - `GET /v1/portal/enterprise/access-requests`
  - `GET /v1/portal/enterprise/request-queue`
  - `GET /v1/portal/personal/overview`

## 2) Canonical Schema Contracts

Canonical schema files for these families are published in:

- `axp-spec/schemas/public_api/` (current repository path remains `axme-spec` during transition)
- `axp-spec/docs/public-api-schema-index.md` (authoritative mapping by operation; current repository path remains `axme-spec` during transition)

Primary schema groups in this batch:

- organizations/access:
  - `api.organizations.*`
  - `api.access_requests.*`
- quotas/usage/billing:
  - `api.quotas.*`
  - `api.usage.summary.get.*`
  - `api.usage.timeseries.get.*`
  - `api.billing.*`
- service accounts:
  - `api.service_accounts.*`
  - `api.service_accounts.keys.*`
- naming/routing/delivery:
  - `api.principals.*`
  - `api.aliases.*`
  - `api.routing.*`
  - `api.transports.bindings.*`
  - `api.deliveries.*`

Schema disposition notes:

- `POST /v1/usage/rollups/daily`, `GET /v1/portal/enterprise/*`, and `GET /v1/portal/personal/*` are currently OpenAPI-exposed operational surfaces.
- `GET /v1/deliveries-operations` and `POST /v1/deliveries/reconcile` are currently OpenAPI-exposed delivery operations surfaces.
- As of this snapshot, there are no dedicated `axp-spec/schemas/public_api/api.usage.rollups.daily.*`, `api.portal.enterprise.*`, `api.portal.personal.*`, or `api.deliveries.operations.*` files.
- These surfaces require explicit disposition in parity tracking:
  - either add canonical `public_api` schema artifacts,
  - or document them as gateway-operational endpoints outside canonical `public_api` family scope.

## 3) Permission and Scope Matrix

Tenant scope context:

- `org_id`
- `workspace_id`
- `actor_id`

Role set:

- `org_owner`
- `org_admin`
- `workspace_admin`
- `member`
- `billing_viewer`
- `security_auditor`

| Operation group | org_owner | org_admin | workspace_admin | member | billing_viewer | security_auditor |
| --- | --- | --- | --- | --- | --- | --- |
| organizations.create/get/update | allow | allow (get/update) | deny | deny | read-only get | read-only get |
| organizations.workspaces.create/list/update | allow | allow | allow (workspace scoped) | deny | read-only list | read-only list |
| organizations.members.list/add/update/remove | allow | allow | allow (workspace scoped) | deny | read-only list | read-only list |
| access_requests.review | allow | allow | deny | deny | deny | read-only list/get |
| quotas.update | allow | allow | deny | deny | deny | deny |
| quotas.get | allow | allow | allow | deny | allow | allow |
| usage.summary.get and usage.timeseries.get | allow | allow | allow | deny | allow | allow |
| usage.rollups.daily | allow | allow | allow | deny | deny | deny |
| billing.plan.update | allow | allow | allow | deny | deny | deny |
| billing.plan.get and billing.invoices.list/get | allow | allow | allow | deny | allow | allow |
| service_accounts.create/get/list and service_accounts.keys.* | allow | allow | allow | deny | read-only list/get | read-only list/get |
| portal.enterprise.navigation/overview/access-requests/request-queue | allow | allow | allow | deny | allow (except request-queue) | allow |
| portal.personal.overview | allow | allow | allow | allow | allow | allow |

Notes:

- `member` can create request-access records for elevated role or org join, but cannot mutate governance resources directly.
- Workspace-scoped actions require workspace membership binding in runtime policy checks.

## 4) Canonical Error Semantics

Error expectations for enterprise governance operations:

- `400 Bad Request`
  - malformed path/query/body combinations
  - scope mismatch between path and body (`org_id` / `workspace_id`)
- `401 Unauthorized`
  - missing or invalid API key
  - missing/invalid actor token when route requires actor context
- `403 Forbidden`
  - caller role cannot perform operation for requested scope
  - actor attempts cross-organization access
- `404 Not Found`
  - unknown `org_id`, `workspace_id`, `member_id`, or `access_request_id`
- `409 Conflict`
  - duplicate membership
  - concurrent conflicting updates
  - invalid state transitions in access-request review
- `422 Unprocessable Entity`
  - request payload fails contract validation
- `429 Too Many Requests`
  - caller exceeded configured rate limits

## 5) Compatibility Notes

- Enterprise routes are additive and remain feature-flagged by deployment profile.
- Runtime rollout can operate in compatibility mode during scoped-credential migration.
- Contract changes for these families must keep:
  - idempotency guidance,
  - trace propagation expectations,
  - auditable role/scope error behavior.
