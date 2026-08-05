---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-04
owner: research-team
---

# Future BS Methodology

The Future BS engine forecasts month boundaries first and derives month lengths from consecutive boundaries. The selected public model is `parva_authority_aware_solar_civil_v7`, with calibration version `de440_source_stratified_authority_civil_2000_2083_v5`.

## Calculation Pipeline

1. Source-labeled historical BS month boundaries form a broad reference tower and a separate official-evidence tower.
2. The astronomy layer solves sidereal solar ingress moments for successive solar signs.
3. Each ingress instant is converted to Nepal civil time.
4. Each tower independently assigns candidate civil month starts using KNN and calibrated cutoff rules.
5. The official tower activates after four prior verified years, which is one more than the three-neighbour civil classifier requires.
6. Each tower receives equal total influence regardless of its internal rule count. Official support resolves an otherwise equal boundary vote.
7. The engine derives a coherent twelve-month sequence and emits model support, prediction sets, boundary distance, and review risk.

Month length is calculated as:

```text
length(month m) = start(month m + 1) - start(month m)
```

This structure keeps the astronomical event, civil assignment rule, and final calendar value separate and reviewable.

## Civil Assignment

Ingress time alone does not define the published BS civil month start. Recent NPNS material describes traditional Saurukta practice, while Parva's astronomy tower calculates modern physical ingress with JPL or Swiss ephemeris data. The engine keeps these signals separate instead of treating one as a direct substitute for the other.

The reference tower learns from the broad historical table. The authority tower learns only from verified official rows. Both towers use the same reusable civil-rule families. Their candidate month starts are reconciled by weighted support, with source authority used only as a tie-break. Events close to a cutoff receive stronger review flags because a small rule or source difference can move the civil assignment by one day.

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
- normalized model support for 29, 30, 31, and 32 days
- model agreement
- heuristic confidence
- distance from the civil assignment boundary
- GREEN, YELLOW, or RED risk labels

The support values are not calibrated probabilities. Public snapshots keep every month at review-required posture until independent probability calibration becomes possible. The publication status remains `computed_prediction_not_official` across every label.

## Validation Boundary

The selected model matches `72/72` official month cases from `2078-2083 BS` under chronological rolling validation. Each target year uses data ending at `target year - 1`. The model contains no target-year lookup or year-specific correction. The result is evidence for this small window and provides no broad future-accuracy guarantee.

The public forecast is trained through BS 2083. Rows for BS 2084 onward remain excluded from training even when weak lookup tables contain them.

The project requires at least 528 verified month cases before considering a broad independent accuracy claim. Current public metadata reports that threshold as unmet.

The [BS 2082 boundary diagnosis](2082_BOUNDARY_DIAGNOSIS.md) records the former failure, the missing model distinction, the two-tower vote, and the corrected chronological replay.

## Ephemeris Position

The ingress layer supports a checksum-verified JPL DE440 kernel when an operator supplies it. Swiss Ephemeris and the built-in Moshier path provide cross-check and fallback calculations. The public forecast is precomputed, versioned, and served without performing an expensive ephemeris solve during each request.
