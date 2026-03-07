# Cloud vs Protocol Examples

AXME follows an **open protocol + managed runtime** model.

- **AXP protocol is open**: you can implement compatible services and runtimes yourself.
- **AXME Cloud runtime is managed**: durable orchestration features are provided by AXME Cloud.

## What works without AXME Cloud

You can still use:

- AXP protocol spec (`axme-spec`)
- SDKs as protocol/client helpers
- CLI for contract-level checks and endpoint testing
- conformance suite (`axme-conformance`) for compatibility validation

## What requires AXME Cloud

Managed execution features:

- durable orchestration runtime
- lifecycle scheduling and progression
- retries/backoff orchestration
- managed callback coordination
- cloud runtime observability and registry routing

## Example hubs

- **Cloud runnable examples**: [axme-examples/cloud](https://github.com/AxmeAI/axme-examples/tree/main/cloud)
- **Protocol-only examples**: [axme-examples/protocol](https://github.com/AxmeAI/axme-examples/tree/main/protocol)

Use cloud examples for product onboarding. Use protocol examples for AXP-only integration and custom runtime compatibility.
