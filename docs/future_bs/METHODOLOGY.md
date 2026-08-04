---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-04
owner: research-team
---

# Future BS Methodology

The Future BS engine forecasts month boundaries first and derives month lengths from consecutive boundaries. The selected public model is `solar_civil_ensemble_v4`, implemented through method version `parva_solar_civil_accuracy_v6` and calibration version `de440_swiss_crosscheck_civil_decision_knn_pattern_stack_2000_2083_v4`.

## Calculation Pipeline

1. Source-labeled historical BS month boundaries form the training and replay corpus.
2. The astronomy layer solves sidereal solar ingress moments for successive solar signs.
3. Each ingress instant is converted to Nepal civil time.
4. A month-specific civil cutoff assigns the ingress to a candidate civil date.
5. A past-only statistical pattern stack scores alternative month lengths around sensitive boundaries.
6. A sequence decoder selects a complete twelve-month year that satisfies calendar constraints.
7. The engine emits prediction sets, model probabilities, agreement, boundary distance, and review risk.

Month length is calculated as:

```text
length(month m) = start(month m + 1) - start(month m)
```

This structure keeps the astronomical event, civil assignment rule, and final calendar value separate and reviewable.

## Civil Assignment

Ingress time alone does not define the BS civil month start. The engine applies a learned cutoff for each month, expressed as minutes after midnight in Nepal time. The public methodology artifact records all twelve selected cutoffs, their calibration sample counts, and replay errors.

The selected family uses month-specific cutoff grid search with boundary abstention. Events close to a cutoff receive stronger review flags because a small rule or source difference can move the civil assignment by one day.

## Sequence Constraints

The decoder evaluates the complete year rather than finalizing each month independently. A valid result must contain:

- exactly twelve months
- month lengths from 29 through 32 days
- a year total of 365 or 366 days

These constraints reject locally plausible combinations that form an invalid year.

## Uncertainty Output

Each month includes:

- a selected length
- 80% and 95% model prediction sets
- probabilities for 29, 30, 31, and 32 days
- model agreement
- heuristic confidence
- distance from the civil assignment boundary
- GREEN, YELLOW, or RED risk labels

The public API sets `review_required=true` for every forecast. A GREEN label describes lower model risk within this system. The publication status remains `computed_prediction_not_official` across every label.

## Validation Boundary

The selected model reproduces `72/72` official month cases from `2078-2083 BS`. The same window contributed to calibration, so the result measures calibrated replay fit. It provides an implementation check and supports method selection. It provides no independent future-accuracy guarantee.

The project requires at least 528 verified month cases before considering a broad independent accuracy claim. Current public metadata reports that threshold as unmet.

## Ephemeris Position

The ingress layer supports a checksum-verified JPL DE440 kernel when an operator supplies it. Swiss Ephemeris and the built-in Moshier path provide cross-check and fallback calculations. The public forecast is precomputed, versioned, and served without performing an expensive ephemeris solve during each request.
