---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Model Registry

Status: governance registry.

The active Future-BS engine is registered as a computed prediction system. It is
not an official publication system.

## Active Run

| Field | Value |
| --- | --- |
| Method version | `parva_solar_civil_accuracy_v6` |
| Calibration version | `de440_swiss_crosscheck_civil_decision_knn_pattern_stack_2000_2083_v4` |
| Default run id | `parva_solar_civil_accuracy_v6_2026_05_07_001` |
| Prediction range | `2084-2200 BS` |
| Publication status | `computed_prediction_not_official` |
| Public snapshot | `forecast_snapshot_v6_2084_2200.json` |

## Registered Model Families

| Family | Role | Public exposure |
| --- | --- | --- |
| Solar-ingress civil decision model | Primary computational tower | Selected methodology and curated snapshot |
| Past-only statistical pattern stack | Secondary bounded signal | Selected methodology and curated snapshot |
| Legacy-cycle baseline | Diagnostic disagreement signal | Private diagnostic only |
| JPL DE440 adapter | Optional high-precision ephemeris adapter | Availability metadata only |
| Swiss Ephemeris adapter | Local astronomical adapter | Availability metadata only |
| Moshier adapter | Fallback astronomical adapter | Availability metadata only |
| Risk threshold classifier | GREEN/YELLOW/RED posture | Public month-level labels |
| Calendar model-risk service | Private exact prediction and stress review | Private routes only |

## Registry Rules

- Public docs may name model families and method versions.
- Public routes expose one selected year at a time; bulk vectors and model-run internals remain controlled.
- Private model-run endpoints require the research route gates documented in
  [RESEARCH_BOUNDARY.md](RESEARCH_BOUNDARY.md).
- Any new public accuracy claim must cite the source policy and evidence window
  used to reproduce it.
