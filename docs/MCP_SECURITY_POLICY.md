---
status: stable
tier: 1
lane: dx
last_verified: 2026-07-20
owner: dx-team
---

# MCP Security Policy

The Parva MCP server is read-only. It uses the official MCP SDK for lifecycle,
version negotiation, notifications, ping, schemas, and stdio framing.

Every tool call is sent to one fixed route:

```text
POST /v3/api/agent/run-tool
```

The server applies these controls:

- closed JSON Schemas with server-side validation
- HTTPS for remote API origins
- HTTP allowed only for local development hosts
- request timeout bounded from 1 to 120 seconds
- response size bounded to 8 MiB
- redirects blocked
- non-JSON and non-object responses rejected
- upstream errors sanitized before they reach an MCP client
- standard output reserved for MCP messages
- optional bearer token read from the process environment

The manifest excludes shell execution, filesystem writes, arbitrary URLs,
private Future-BS routes, admin routes, billing routes, keys, webhooks, and trust
mutation routes. Resource reads accept the six declared `parva://` URIs only.

Successful and failed tool results preserve `claim_boundary`,
`review_required`, and `not_authority`. Future-BS results keep
`publication_status = computed_prediction_not_official` when supplied by the
API.

Project Parva does not replace government publications or institutional policy.
Sensitive legal, tax, banking, payroll, religious, disputed-source, and future
calendar decisions follow the human-review status returned by the agent layer.
