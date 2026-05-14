---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Protocol Security

Parva Protocol is a protocol draft. Public artifacts must be useful for verification without exposing private future-BS outputs, private source archives, customer data, secrets, or fake authority.

## Security Objectives

- Keep public and private route profiles separate.
- Keep private future-BS prediction, export, backtest, residual, comparison, and schedule-impact workflows out of public OpenAPI by default.
- Keep public protocol credentials hash-only until a real signing profile is configured.
- Preserve claim boundaries on every credential, conformance report, evidence packet, and offline bundle.
- Reject unsupported or high-risk temporal claims into human review instead of presenting them as verified.

## Public Artifact Rules

Public protocol artifacts may include schemas, source records, release manifests, trust logs, evidence packet shapes, alpha conformance reports, and preview offline bundle manifests.

Public protocol artifacts must not include:

- secrets or API tokens
- customer names or private business strategy
- private source paths
- exact private future-BS vectors
- corrected future values
- private calibration thresholds
- fake signatures or implied certification

## Credential Status

Preview credentials use:

- `hash_only_preview` for deterministic hash verification
- `unsigned_preview` for preview offline bundle manifests

These labels are intentional. They prevent a public demo credential from being mistaken for a production legal, tax, banking-contract, regulatory, or official calendar authority.

## Route Exposure

The lightweight public demo excludes protocol, agent, and impact POST routes. Full or private deployments may enable them when an operator has reviewed the source policy, CORS policy, authentication, and operational boundary.
