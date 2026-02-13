# Benchmark Package

This folder provides reproducible benchmark tooling for Project Parva and now includes Year-3 preparation harnesses.

## Scope

- Evaluates festival-date calculations using `evaluate_v4`.
- Rebuilds discrepancy report and scorecard.
- Enforces minimum accuracy gate.
- Validates benchmark packs (`benchmark/validate_pack.py`).
- Runs pack-driven HTTP assertions (`benchmark/harness.py`).

## Prerequisites

- Python 3.11+
- Dependencies installed for backend and scripts
- Run from repo root

## Run

```bash
./benchmark/run_benchmark.sh

# Year-3 prep harness
python3 benchmark/validate_pack.py benchmark/packs/bs_conversion_pack.json
PYTHONPATH=backend python3 benchmark/harness.py benchmark/packs/bs_conversion_pack.json --local
PYTHONPATH=backend python3 benchmark/run_all_packs.py
```

## Outputs

- `benchmark/output/evaluation_v4.json`
- `benchmark/output/evaluation_v4.csv`
- `benchmark/output/evaluation_v4.md`
- `benchmark/results/*_report.json` (pack harness reports)
- `benchmark/results/baseline_2028Q1.json` (consolidated baseline)
- `data/ground_truth/discrepancies.json`
- `reports/evaluation_scorecard.md`

## Expected headline

On current dataset baseline, the run is expected to pass the gate and produce no open discrepancy in the triage report.

## Reproducibility notes

- See `benchmark/checksums.sha256` for integrity of benchmark input files.
- Use `PYTHONPATH=backend` consistently when invoking backend tools.
