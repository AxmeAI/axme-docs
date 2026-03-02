# Public API Families D6: Enterprise Governance (Sprint 1)

This guide publishes Sprint 1 Track F contract docs for:

- `organizations.*`
- `organizations.workspaces.*`
- `organizations.members.*`
- `access_requests.*`
- `quotas.*`
- `usage.summary.get`
- `usage.timeseries.get`

Use this guide with:

- `docs/openapi/gateway.track-f-sprint1.v1.json` (draft OpenAPI operation surface for Sprint 1)
- `axp-spec/schemas/public_api/*.json` (canonical schema contracts)
- `docs/public-api-auth.md`
- `docs/supported-limits-and-error-model.md`
- `docs/enterprise-runtime-model-and-placement.md`

## 1) OpenAPI Operation Publication

Sprint 1 operation publication for enterprise families is captured in:

- `docs/openapi/gateway.track-f-sprint1.v1.json`

Published operation groups:

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

## 2) Canonical Schema Contracts

Organizations and access requests:

- `axp-spec/schemas/public_api/api.organizations.create.request.v1.json`
- `axp-spec/schemas/public_api/api.organizations.create.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.get.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.update.request.v1.json`
- `axp-spec/schemas/public_api/api.organizations.update.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.workspaces.create.request.v1.json`
- `axp-spec/schemas/public_api/api.organizations.workspaces.create.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.workspaces.list.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.workspaces.update.request.v1.json`
- `axp-spec/schemas/public_api/api.organizations.workspaces.update.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.members.list.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.members.add.request.v1.json`
- `axp-spec/schemas/public_api/api.organizations.members.add.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.members.update.request.v1.json`
- `axp-spec/schemas/public_api/api.organizations.members.update.response.v1.json`
- `axp-spec/schemas/public_api/api.organizations.members.remove.response.v1.json`
- `axp-spec/schemas/public_api/api.access_requests.create.request.v1.json`
- `axp-spec/schemas/public_api/api.access_requests.create.response.v1.json`
- `axp-spec/schemas/public_api/api.access_requests.list.response.v1.json`
- `axp-spec/schemas/public_api/api.access_requests.get.response.v1.json`
- `axp-spec/schemas/public_api/api.access_requests.review.request.v1.json`
- `axp-spec/schemas/public_api/api.access_requests.review.response.v1.json`

Quotas and usage:

- `axp-spec/schemas/public_api/api.quotas.get.response.v1.json`
- `axp-spec/schemas/public_api/api.quotas.update.request.v1.json`
- `axp-spec/schemas/public_api/api.quotas.update.response.v1.json`
- `axp-spec/schemas/public_api/api.usage.summary.get.response.v1.json`
- `axp-spec/schemas/public_api/api.usage.timeseries.get.response.v1.json`

## 3) Permission and Scope Matrix (Sprint 1)

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

Permission matrix:

| Operation group | org_owner | org_admin | workspace_admin | member | billing_viewer | security_auditor |
| --- | --- | --- | --- | --- | --- | --- |
| organizations.create/get/update | allow | allow (get/update) | deny | deny | read-only get | read-only get |
| organizations.workspaces.create/list/update | allow | allow | allow (workspace scoped) | deny | read-only list | read-only list |
| organizations.members.list/add/update/remove | allow | allow | allow (workspace scoped) | deny | read-only list | read-only list |
| access_requests.review | allow | allow | deny | deny | deny | read-only list/get |
| quotas.update | allow | allow | deny | deny | deny | deny |
| quotas.get | allow | allow | allow | deny | allow | allow |
| usage.summary.get and usage.timeseries.get | allow | allow | allow | deny | allow | allow |

Notes:

- `member` role can create request-access records for elevated role or org join, but cannot mutate organization/member/quota records directly.
- Workspace-scoped actions require workspace membership binding in runtime policy checks.

## 4) Canonical Error Semantics (Sprint 1)

Error expectations for enterprise governance operations:

- `400 Bad Request`
  - malformed path/query/body combinations
  - scope mismatch between path and body (`org_id` / `workspace_id`)
- `401 Unauthorized`
  - missing or invalid API key
  - missing/invalid bearer token when route requires bearer
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

- Sprint 1 publishes additive contracts and OpenAPI operation docs only.
- Runtime rollout remains feature-flagged and can run in compatibility mode while scoped-credential migration is in progress.
