# Diagram Usage Matrix (All Repositories)

This matrix ensures every generated visualization is used at least once in repository documentation.

Legend:
- `primary_repo`: repository that must embed the diagram directly in its README/docs.
- `secondary_repo`: optional additional repository that can reuse the same diagram.

## Intents

| diagram | primary_repo | secondary_repo |
| --- | --- | --- |
| `intents/01-intent-lifecycle-state-machine.svg` | `axme-control-plane` | `axme-examples` |
| `intents/02-create-and-control-sequence.svg` | `axme-cli` | `axme-sdk-python` |
| `intents/03-policy-anatomy.svg` | `axme-control-plane` | `axme-spec` |
| `intents/04-waiting-branches-and-wakeups.svg` | `axme-control-plane` | `axme-conformance` |
| `intents/05-delivery-and-processing-pipeline.svg` | `axme-control-plane` | `axme-infra` |
| `intents/06-internal-scheduler-loop.svg` | `axme-control-plane` | `axme-infra` |
| `intents/07-access-control-matrix.svg` | `axme-security-ops` | `axme-control-plane` |
| `intents/08-audit-trail-map.svg` | `axme-conformance` | `axme-security-ops` |
| `intents/09-intent-payload-extensibility-and-semantic-schemas.svg` | `axme-spec` | `axme-docs` |
| `intents/10-human-in-loop-approval-branches.svg` | `axme-reference-clients` | `axme-mobile` |
| `intents/11-resume-controls-policy-conflict-resolution.svg` | `axme-conformance` | `axme-reference-clients` |

## Platform

| diagram | primary_repo | secondary_repo |
| --- | --- | --- |
| `platform/01-system-context-c4.svg` | `axme-docs` | `axme-cloud-landing` |
| `platform/02-container-runtime-c4.svg` | `axme-control-plane` | `axme-infra` |
| `platform/03-enterprise-placement-and-boundaries.svg` | `axme-docs` | `axme-reference-clients` |
| `platform/04-conformance-traceability-map.svg` | `axme-conformance` | `axme-spec` |

## API

| diagram | primary_repo | secondary_repo |
| --- | --- | --- |
| `api/01-api-method-family-map.svg` | `axme-sdk-typescript` | `axme-sdk-python` |
| `api/02-error-model-retriability.svg` | `axme-sdk-go` | `axme-sdk-dotnet` |
| `api/03-pagination-filtering-sorting-patterns.svg` | `axme-sdk-java` | `axme-sdk-dotnet` |
| `api/04-rate-limit-and-quota-model.svg` | `axme-cli` | `axme-spec` |

## Protocol

| diagram | primary_repo | secondary_repo |
| --- | --- | --- |
| `protocol/01-protocol-envelope.svg` | `axme-spec` | `axme-sdk-typescript` |
| `protocol/02-versioning-and-deprecation-flow.svg` | `axme-spec` | `axme-docs` |
| `protocol/03-idempotency-and-replay-protection.svg` | `axme-sdk-python` | `axme-sdk-typescript` |
| `protocol/04-schema-governance-compatibility.svg` | `axme-spec` | `axme-conformance` |
| `protocol/05-transport-selection-and-fallbacks.svg` | `axme-examples` | `axme-docs` |

## Security

| diagram | primary_repo | secondary_repo |
| --- | --- | --- |
| `security/01-authn-authz-enforcement-flow.svg` | `axme-security-ops` | `axme-control-plane` |
| `security/02-crypto-key-lifecycle.svg` | `axme-security-ops` | `axme-infra` |
| `security/03-trust-boundary-dfd.svg` | `axme-security-ops` | `axme-docs` |
| `security/04-secrets-management-rotation-flow.svg` | `axme-security-ops` | `axme-infra` |
| `security/05-webhook-signature-verification.svg` | `axme-control-plane` | `axme-spec` |
| `security/06-threat-model-stride-map.svg` | `axme-local-internal` | `axme-security-ops` |
| `security/07-data-classification-and-encryption-zones.svg` | `axme-security-ops` | `axme-docs` |

## Operations

| diagram | primary_repo | secondary_repo |
| --- | --- | --- |
| `operations/01-release-and-rollback-flow.svg` | `axme-infra` | `axme-security-ops` |
| `operations/02-dr-backup-restore-flow.svg` | `axme-infra` | `axme-security-ops` |
| `operations/03-observability-slos-alerts.svg` | `axme-control-plane` | `axme-examples` |
| `operations/04-capacity-latency-budget.svg` | `axme-cli` | `axme-control-plane` |
| `operations/05-incident-response-swimlane.svg` | `axme-security-ops` | `axme-reference-clients` |
| `operations/06-runbook-decision-tree-top-incidents.svg` | `axme-local-internal` | `axme-infra` |
| `operations/07-change-management-and-gates.svg` | `axme-infra` | `axme-local-internal` |

## Website / Interactive

| asset | primary_repo | secondary_repo |
| --- | --- | --- |
| `website/01-interactive-intent-journey.html` | `axme-cloud-landing` | `axme-docs` |

