# Differential Testing (Year 3 Week 9-10 Prep)

## Goal
Detect drift by comparing current benchmark results with a baseline report.

## Taxonomy
- `agreement`
- `minor_difference`
- `major_difference`
- `source_missing`
- `incomparable`

## Framework
Implementation:
- `/Users/rohanbasnet14/Documents/Project Parva/backend/app/differential/framework.py`

Runner:
- `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/run_differential.py`

Outputs:
- `/Users/rohanbasnet14/Documents/Project Parva/reports/differential_report.json`
- `/Users/rohanbasnet14/Documents/Project Parva/reports/differential_report.md`
- `/Users/rohanbasnet14/Documents/Project Parva/data/differential/disagreements.json`

## Usage
```bash
PYTHONPATH=backend python3 backend/tools/run_differential.py \
  --current benchmark/results/bs_conversion_v1_report.json \
  --baseline benchmark/results/baseline_2028Q1_bs_conversion.json
```

If baseline is missing, the tool bootstraps baseline from current.

## Drift Gate (recommended)
- Warn if `drift_percent > 1%`
- Block release if `drift_percent > 2%`
