# Parva Temporal Spec

This directory contains public temporal specifications for Project Parva.

## Current Drafts

- `PARVA_TEMPORAL_SPEC_V0_1.md`: early public contract draft for shared temporal objects and JSON schemas.
- `PARVA_TEMPORAL_SPEC_V1.md`: older normative core draft for selected computation behavior.

The v0.1 draft focuses on public data contracts. It defines names and JSON shapes for dates, source references, releases, calculation traces, fiscal years, panchanga days, festivals, reconciliation events, and future-BS risk labels.

## Schema Location

Root public schemas live in:

```text
schemas/
```

These schemas define public contracts. They are intended for documentation, SDK generation, conformance checks, and integration review.

## Claim Boundary

Project Parva is not an official government calendar publication.

Official publication overrides computed output.

Future-BS research outputs remain:

```text
computed_prediction_not_official
```

The implementation may evolve, but public contracts should keep source policy, publication status, and review posture visible.
