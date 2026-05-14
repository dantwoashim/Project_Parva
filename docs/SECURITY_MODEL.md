---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# Security Model

Project Parva exposes public calendar and trust APIs, commercial API-key flows,
admin operations, provenance mutation paths, RuleLang execution, agent-safe
tools, billing state, generated trust artifacts, and frontend/static surfaces.

## Assets

- API keys, admin bearer tokens, billing database rows, subscription state, and
  webhook secrets.
- Provenance records, transparency log entries, trust anchors, evidence packets,
  release/source metadata, and reason traces.
- Public calendar data, computed panchanga/kundali/muhurta outputs, Future-BS
  research outputs, and route profile exposure policy.
- Deployment configuration: CORS, CSP, rate limiter, trusted proxy settings,
  provenance attestation keys, source URL, database URL, and API key pepper.

## Trust Boundaries

- Public unauthenticated callers can reach stable public read routes and selected
  preview routes allowed by route profile policy.
- API-key principals can reach commercial read surfaces and quota-tracked routes.
- Admin principals can mutate billing/admin state and provenance/trust surfaces.
- Local CLI scripts can regenerate artifacts, but public runtime must not rely on
  private data or test-only fixtures.
- Production and staging deployments are not allowed to silently use process-local
  rate limiting, SQLite billing storage, unsigned provenance mutation mode, debug
  mode, private route profiles, or missing source publication metadata.

## Security Invariants

- Production and staging fail closed on unsafe configuration.
- Admin mutations require admin auth, local-only semantics, or an explicit
  non-production guard.
- Billing secrets are never stored in plaintext; new API keys use versioned
  PBKDF2-HMAC hashes with random salt and a deployment pepper.
- Provenance and billing mutations write audit records with actor context,
  route/action, object ID, before/after hashes when available, request ID, source
  context, and timestamp.
- Reason traces, billing audit metadata, transparency payloads, and public trace
  artifacts are scrubbed for obvious PII before persistence.
- RuleLang and agent tools cannot execute arbitrary code, call network/file/env
  sinks, run unbounded loops, or approve sensitive payroll/banking/legal/fiscal
  actions without review gates.

## Failure Mode

The intended failure mode for security-critical controls is fail closed:
startup refuses unsafe production config, Redis rate-limit outages return a clear
503 instead of bypassing global limits, and unsupported/ambiguous agent claims
return review-required or unsupported decisions.
