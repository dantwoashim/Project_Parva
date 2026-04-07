# Security Policy

## Supported tracks

| Track | Status | Notes |
| --- | --- | --- |
| `/v3/api/*` | Supported public contract | Canonical public API for new integrations |
| `/api/*` | Legacy compatibility | Still served, but not recommended for new work |
| `/v2`, `/v4`, `/v5` | Experimental | Disabled by default and not version-isolated |
| Admin or mutation surfaces | Non-public | Require explicit auth and are outside the public stability promise |

See [docs/ROUTE_ACCESS.md](docs/ROUTE_ACCESS.md) and [docs/STABILITY.md](docs/STABILITY.md).

## Reporting a vulnerability

Use GitHub private vulnerability reporting for this repository if it is enabled. If private reporting is not available, open a minimal public issue requesting a private follow-up channel and do not include exploit details, live credentials, or sensitive environment information.

Include:

- affected path or component
- reproduction steps
- expected impact
- affected commit or tag if known

## Current security posture

- request-size and query-length guards
- security response headers
- per-request IDs
- auth for non-public/admin surfaces
- rate limiting with production validation for Redis-backed distributed mode
- startup validation for risky deployment flags
- repo hygiene and secret scanning in CI

## Access model

- The normal `v3` read and compute surface is public by default.
- Public compute does not imply private storage. Treat request-sensitive POST routes carefully and follow route metadata.
- Admin and preview surfaces require either a scoped `X-API-Key` or an admin bearer token.
- Experimental routes are disabled unless explicitly enabled by configuration.

## Recommended hardening routine

```bash
make verify
python3.11 scripts/security/run_audit.py
```

`scripts/security/run_audit.py` writes a generated report to `reports/security_audit.json`. That report is an artifact, not source.
