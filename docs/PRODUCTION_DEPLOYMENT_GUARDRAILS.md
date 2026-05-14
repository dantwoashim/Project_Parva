---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Production Deployment Guardrails

Production and staging are treated as deployed environments. They must provide
explicit security configuration instead of inheriting local/demo defaults.

## Required In Production/Staging

- `PARVA_ENV=production` or `PARVA_ENV=staging`.
- `PARVA_SOURCE_URL` pointing to the corresponding published source.
- `PARVA_ROUTE_PROFILE` set to a public/deployed-safe profile such as
  `public_reference`, `public_demo`, `minimal_public`, `developer_preview`, or
  `enterprise_preview`.
- `PARVA_RATE_LIMIT_BACKEND=redis` and `PARVA_REDIS_URL`.
- `PARVA_PROVENANCE_ATTESTATION_KEY` or
  `PARVA_PROVENANCE_ATTESTATION_KEY_FILE`.
- `PARVA_REQUIRE_SIGNED_PROVENANCE_MUTATIONS=true`.
- `PARVA_ADMIN_TOKEN` when admin, billing, experimental, or mutation surfaces
  are mounted.
- `PARVA_BILLING_ENABLED=true` deployments must use a Postgres
  `PARVA_DATABASE_URL` and a non-default `PARVA_API_KEY_PEPPER`.
- `PARVA_TRUSTED_PROXY_IPS` must name exact trusted proxies; `*` is rejected.
- CORS origins must be explicit and cannot include localhost in production or
  staging.

## Rejected In Production/Staging

- `PARVA_DEBUG=true`.
- `PARVA_RATE_LIMIT_BACKEND=memory`.
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
