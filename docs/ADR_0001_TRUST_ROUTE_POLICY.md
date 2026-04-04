# ADR 0001: Public Trust Route Policy

## Status

Accepted

## Decision

Parva exposes trust-facing read surfaces as part of the public v3 API contract:

- reliability read routes
- provenance read routes
- public artifacts
- spec/conformance visibility

Write or mutation-oriented provenance operations remain protected by admin policy.

## Why

The product already depends on trust/reliability/provenance as part of the public story. Hiding those routes in some environments while referencing them in docs and OpenAPI created drift and made release gating brittle.

## Consequences

- Docs, runtime, and contract freeze now agree.
- Access control remains explicit-public and default-deny for unknown API paths.
- Contributors should treat trust-read routes as product surface, not internal-only debug endpoints.

## Follow-up

- Continue moving trust payload assembly into presenters/shared trust helpers.
- Keep operational-only metrics in Prometheus/logs when they are too noisy for product surfaces.
