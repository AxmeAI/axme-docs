# Enterprise Scoped Credentials Migration Note (F0.3)

## Purpose

This note defines the Sprint 1 migration path for enterprise integrators moving from deployment-wide shared key posture to scoped credentials.

Scope:

- gateway auth hardening defaults for production profiles
- controlled account bootstrap posture
- scoped-credential transition flags and compatibility window behavior

## Operational Defaults by Profile

Production fail-closed defaults:

- `AXME_DEPLOYMENT_PROFILE=production`
- `GATEWAY_REQUIRE_BEARER_AUTH=true` (default in production profile)
- `GATEWAY_ENFORCE_INBOX_OWNER_SCOPE=true` (default in production profile)
- `GATEWAY_ALLOW_UNCONTROLLED_ACCOUNT_BOOTSTRAP=false` (default in production profile)

Non-production defaults remain compatibility-oriented unless explicitly hardened:

- bearer auth and strict owner scope stay opt-in
- uncontrolled bootstrap remains enabled by default

## Internal Caller Posture Checks (Gateway-Adjacent Services)

Internal services that call gateway enterprise routes (for example `mcp-server`) must follow the same shared-key migration posture:

- production profile is fail-closed:
  - `AXME_DEPLOYMENT_PROFILE=production`
  - `GATEWAY_API_KEY` must be explicitly configured (startup fails if missing)
- non-production profile may use `dev-gateway-key` default only for local/dev flows.

Operational verification:

- check `GET /health` on `mcp-server`:
  - `deployment_profile`
  - `gateway_api_key_source` (`explicit` or `dev_default`)
  - `gateway_shared_key_default_active` (must be `false` for staging/production)

## Scoped Credential Transition Flags

Runtime feature controls:

- `AXME_FEATURE_SCOPED_CREDENTIALS`
  - `false` (default): scoped claim checks are disabled
  - `true`: scoped claim checks are active
- `AXME_SCOPED_CREDENTIALS_ALLOW_LEGACY_OWNER`
  - `true` (default): compatibility mode, legacy owner-claim tokens still accepted
  - `false`: strict mode, tokens must include scoped claims

Required scoped claims in strict mode:

- `org_id`
- `workspace_id`
- `actor_id` (or equivalent identity claim used by runtime policy)
- `roles`

## Compatibility Window Behavior

### Phase 0 (legacy baseline)

- `AXME_FEATURE_SCOPED_CREDENTIALS=false`
- Integrations may continue using owner-claim bearer flows without scoped claim assertions.

### Phase 1 (compatibility transition)

- `AXME_FEATURE_SCOPED_CREDENTIALS=true`
- `AXME_SCOPED_CREDENTIALS_ALLOW_LEGACY_OWNER=true`
- Integrators should begin issuing scoped claims while legacy owner-claim flows continue to work.

### Phase 2 (strict scoped credentials)

- `AXME_FEATURE_SCOPED_CREDENTIALS=true`
- `AXME_SCOPED_CREDENTIALS_ALLOW_LEGACY_OWNER=false`
- Legacy owner-only tokens are rejected; scoped claim set is mandatory.

## Integrator Action Checklist

1. Ensure actor token issuance pipeline can mint `org_id`, `workspace_id`, and role claims.
2. Roll out scoped claims to sandbox and staging while in Phase 1 compatibility mode.
3. Validate authorization outcomes for all enterprise admin paths before switching to strict mode.
4. Disable uncontrolled bootstrap in production and route onboarding through access-request flow.
5. Record fallback procedure to temporarily return to compatibility mode if migration defects are detected.

## Rollback Guidance

If strict mode causes production impact:

- set `AXME_SCOPED_CREDENTIALS_ALLOW_LEGACY_OWNER=true`
- keep `AXME_FEATURE_SCOPED_CREDENTIALS=true` so scoped claims continue to be evaluated where present
- investigate claim-shaping gaps and re-run migration validation before returning to strict mode

## References

- `docs/public-api-auth.md`
- `docs/supported-limits-and-error-model.md`
- `docs/public-api-families-d6-enterprise-governance.md`
- `docs/migration-and-deprecation-policy.md`
