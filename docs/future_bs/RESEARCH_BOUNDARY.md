---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-04
owner: research-team
---

# Future BS Research Boundary

The public profile serves a curated, precomputed Future BS forecast. The controlled profile contains the full research workspace.

## Public Profile

Public profiles may expose:

- `/v4/api/future-bs/capabilities`
- `/v4/api/future-bs/methodology`
- `/v4/api/future-bs/forecast/{bs_year}`
- the committed forecast and methodology artifacts used by those routes
- selected month lengths, prediction sets, model probabilities, boundary distance, risk labels, and validation scope

Every forecast uses `computed_prediction_not_official`, requires human review, and records that authoritative publication overrides the computed result.

## Controlled Profile

The controlled profile retains:

- bulk prediction and export
- source-sheet import and comparison
- backtests and residual rows
- model-run inventories
- raw explain and boundary payloads
- calendar model-risk internals
- loan, contract, and schedule-impact simulation
- private source archives and calibration data

Controlled routes require:

```text
PARVA_ROUTE_PROFILE=research_private | internal_lab | full_dev
PARVA_ENABLE_EXPERIMENTAL_API=true
PARVA_ENABLE_RESEARCH_API=true
PARVA_ADMIN_TOKEN=<operator token> or scoped PARVA_API_KEYS
```

Private OpenAPI additionally requires `PARVA_SHOW_PRIVATE_SCHEMA=true`.

## Release Rule

A public forecast release must preserve its source tier, snapshot and model versions, validation interpretation, risk labels, review requirement, and publication status. Leakage of private paths, source contents, raw model runs, or unqualified authority claims blocks release.
