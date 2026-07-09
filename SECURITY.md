# Security Policy

Project Parva is temporal infrastructure, so security controls are part of the
trust story. This file is the authoritative security policy and security
engineering index for the repository.

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
- structured audit logs for admin billing actions
- explicit production/staging rejection of wildcard trusted proxy headers

Detailed engineering references:

- [Security model](docs/SECURITY_MODEL.md)
- [Production deployment guardrails](docs/PRODUCTION_DEPLOYMENT_GUARDRAILS.md)
- [PII and trace policy](docs/PII_AND_TRACE_POLICY.md)
- [Admin audit logging](docs/ADMIN_AUDIT_LOGGING.md)
- [Billing security](docs/BILLING_SECURITY.md)

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

`scripts/security/run_audit.py` writes a generated artifact report to `reports/security_audit.json`. That report is an artifact, not source.

## CORS and CSP

Production CORS must use explicit origins, methods, and headers. Wildcard
methods or headers are not allowed for credentialed production use.

The backend sets conservative browser-visible security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Content-Security-Policy: default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'`

## Trusted proxies

`PARVA_TRUSTED_PROXY_IPS=*` is allowed only for local or test use. Production
and staging deployments must list explicit trusted proxy IPs.

## CSRF boundary

Current public and commercial API flows use bearer or API-key authentication,
not cookie-session authentication. If cookie or session authentication is
introduced later, it must include CSRF tokens or strict SameSite cookie policy
before production use.

## Admin billing audit

Manual billing actions are auditable. Admin invoice payment, subscription
extension, and API-key revocation actions emit structured audit events with:

- admin principal
- invoice, subscription, or key id
- provider and provider reference where applicable
- request id
- timestamp
- action type

## Transparency log

The public transparency log is append-only and hash-chained for the public
preview. The local implementation is process-safe. Multi-process production
deployments should use a database-backed append-only log or an external lock.

## JPL and source artifacts

JPL and source artifact downloads must be checksum-verified or handled as
explicit release artifacts. Docker builds should not silently depend on
unverified live downloads.

Large source PDFs are allowed only when provenance, retrieval policy, and
checksums are clear. Otherwise they belong in controlled release artifacts or
private source archives, not in the public repository.
