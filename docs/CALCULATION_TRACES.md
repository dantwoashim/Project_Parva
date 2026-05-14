---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Calculation Traces

Calculation traces explain the release, source policy, input, output, and ordered steps behind a result.

The public trace schema is:

```text
schemas/calculation-trace.schema.json
```

## What A Trace Does

A trace helps reviewers answer:

- what operation was run
- what input was used
- what output was produced
- which release was used
- which source policy applied
- which steps were applied
- which warnings were raised
- what publication status applies

## Public Trace Shape

Example:

```json
{
  "trace_id": "tr_demo_bs_to_ad_2083_01_01",
  "operation": "bs_to_ad",
  "input": {"year": 2083, "month": 1, "day": 1},
  "output": {"date": "2026-04-14"},
  "release_id": "parva-bs-public-demo",
  "source_policy": "public_demo",
  "steps": [
    {"name": "validate_bs_date", "status": "applied"},
    {"name": "resolve_month_start", "status": "applied"},
    {"name": "add_day_offset", "status": "applied"},
    {"name": "project_to_gregorian", "status": "applied"}
  ],
  "warnings": [],
  "publication_status": "computed_prediction_not_official"
}
```

## Backend Model

The backend now includes a public trace model aligned with the schema:

```text
backend/app/core/calculation_trace.py
```

This model is intentionally additive. It does not change existing API routes or private trace storage.

## Claim Boundary

Traces explain computation. They do not create official authority.

Official publication overrides computed output.

Future-BS output remains:

```text
computed_prediction_not_official
```

## Alpha Limitations

- Public traces are schema-level and model-level in this phase.
- Existing runtime trace storage remains compatible with current routes.
- Future work can attach release identifiers and artifact hashes to selected public API responses once route-level integration is reviewed.
