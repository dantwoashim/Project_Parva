# Evaluator Guide

## What to evaluate first
1. Astronomical core correctness (BS conversion + udaya tithi + panchanga).
2. Festival derivation explainability (`/festivals/{id}/explain`).
3. Personal stack usefulness (Personal Panchanga, Muhurta, Kundali).

## 10-minute demo flow
1. Open Festival Explorer and search `Dashain`.
2. Open detail page and click **Why this date?**
3. Open Panchanga page and change date to show recalculation.
4. Open Personal Panchanga and change coordinates.
5. Open Muhurta page and compare `general` vs `vivah` windows.
6. Open Kundali page and inspect Lagna + graha table.
7. Open iCal Feeds and generate a custom feed URL.

## Verification commands
From repo root (single command):
```bash
./scripts/release/run_month9_release_gates.sh
```

Manual equivalent:
```bash
PYTHONPATH=backend python3 -m pytest -q
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py
PYTHONPATH=backend python3 scripts/rules/ingest_rule_sources.py --check --target 300 --computed-target 300
PYTHONPATH=backend python3 scripts/generate_accuracy_report.py
PYTHONPATH=backend python3 scripts/generate_authority_dashboard.py
PYTHONPATH=backend python3 scripts/release/generate_month9_dossier.py
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

## Key evidence artifacts
- `/Users/rohanbasnet14/Documents/Project_Parva/reports/conformance_report.json`
- `/Users/rohanbasnet14/Documents/Project_Parva/reports/authority_dashboard.json`
- `/Users/rohanbasnet14/Documents/Project_Parva/reports/accuracy/annual_accuracy_2082.json`
- `/Users/rohanbasnet14/Documents/Project_Parva/reports/release/month9_dossier.json`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/public_beta/month9_release_dossier.md`

## Known constraints
- Public profile is v3.
- Experimental tracks are feature development tracks, disabled by default.
- Policy metadata is informational; local religious authority takes precedence.
