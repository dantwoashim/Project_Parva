---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Research Layer

Status: research-private boundary.

The future-BS layer is an experimental calendar-risk research system. It studies how month-length assumptions behave before they affect fiscal reports, contracts, renewals, interest periods, exports, and audit trails.

Parva does not publish assured future BS dates.

## Public Research Summary

The public documentation describes the concept without exposing private future values, full prediction vectors, private calibration artifacts, or exact model thresholds.

The research approach is:

- month start is the primitive
- month length is derived from the next month start minus the current month start
- solar-civil computation provides one computational tower
- source-aware validation separates official, printed, public-witness, publisher, software-table, and third-party evidence
- regime-aware risk detection separates stable behavior from boundary-sensitive or source-conflicted months
- GREEN, YELLOW, and RED labels describe risk posture, not official status

## Public Surface

The public deployment exposes only:

- future-BS capabilities summary
- source policy summary
- claim boundary
- risk-label vocabulary
- aggregate validation posture

The public deployment does not expose direct future month-length prediction, full-range exports, model runs, backtests, residual analysis, client sheet comparison, or schedule-impact simulation by default.

## Module Classification

Future-BS code is classified by public-safety level:

| Class | Meaning |
|---|---|
| Production/core | Stable calendar conversion policy, public capability summaries, and claim-boundary enforcement |
| Public preview | Risk-label vocabulary, source-policy summaries, and aggregate validation posture |
| Research/private | Month-start inversion, model runs, residual analysis, calibration artifacts, wide-corpus evaluation, and generated future vectors |
| Experimental | Shadow-source comparison, candidate-rule scoring, weak-label fusion, and active-learning queues |

Public APIs must not present research/private or experimental outputs as
official. Any future-dated output stays `computed_prediction_not_official`
unless a future source-policy decision explicitly says otherwise.

## Naming Honesty

Some research modules use ambitious historical names because they started as
research prototypes. Public documentation should describe their current
behavior precisely:

- fixed rule-grid scoring should be described as candidate rule selection
- weighted source consensus should be described as consensus truth selection
- ayanamsha candidates should be described as candidate evaluation unless a real calibration run is present
- heuristic forecast scores should be labeled `heuristic_accuracy_estimate` or `heuristic_not_empirically_calibrated`

## Evidence Boundary

The official-strict evidence window remains limited. Strong results inside a narrow official window support the research direction, but they do not prove broad future-calendar certainty.

All future outputs are labeled:

```text
computed_prediction_not_official
```

See [../FUTURE_BS_RESEARCH_BOUNDARY.md](../FUTURE_BS_RESEARCH_BOUNDARY.md) for the current public/private exposure policy.
