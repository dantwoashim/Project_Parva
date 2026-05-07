# Project Parva One-Shot Implementation Report

Generated: 2026-05-08

## 1. Existing Features Found and Preserved

The existing Parva platform remains intact. Inventory is documented in `docs/CURRENT_FEATURES.md`.

Preserved surfaces include:

- BS/AD conversion and known-year BS lookup routes.
- Enterprise fiscal-year, BS month, business-day, bulk-convert, and validation routes.
- Holiday, festival, observance, feed, iCal, and integration surfaces.
- Panchanga, tithi, muhurta, personal panchanga, temporal compass, kundali, and proof-capsule APIs.
- Reliability, provenance, public artifact, cache, engine, policy, and spec endpoints.
- React/Vite frontend and Python SDK import surface.
- Docker, Cloud Run, Render, Cloud Build, release, governance, security, and precompute scripts.

## 2. New Modules Added

- `backend/app/future_bs/year_total_gate.py`
- `backend/app/future_bs/prediction_sets.py`
- `backend/app/future_bs/perturbation_robustness.py`
- `backend/app/future_bs/source_trust.py`
- `backend/app/future_bs/claim_readiness.py`
- `backend/app/future_bs/calendar_var.py`
- `backend/app/future_bs/red_team_2083.py`
- `backend/app/services/calendar_model_risk_service.py`
- `backend/app/api/calendar_model_risk_routes.py`

Existing future-BS modules were extended without replacing the v6 predictor.

## 3. APIs Added

New public model-risk routes:

- `GET /v5/api/calendar-model-risk/capabilities`
- `GET /v5/api/calendar-model-risk/prediction/{bs_year}/{month}`
- `GET /v5/api/calendar-model-risk/prediction-set/{bs_year}/{month}`
- `GET /v5/api/calendar-model-risk/committee-posterior/{bs_year}/{month}`
- `GET /v5/api/calendar-model-risk/perturbation-robustness/{bs_year}/{month}`
- `POST /v5/api/calendar-model-risk/audit-external-sheet`
- `POST /v5/api/calendar-model-risk/calendar-var`
- `POST /v5/api/calendar-model-risk/stress-test`
- `GET /v5/api/calendar-model-risk/red-team/2083-ashwin`
- `GET /v5/api/calendar-model-risk/claim-readiness`
- `GET /v5/api/calendar-model-risk/reports/{report_id}`

Existing `/v4/api/future-bs/*` routes remain available.

## 4. Scripts Added

- `scripts/future_bs/run_time_travel_backtest.py`
- `scripts/future_bs/replay_2083_ashwin.py`
- `scripts/future_bs/generate_claim_readiness_report.py`

The existing `scripts/download_jpl_kernel.py` now supports named presets:

- `--kernel de440`
- `--kernel de441-part1`
- `--kernel de441-part2`

## 5. Data Artifacts Generated

- `data/future_bs/reports/claim_readiness_v7.json`
- `data/future_bs/reports/case_2083_ashwin_replay.json`
- `data/future_bs/reports/time_travel_official_v7.json`

Local JPL kernels are configured but git-ignored:

- `data/ephemeris/jpl/de440.bsp`
- `data/ephemeris/jpl/de441_part-1.bsp`
- `data/ephemeris/jpl/de441_part-2.bsp`

## 6. Tests Added

- `tests/unit/future_bs/test_year_total_gate.py`
- `tests/unit/future_bs/test_prediction_sets.py`
- `tests/accuracy/test_future_year_total_gate.py`
- `tests/integration/test_calendar_model_risk_routes.py`
- `tests/regression/test_existing_calendar_platform_routes.py`

The frontend test environment shim was hardened so jsdom local/session storage remains complete after tests that replace it with partial mocks.

## 7. Test Results

Backend:

```text
py -3.11 -m ruff check backend\app scripts tests
All checks passed.

py -3.11 -m pytest -q
588 passed in 80.40s
```

Frontend:

```text
npm run build
vite build completed successfully in 2.87s

npm run test
24 test files passed, 109 tests passed
```

## 8. Performance Results

Measured with FastAPI `TestClient`:

- `/v4/api/future-bs/month-lengths/2112`: 73.47 ms
- `/v4/api/future-bs/backtest`: 818.67 ms
- `/v5/api/calendar-model-risk/prediction/2089/6`: 6.26 ms
- `/v5/api/calendar-model-risk/claim-readiness`: 868.58 ms

The default backtest route is under the 3 second target.

## 9. Accuracy Benchmark Results

Generated `data/future_bs/reports/time_travel_official_v7.json`:

- Source policy: `official_only`
- Train start: 2000 BS
- Test range: 2078-2083 BS
- Months tested: 72

Generated `data/future_bs/reports/claim_readiness_v7.json` keeps the broad 99% claim locked because the final-test official/printed corpus is still below the required 528 month cases.

## 10. 2083 Ashwin Replay Result

Generated `data/future_bs/reports/case_2083_ashwin_replay.json`.

Summary:

- Case id: `PARVA-REDTEAM-2083-ASHWIN`
- Train end: 2082 BS
- Target: Ashwin 2083
- Parva pre-publication prediction: 31 days
- Publication status: `computed_prediction_not_official`
- Recommended policy: `override_ready_until_official_publication`

## 11. Known Limitations

- The official verified corpus is still too small for a broad public 99%+ official accuracy claim.
- The model is a computed prediction system, not an official calendar publication.
- Third-party and legacy reference rows remain comparison/stress-test evidence, not final official truth.
- Calendar VaR is an operational risk estimate, not legal, tax, regulatory, or accounting advice.
- DE441 is installed for local cross-check work, but the production adapter still uses the existing DE440-style JPL adapter path.

## 12. Remaining TODOs

- Expand official/printed source corpus toward 528+ final-test month cases.
- Add full OCR and dual-review source promotion workflow.
- Add richer empirical confidence calibration and false-green reporting from larger source-strict corpora.
- Generate PDF/XLSX model-risk reports once report rendering dependencies and templates are finalized.
- Wire a dedicated DE441 adapter class if production behavior should select DE441 directly rather than use it as a local cross-check kernel.

## 13. Exact Regeneration Commands

```powershell
py -3.11 scripts\download_jpl_kernel.py --kernel de440
py -3.11 scripts\download_jpl_kernel.py --kernel de441-part1
py -3.11 scripts\download_jpl_kernel.py --kernel de441-part2
py -3.11 scripts\future_bs\generate_claim_readiness_report.py --out data\future_bs\reports\claim_readiness_v7.json
py -3.11 scripts\future_bs\replay_2083_ashwin.py --out data\future_bs\reports\case_2083_ashwin_replay.json
py -3.11 scripts\future_bs\run_time_travel_backtest.py --source-policy official_only --train-start 2000 --start 2078 --end 2083 --out data\future_bs\reports\time_travel_official_v7.json
```

## 14. Exact Test Commands

```powershell
py -3.11 -m ruff check backend\app scripts tests
py -3.11 -m pytest -q
cd frontend
npm run build
npm run test
```

## 15. Safe InfoDevelopers Email Claims

- Parva is a complete Nepali calendar infrastructure platform with an additive Calendar Model-Risk Engine.
- Parva can independently compute future BS month-length predictions and mark every unpublished future output as `computed_prediction_not_official`.
- Parva can compare an external Excel/CSV future calendar sheet month-by-month and classify disagreements by confidence and risk.
- Parva can estimate loan/interest exposure from one-day month-length mismatches.
- Parva includes a 2083 Ashwin red-team replay showing whether the system would predict or flag the risky month before official publication.
- Parva does not claim to replace official panchanga publication or guarantee official future accuracy to 2200 BS.
