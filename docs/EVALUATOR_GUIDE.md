# Evaluator Guide

## What to evaluate first
1. Astronomical core correctness (BS conversion + udaya tithi + panchanga).
2. Festival derivation explainability (`/festivals/{id}/explain`).
3. Temporal Cartography UX (Observance Mode vs Authority Mode).
4. Personal stack usefulness (Personal Panchanga, Muhurta, Kundali).

## 10-minute demo flow (updated)
1. Open `/` (Temporal Compass).
2. In **Observance Mode**, show daily cockpit: BS date, tithi, horizon strip, today festivals.
3. Switch to **Authority Mode** using top-right toggle and show trace/provenance metadata.
4. Open `/festivals` and show month-grouped timeline ribbon + quality markers.
5. Open a festival detail and show canonical `ritual_sequence.days[]` rendering.
6. Open `/panchanga` and change date to show recalculation + glossary explanation.
7. Open `/muhurta` and show 24h heatmap + reason codes.
8. Open `/kundali` and show interactive graph + insight sidebar.
9. Open `/feeds` and generate a custom iCal URL.

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
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/UI_TEMPORAL_CARTOGRAPHY_SPEC.md`

## Known constraints
- Public profile is v3.
- Experimental tracks are disabled by default.
- Policy metadata is informational; local religious authority takes precedence.
- Free-tier hosting may show occasional cold-start latency.
