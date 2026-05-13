# Security

Project Parva is temporal infrastructure, so security controls are part of the
trust story.

## Authentication

Public read surfaces do not require credentials. Admin and commercial surfaces
use bearer tokens or API keys.

API keys use versioned slow hashing with per-key salt. Production billing must
set a real `PARVA_API_KEY_PEPPER`; the local development pepper is rejected
outside local, test, and development environments.

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
