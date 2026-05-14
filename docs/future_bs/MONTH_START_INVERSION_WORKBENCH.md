---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Month-Start Inversion Workbench

Project Parva's future-BS research layer treats the BS month start as the
primitive calendar fact. Month length is derived from the distance between one
month start and the next month start.

The Month-Start Inversion Workbench is a historical diagnostic tool. It does
not publish official future dates. Its generated outputs use:

`publication_status = computed_prediction_not_official`

## Purpose

The workbench helps answer one question:

Which civil-date assignment rule best explains verified historical BS
month-start outcomes?

It produces:

- month-start candidates
- solar ingress timing features
- cutoff-distance features
- civil-date assignment candidates
- official match and fail labels
- boundary-risk cases
- rule inversion summary
- false-GREEN memory
- top verification targets

## Data Policy

The default run is historical-only and stops at BS 2083. Official match labels
come only from source-policy final-test rows, currently the official-verified
2078-2083 window.

Weak third-party and needs-review rows can appear in the verification target
queue, but they do not become official truth and do not support official-grade
accuracy claims.

## Command

```powershell
$env:PYTHONPATH='backend'
python scripts\future_bs\run_month_start_inversion_workbench.py
```

Artifacts are written under:

```text
data/future_bs/accuracy_lab/month_start_inversion_workbench/
```

This directory is ignored by Git because the artifacts are diagnostic research
outputs, not public release data.

## Output Files

| File | Purpose |
|---|---|
| `month_start_candidates.csv` | Observed source starts plus civil-rule candidate starts |
| `solar_ingress_timing_features.csv` | Solar ingress timing, weekday, cutoff distances, and boundary risk |
| `civil_date_assignment_candidates.csv` | Rule-by-rule candidate assignments and errors |
| `official_match_labels.csv` | Match/fail labels against official verified rows |
| `boundary_risk_cases.csv` | Boundary-sensitive historical cases |
| `rule_inversion_summary.json` | Machine-readable inversion summary |
| `rule_inversion_summary.md` | Human-readable inversion summary |
| `false_green_memory.json` | Historical cases where a rule would have been overconfident and wrong |
| `top_verification_targets.csv` | Ranked historical rows for official, printed, or public witness acquisition |

## Interpretation

The current official label set remains small. The workbench can reject fragile
rules, identify boundary-sensitive cases, and rank source acquisition targets.
It should not be used to claim broad future-calendar certainty.

The highest-value next data work is to promote more historical month starts
from weak or needs-review status into official, printed, or public-daily
witness status.
