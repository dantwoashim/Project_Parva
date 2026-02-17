# Year 1 Week 3 — Verification & Ground Truth Status

## Scope Delivered

1. Built baseline ground truth for **BS 2080–2082** from MoHA OCR matched entries.
2. Added extraction confidence metadata per entry.
3. Generated discrepancy register comparing V2 (without overrides) vs official baseline.
4. Generated scorecard with:
   - by-festival breakdown
   - by-rule-group breakdown
   - by-BS-year breakdown
5. Ran evaluator pipeline and saved evaluation artifacts.

## New Tooling

- `backend/tools/week3_ground_truth_pipeline.py`
  - builds baseline
  - builds discrepancies
  - builds scorecard (JSON + Markdown)

Run command:

```bash
PYTHONPATH=backend python3 backend/tools/week3_ground_truth_pipeline.py
```

## Artifacts Produced

- `data/ground_truth/baseline_2080_2082.json`
- `data/ground_truth/discrepancies.json`
- `data/ground_truth/scorecard_2080_2082.json`
- `data/ground_truth/scorecard_2080_2082.md`
- `data/ground_truth/evaluation_week3.csv`
- `data/ground_truth/evaluation_week3.md`

## Current Metrics

From baseline pipeline (`scorecard_2080_2082.json`):
- Total usable entries: **45**
- V2 exact match rate **without overrides**: **24.44%**
- V2 exact match rate **with overrides**: **86.67%**
- Discrepancies: **34**

Top probable causes:
- `adhik_maas_or_lunar_month_alignment`: 19
- `tithi_boundary_or_timezone`: 9
- `legacy_rule_fallback`: 3
- `minor_rule_alignment`: 2
- `no_rule_or_calc_failure`: 1

From evaluator (`evaluate.py`, with current override behavior):
- Tests: **64**
- Passed: **64 (100%)**

## Interpretation

1. Ground-truth ingestion and scoring pipeline is now in place and repeatable.
2. Official alignment currently depends significantly on overrides.
3. Largest technical gap remains lunar-month/Adhik alignment in algorithmic mode.

## Week 4 Priority (recommended)

1. Resolve highest-impact discrepancy cluster:
   - `adhik_maas_or_lunar_month_alignment`
2. Migrate remaining legacy-only rule IDs to V3-native rules to reduce fallback.
3. Re-run Week 3 pipeline after each fix and track reduction in discrepancy count.
