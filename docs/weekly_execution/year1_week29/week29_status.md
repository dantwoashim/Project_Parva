# Year 1 Week 29 Status (Evaluation Harness)

## Completed
- Added configurable evaluation harness:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/evaluate_v4.py`
- Features implemented:
  - Year-range filtering (`--year-from`, `--year-to`)
  - Festival filtering (`--festival`)
  - Override toggling (`--no-overrides`)
  - MoHA expansion toggling (`--no-moha`)
  - By-festival and by-rule summaries
  - Probable-cause classification for mismatches
- Generated outputs:
  - `/Users/rohanbasnet14/Documents/Project Parva/reports/evaluation_v4/evaluation_v4.csv`
  - `/Users/rohanbasnet14/Documents/Project Parva/reports/evaluation_v4/evaluation_v4.json`
  - `/Users/rohanbasnet14/Documents/Project Parva/reports/evaluation_v4/evaluation_v4.md`
- Added summary unit test:
  - `/Users/rohanbasnet14/Documents/Project Parva/tests/unit/tools/test_evaluate_v4.py`

## Outcome
- Evaluation is now configurable, analyzable, and automation-friendly.
