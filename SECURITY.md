# Security Policy

## Supported versions

| Track | Status | Notes |
| --- | --- | --- |
| `v3` | public stable | only launch-supported public contract |
| `v2`, `v4`, `v5` | experimental | disabled by default |
| webhook management | not shipped | startup rejects enablement in this build |
| provenance and ops mutations | admin only | not part of public stable profile |

## Reporting a vulnerability

- Open a private disclosure with reproduction steps, impacted endpoint, and
  expected risk.
- Include the affected commit hash or tag if known.

## Baseline controls

- request-size and query-length guards
- per-request IDs and structured request logs
- security response headers
- admin bearer token and scoped API key support for non-public surfaces
- rate limiting for anonymous and authenticated traffic
- startup validation for risky feature flags
- dependency audit script: `python scripts/security/run_audit.py`

## Access control policy

- Public stable `v3` endpoints are intentionally anonymous and read-only.
- Non-public routes must be called with either a scoped `X-API-Key` or an
  admin bearer token.
- Provenance mutation routes are admin-only.
- Webhook routes are not part of the production launch build.

The detailed route matrix is documented in `docs/ROUTE_ACCESS.md`.

## Hardening routine

- Run `python -m pytest -q`
- Run `npm --prefix frontend run lint`
- Run `npm --prefix frontend test -- --run`
- Run `python scripts/security/run_audit.py`
- Run `python scripts/check_path_leaks.py`
- Archive generated security output in `reports/security_audit.json`
