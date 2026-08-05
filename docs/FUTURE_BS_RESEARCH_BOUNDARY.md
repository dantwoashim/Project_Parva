---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-05
owner: platform-team
---

# Future BS Research Boundary

Project Parva exposes a curated Future BS research forecast and retains the broader research workspace behind controlled deployment gates.

## Publicly Available

- capability discovery at `/v4/api/future-bs/capabilities`
- selected methodology at `/v4/api/future-bs/methodology`
- one-year forecasts at `/v4/api/future-bs/forecast/{bs_year}`
- tracked forecast coverage for `2084-2200 BS`
- twelve month lengths, prediction sets, normalized model support, model agreement, civil-boundary distance, constraints, and risk labels
- method and calibration versions, source metadata, warnings, and validation scope

All forecast responses preserve:

```text
publication_status = computed_prediction_not_official
review_required = true
authoritative_publication_overrides = true
```

## Controlled Research

Bulk ranges, exports, imports, comparisons, backtests, residuals, model-run inventories, detailed raw traces, financial simulations, and private evidence require `research_private`, `internal_lab`, or `full_dev`, plus experimental/research flags and operator authentication.

Public OpenAPI contains the curated routes. Private OpenAPI requires `PARVA_SHOW_PRIVATE_SCHEMA=true`.

## Evidence Rule

The `72/72` result covers chronological rolling validation over official month cases from `2078-2083 BS`. Every target year uses training data ending at the previous BS year. The window also informed model development, and its 72 month cases remain below the 528 verified-month threshold for a broad independent accuracy claim.

Detailed policy lives in [future_bs/RESEARCH_BOUNDARY.md](future_bs/RESEARCH_BOUNDARY.md).
