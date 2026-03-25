# axme-docs

Implementation documentation, security model, API references, and architecture diagrams for the AXME platform.

> **Alpha** - Protocol and API surface are stabilizing. Not recommended for production workloads yet.
> Install CLI, log in, run your first example in under 5 minutes. [Quick Start](https://cloud.axme.ai/alpha/cli) - [hello@axme.ai](mailto:hello@axme.ai)

---

## What Is AXME?

AXME is a coordination infrastructure for durable execution of long-running intents across distributed systems.

It provides a model for executing **intents** - requests that may take minutes, hours, or longer to complete - across services, agents, and human participants.

## AXP - the Intent Protocol

At the core of AXME is **AXP (Intent Protocol)** - an open protocol that defines contracts and lifecycle rules for intent processing.

AXP can be implemented independently.  
The open part of the platform includes:

- the protocol specification and schemas
- SDKs and CLI for integration
- conformance tests
- implementation and integration documentation

Without AXME Cloud runtime, these open components are still usable for protocol-compatible implementations and validation.

## AXME Cloud

**AXME Cloud** is the managed service that runs AXP in production together with **The Registry** (identity and routing).

It removes operational complexity by providing:

- reliable intent delivery and retries  
- lifecycle management for long-running operations  
- handling of timeouts, waits, reminders, and escalation  
- observability of intent status and execution history  

State and events can be accessed through:

- API and SDKs  
- event streams and webhooks  
- the cloud console

---

<details>
<summary>Full repository structure</summary>

```
axme-docs/
├── docs/
│   ├── diagrams/              # Full visualization program (SVG / PNG / DOT / MMD sources)
│   │   ├── intents/           # Intent lifecycle, policy, delivery, approvals
│   │   ├── platform/          # System context, container view, enterprise placement
│   │   ├── protocol/          # Protocol envelope, versioning, idempotency, transport
│   │   ├── api/               # API method families, error model, pagination, quotas
│   │   ├── security/          # Auth/authz, crypto, trust boundaries, threat model
│   │   ├── operations/        # Release, DR, SLOs, observability, runbooks
│   │   └── website/           # Diagrams for the public website / landing page
│   ├── openapi/               # OpenAPI artifacts for the public API surface
│   ├── connectors/            # Connector setup guides (HTTP, webhook, MCP)
│   ├── ADR-002-service-boundaries.md
│   ├── ADR-003-trust-consent-model.md
│   ├── axme-is-not-rpc.md
│   ├── B2B_FEATURES.md
│   ├── enterprise-routing-transport-operations.md
│   ├── enterprise-runtime-model-and-placement.md
│   ├── enterprise-scoped-credentials-migration-note.md
│   ├── examples-cloud-vs-protocol.md
│   ├── external-integrator-dry-run.md
│   ├── integration-quickstart.md
│   ├── mcp-api-reference.md            # MCP API reference - all 48 tools, auth, response format
│   ├── mcp-axme-continuation-pattern.md
│   ├── migration-and-deprecation-policy.md
│   ├── migration-message-centric-to-intent-lifecycle.md
│   ├── MVP_SCOPE.md
│   ├── public-api-auth.md
│   ├── public-api-families-d1-intents-inbox-approvals.md
│   ├── public-api-families-d2-webhooks-capabilities.md
│   ├── public-api-families-d3-users.md
│   ├── public-api-families-d4-invites-media.md
│   ├── public-api-families-d5-schemas.md
│   ├── public-api-families-d6-enterprise-governance.md
│   ├── security-overview.md
│   └── supported-limits-and-error-model.md
├── scripts/
│   └── validate_docs.py
└── tests/
```

</details>

---

## Platform Overview

The diagram below shows how AXME components relate: the public gateway, control plane services, connectors, and client SDKs.

![AXME System Context - C4 Level 1](docs/diagrams/platform/01-system-context-c4.svg)

*The gateway is the single public entry point. Intents flow from SDK clients through TLS to the gateway, which routes them into the durable scheduler and connector layer. Webhooks and MCP callbacks leave the platform from the connector side, cryptographically signed.*

---

## Intent Lifecycle

Every intent progresses through a well-defined state machine. The diagram below shows all states, transitions, and terminal outcomes.

![Intent Lifecycle State Machine](docs/diagrams/intents/01-intent-lifecycle-state-machine.svg)

*Key states: `PENDING → PROCESSING → WAITING_* → DELIVERED → RESOLVED`. Any intent can be cancelled or expire at most transition points. Retry loops are bounded by the policy envelope.*

The complete runtime container view - services, databases, queues, and their connections:

![Container Runtime - C4 Level 2](docs/diagrams/platform/02-container-runtime-c4.svg)

*Gateway (public REST API), agent-core (workflow engine), auth service, MCP platform (48 JSON-RPC tools), and tool registry run as Cloud Run services sharing a PostgreSQL instance. The scheduler runs on the gateway via internal tick endpoints.*

---

## Integration Quickstart

1. **Install the CLI and run your first example**: https://cloud.axme.ai/alpha/cli
2. Choose your SDK: [Python](https://github.com/AxmeAI/axme-sdk-python) · [TypeScript](https://github.com/AxmeAI/axme-sdk-typescript) · [Go](https://github.com/AxmeAI/axme-sdk-go) · [Java](https://github.com/AxmeAI/axme-sdk-java) · [.NET](https://github.com/AxmeAI/axme-sdk-dotnet)
3. Follow `docs/integration-quickstart.md` for the full onboarding path
4. Example hubs:
   - Cloud runnable: [axme-examples/examples](https://github.com/AxmeAI/axme-examples/tree/main/examples)
   - Protocol-only: [axme-examples/protocol](https://github.com/AxmeAI/axme-examples/tree/main/protocol)

---

## Key Documents

| Document | Description |
|---|---|
| [`integration-quickstart.md`](docs/integration-quickstart.md) | End-to-end onboarding path for new integrators |
| [`public-api-auth.md`](docs/public-api-auth.md) | Authentication: platform API keys, actor tokens, JWT validation |
| [`security-overview.md`](docs/security-overview.md) | Security architecture, controls, and enterprise review baseline |
| [`supported-limits-and-error-model.md`](docs/supported-limits-and-error-model.md) | Rate limits, quotas, error codes, retriability table |
| [`migration-and-deprecation-policy.md`](docs/migration-and-deprecation-policy.md) | API versioning, deprecation timelines, migration guides |
| [`mcp-api-reference.md`](docs/mcp-api-reference.md) | MCP Server - all 48 tools, auth model, response format |
| [`cross-org-receive-policy.md`](docs/cross-org-receive-policy.md) | Cross-org intent delivery: org policy + agent overrides |
| [`agent-addressing.md`](docs/agent-addressing.md) | Agent address registry, agent:// URI scheme |

### API Family References

| Document | Scope |
|---|---|
| [`D1 - Intents, Inbox, Approvals`](docs/public-api-families-d1-intents-inbox-approvals.md) | Intent CRUD, SSE, lifecycle events, human tasks |
| [`D2 - Webhooks, Capabilities`](docs/public-api-families-d2-webhooks-capabilities.md) | Webhook subscriptions, deliveries, event types |
| [`D3 - Users`](docs/public-api-families-d3-users.md) | User profiles, nicks, contacts |
| [`D4 - Invites, Media`](docs/public-api-families-d4-invites-media.md) | Invite links, media upload/download |
| [`D5 - Schemas`](docs/public-api-families-d5-schemas.md) | Schema governance, payload validation |
| [`D6 - Enterprise Governance`](docs/public-api-families-d6-enterprise-governance.md) | Orgs, workspaces, members, agents, policies, quotas |

---

## Protocol

AXP wraps every intent in a signed envelope. The protocol layer ensures integrity, ordering, and schema version negotiation.

![AXP Protocol Envelope](docs/diagrams/protocol/01-protocol-envelope.svg)

*The envelope carries the intent payload, sender identity, schema version, idempotency key, and a gateway-applied HMAC signature. Recipients verify the signature before processing.*

Idempotency and replay protection are first-class protocol features:

![Idempotency and Replay Protection](docs/diagrams/protocol/03-idempotency-and-replay-protection.svg)

*Duplicate requests bearing the same idempotency key return the cached response without re-executing. Replay attacks are rejected by the nonce registry.*

---

## Security Model

The platform enforces layered security boundaries. The trust boundary diagram maps each enforcement point:

![Security Trust Boundary - DFD](docs/diagrams/security/03-trust-boundary-dfd.svg)

*Public-facing TLS terminates at the gateway. Internal service calls use mTLS. Data at rest is encrypted with AES-256-GCM. Webhook payloads carry HMAC-SHA256 signatures.*

Security control baseline for enterprise review: [`docs/security-overview.md`](docs/security-overview.md).

Authentication and authorization enforcement flow:

![Auth/Authz Enforcement](docs/diagrams/security/01-authn-authz-enforcement-flow.svg)

*API key verification → JWT validation → org/workspace scope check → role-based access → resource-level policy grant evaluation. All steps are audited.*

---

<details>
<summary>Visualization program</summary>

The `docs/diagrams/` directory is the canonical home for all platform visualizations. Each diagram is available in four formats: `.mmd` (Mermaid source), `.dot` (Graphviz source), `.svg` (rendered vector), and `.png` (raster).

- **[Visualization Backlog & Status](docs/diagrams/VISUALIZATION_BACKLOG.md)** - P0 / P1 / P2 diagram inventory
- **[Diagram Usage Matrix](docs/diagrams/DIAGRAM_USAGE_MATRIX.md)** - which diagrams appear in which repositories
- **[Repository Distribution Plan](docs/diagrams/REPO_DISTRIBUTION_PLAN.md)** - placement strategy

</details>

---

## Related Repositories

| Repository | Role |
|---|---|
| [axme-spec](https://github.com/AxmeAI/axme-spec) | Canonical schema and protocol contracts |
| Control-plane runtime (private) | Internal runtime implementation |
| [axme-conformance](https://github.com/AxmeAI/axme-conformance) | Conformance and contract test suite |
| [axme-sdk-python](https://github.com/AxmeAI/axme-sdk-python) | Python SDK |
| [axme-sdk-typescript](https://github.com/AxmeAI/axme-sdk-typescript) | TypeScript SDK |
| [axme-sdk-go](https://github.com/AxmeAI/axme-sdk-go) | Go SDK |
| [axme-sdk-java](https://github.com/AxmeAI/axme-sdk-java) | Java SDK |
| [axme-sdk-dotnet](https://github.com/AxmeAI/axme-sdk-dotnet) | .NET SDK |
| [axme-cli](https://github.com/AxmeAI/axme-cli) | Command-line interface |

---

## Contributing & Contact

- Bug reports and docs feedback: open an issue in this repository
- Quick Start: https://cloud.axme.ai/alpha/cli - Contact: [hello@axme.ai](mailto:hello@axme.ai)
- Security disclosures: see [SECURITY.md](SECURITY.md)
- Contribution guidelines: [CONTRIBUTING.md](CONTRIBUTING.md)

<details>
<summary>Validate this documentation repo locally</summary>

```bash
python -m pip install -e ".[dev]"
python scripts/validate_docs.py
pytest
```

</details>
