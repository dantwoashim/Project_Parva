---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Production Deployment Guardrails

Every internet-facing process uses `PARVA_EXPOSURE=internet`. The `public`,
`staging`, and `production` environments select that exposure automatically and
cannot downgrade it.

## Required For Internet Exposure

- `PARVA_ENV=public`, `PARVA_ENV=staging`, or `PARVA_ENV=production`.
- `PARVA_EXPOSURE=internet`.
- `PARVA_SOURCE_URL` pointing to the corresponding published source.
- `PARVA_ROUTE_PROFILE` set to a public/deployed-safe profile such as
  `public_reference`, `public_demo`, `minimal_public`, `developer_preview`, or
  `enterprise_preview`.
- `PARVA_RATE_LIMIT_BACKEND=redis` and `PARVA_REDIS_URL` for shared enforcement.
- A one-process public demo may use `PARVA_RATE_LIMIT_BACKEND=memory` only with
  `PARVA_SINGLE_PROCESS_RATE_LIMIT=true` and a bounded
  `PARVA_RATE_LIMIT_MAX_BUCKETS` value.
- `PARVA_PROVENANCE_ATTESTATION_KEY` or
  `PARVA_PROVENANCE_ATTESTATION_KEY_FILE`.
- `PARVA_REQUIRE_SIGNED_PROVENANCE_MUTATIONS=true`.
- `PARVA_ADMIN_TOKEN` when admin, billing, experimental, or mutation surfaces
  are mounted.
- `PARVA_BILLING_ENABLED=true` deployments must use a Postgres
  `PARVA_DATABASE_URL` and a non-default `PARVA_API_KEY_PEPPER`.
- `PARVA_TRUSTED_PROXY_IPS` must name exact trusted proxies; `*` is rejected.
- CORS origins must be explicit and cannot include localhost.

## Rejected For Internet Exposure

- `PARVA_DEBUG=true`.
- Process-local rate limiting without `PARVA_SINGLE_PROCESS_RATE_LIMIT=true`.
- Route profiles `research_private`, `internal_lab`, `full`, or `full_dev`.
- Unsigned provenance mutation mode.
- SQLite billing storage when billing is enabled.
- Missing source URL.
- Default local API-key pepper.

## Preflight

`make preflight-production` runs the production preflight with a public reference
route profile, Redis rate-limit settings, signed provenance mutation mode, and
offline place-search settings. The command is intended as a config validation
gate, not as a deploy substitute.

## CI Security Scanning

CI blocks on the repository secret scan, Python dependency audit, frontend npm
audit, and JavaScript SDK npm audit.

- Python dependencies: `python -m pip_audit --strict`.
- Frontend dependencies: `npm --prefix frontend audit --audit-level=high`.
- JavaScript SDK dependencies:
  `npm --prefix packages/parva-js audit --audit-level=high`.

Local dependency audits require access to the PyPI and npm advisory endpoints.
If the local environment blocks outbound advisory traffic, treat the local
result as an environment blocker and rely on the CI gate for network-backed
advisory resolution.
