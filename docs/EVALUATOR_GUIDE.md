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
python scripts/release/check_repo_hygiene.py
python scripts/release/check_sdk_install.py
python -m pytest -q
python scripts/spec/run_conformance_tests.py
python scripts/release/check_contract_freeze.py
python scripts/release/generate_public_beta_artifacts.py --target 300 --computed-target 300
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
python scripts/run_browser_smoke.py
```

## Key evidence artifacts
- `reports/conformance_report.json` (generated artifact)
- `reports/authority_dashboard.json` (generated artifact)
- `reports/accuracy/annual_accuracy_2082.json` (generated artifact)
- `reports/release/month9_dossier.json` (generated artifact)
- `docs/public_beta/month9_release_dossier.md`
- `docs/UI_TEMPORAL_CARTOGRAPHY_SPEC.md`
- `docs/API_QUICKSTART.md`
- `docs/EMBED_GUIDE.md`

## Known constraints
- Public profile is v3.
- Experimental tracks are disabled by default.
- Public messaging should remain public-beta, explainable, and known-limits-first until stronger evidence gates are green.
- Policy metadata is informational; local religious authority takes precedence.
- Free-tier hosting may show occasional cold-start latency.
