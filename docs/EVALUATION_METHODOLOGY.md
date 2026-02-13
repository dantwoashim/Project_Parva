# Evaluation Methodology (V4)

## Purpose
Provide repeatable, source-aware evaluation of festival date calculations with by-festival and by-rule visibility.

## Harness
- Script: `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/evaluate_v4.py`
- Inputs:
  - Built-in reference cases (`TEST_CASES_2026`)
  - Optional OCR-expanded MoHA matched cases from `data/ingest_reports/*.csv`
- Core engine under test: `calculator_v2.calculate_festival_v2`

## Run Parameters
- `--year-from`, `--year-to`: limit by Gregorian year
- `--festival`: filter one/many festival ids
- `--variance`: accepted day delta (default `1`)
- `--no-overrides`: test pure algorithm without official overrides
- `--no-moha`: disable OCR-expanded dataset

## Output Artifacts
- CSV: `reports/evaluation_v4/evaluation_v4.csv`
- JSON: `reports/evaluation_v4/evaluation_v4.json`
- Markdown: `reports/evaluation_v4/evaluation_v4.md`

Each row includes:
- `festival_id`, `year`, `expected_date`, `calculated_date`
- `passed`, `variance_days`
- `source`, `notes`
- `rule_type` (`lunar|solar|fallback`)
- `probable_cause` (`match|boundary_shift|rule_or_source_mismatch|calculation_error|missing_result`)

## Score Breakdown
The harness computes:
- Overall pass rate
- Pass rate by festival
- Pass rate by rule type
- Failure-cause counts

## Scorecard/Trend Tracking
- Scorecard generator: `/Users/rohanbasnet14/Documents/Project Parva/scripts/generate_scorecard.py`
- Trend history: `reports/evaluation_history.jsonl`
- Current scorecard: `reports/evaluation_scorecard.md`
- Gate script: `/Users/rohanbasnet14/Documents/Project Parva/scripts/check_accuracy_gate.py`

## Example
```bash
PYTHONPATH=backend python3 backend/tools/evaluate_v4.py --year-from 2025 --year-to 2027
python3 scripts/generate_scorecard.py --label "2026-02 Week30"
python3 scripts/check_accuracy_gate.py
```
