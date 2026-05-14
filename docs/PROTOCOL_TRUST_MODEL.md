---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Protocol Trust Model

Parva Protocol separates evidence strength from convenience. A route can be useful while still carrying a limited claim boundary.

## Trust Inputs

The trust model uses:

- source tier
- source independence
- release manifest status
- trust log presence
- confidence label
- claim boundary
- human review status
- conflict status
- artifact hash integrity

## Confidence Labels

Common labels include:

| Label | Meaning |
| --- | --- |
| `official_verified` | Strong official evidence supports the claim |
| `source_backed` | Public source metadata supports the claim |
| `calculated` | Computed result with a documented method |
| `fixture_only` | Synthetic or test data |
| `research_preview` | Research output that needs review before operational use |
| `disputed` | Conflicting evidence exists |
| `unsupported` | The system cannot support the claim |
| `unknown` | Confidence has not been established |

## Claim Boundaries

Public claims must preserve their boundary. Future-BS research outputs use `computed_prediction_not_official`. Agent, impact, and protocol outputs are decision support, not legal, tax, banking-contract, regulatory, or official calendar authority.

## Human Review

Human review is required when a claim is unsupported, future-facing, operational, legal, official-status-sensitive, disputed, or backed only by weak evidence.
