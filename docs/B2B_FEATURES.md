# Axme B2B Features

This document defines the B2B offering for Axme as a managed infrastructure platform.
It answers one question: **what a B2B customer gets when integrating with Axme**.

## 1) Product Scope for B2B

Axme B2B is built on AXP, the Intent Protocol (durable execution layer), and provides infrastructure capabilities for production operations:

- identity and addressing (`@ax`);
- message transport and inbox storage;
- partner integrations via API/MCP;
- security, policy, and audit controls for production usage.

Customers consume Axme as a hosted service. Core server code remains private and operated by Axme.

## 2) Workspace and Tenant Model

B2B customers get:

- `org/workspace` model for multi-team operations;
- organization admins and role-based access controls (RBAC);
- service accounts for machine-to-machine integrations;
- environment separation (`sandbox`, `staging`, `production`) per customer.

## 3) Identity and Addressing

B2B customers get:

- globally resolvable Axme addresses under `@ax` namespace;
- nick registration and validation APIs;
- owner-scoped identity model (`owner_agent`) for secure routing;
- optional service-agent identities without phone-based onboarding.

## 4) Transport and Inbox Capabilities

B2B customers get:

- message send/receive APIs (`send`, `list inbox`, `get thread`, `reply`);
- delivery lifecycle with thread status transitions;
- idempotency support for write operations;
- durable inbox and thread history persistence.

## 5) Event Delivery

B2B customers get:

- webhook subscriptions for inbox and lifecycle events;
- signed webhook payloads (HMAC) with anti-replay protections;
- `at-least-once` event delivery with retries and dead-letter strategy;
- event replay support for missed deliveries;
- cursor-based sync fallback (`/inbox/changes`) for resilient clients.

## 6) Integrations and Interoperability

B2B customers get:

- MCP-compatible integration path for AI assistants and agent tools;
- OAuth-based linking flow for user-delegated access;
- integration runbooks for major assistant channels (for example ChatGPT, Gemini, Siri bridge);
- versioned public contracts (schemas + API docs) for stable partner integration.

## 7) Security and Access Controls

B2B customers get:

- strict owner isolation across data access and tool calls;
- JWT/JWKS validation with fail-closed policy;
- session lifecycle controls (refresh rotation, revoke session, revoke all);
- deterministic auth and authorization error behavior (`401/403`);
- rate limiting on auth and tool/API layers.

## 8) Audit and Observability

B2B customers get:

- request traceability (`trace_id`, `request_id`, `session_id`);
- audit events for auth, access, and tool execution outcomes;
- credential-safe logging (tokens/keys redacted);
- operational runbooks for smoke, rollout, and incident response.

## 9) Data and Storage Controls

B2B customers get:

- durable storage for profiles, threads, and message metadata;
- media support via object storage and signed URLs;
- backup/restore operating model;
- retention controls for messages, events, and audit data.

## 10) Commercial and Governance Features

B2B customers get:

- workspace-level billing model (per account/seat and/or usage-based options);
- business identity verification path (for example verified domain);
- plan-based limits and feature gates;
- contract and policy surface suitable for enterprise procurement.

## 11) Optional Enterprise Add-ons

Depending on plan, Axme can provide:

- advanced RBAC and delegated admin workflows;
- compliance-focused audit export;
- custom retention and data residency options;
- higher SLA and priority support;
- dedicated onboarding and architecture review.

## 12) What Is Not Included in B2B Core by Default

- source code access to Axme core services;
- customer self-hosting of Axme control plane;
- unrestricted namespace control outside Axme policies;
- custom protocol forks that break Axme compatibility guarantees.

## 13) B2B Value Proposition

Axme B2B gives partners a production-ready intent execution and coordination layer without building identity, transport, addressing, delivery guarantees, and security controls from scratch.
