# Project Parva Implementation Report

Generated: 2026-05-08

## 1. Existing Features Preserved

The platform boundary is preserved and documented in `docs/CURRENT_FEATURES.md`.

- BS/AD conversion, fiscal-year logic, enterprise calendar routes, holidays, festivals, panchanga, muhurta, kundali, reliability, provenance, frontend, SDK, deployment, and governance files remain in place.
- Existing `/v4/api/future-bs/*` APIs remain additive beside the new model-risk layer.
- Future unpublished outputs are labeled `computed_prediction_not_official`.

## 2. New Modules Added

- Computed posterior, precedent, prediction-set, perturbation, year-total, claim-readiness, Calendar VaR, and 2083 replay modules under `backend/app/future_bs`.
- Compatibility package paths under `backend/app/future_bs/challenger` and `backend/app/future_bs/finance`.
- Calendar Model-Risk service and route layer under `backend/app/services/calendar_model_risk_service.py` and `backend/app/api/calendar_model_risk_routes.py`.
- Active-learning queue writer at `backend/app/future_bs/active_learning_queue.py`.

## 3. New APIs Added

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

## 4. Scripts Added

- `scripts/future_bs/run_time_travel_backtest.py`
- `scripts/future_bs/replay_2083_ashwin.py`
- `scripts/future_bs/generate_claim_readiness_report.py`
- `scripts/future_bs/generate_residual_report.py`
- `scripts/future_bs/audit_external_bs_sheet.py`
- `scripts/future_bs/generate_calendar_var_report.py`

## 5. Data Artifacts Generated

- `data/future_bs/reports/claim_readiness_v7.json`
- `data/future_bs/reports/case_2083_ashwin_replay.json`
- `data/future_bs/reports/time_travel_official_v7.json`
- `data/future_bs/reports/residual_report_v7.md`
- `data/future_bs/reports/parva_shadow_audit_sample.xlsx`
- `data/future_bs/reports/parva_shadow_audit_sample.pdf`
- `data/future_bs/reports/parva_calendar_var_sample.pdf`
- `data/future_bs/reports/parva_calendar_var_sample.json`
- `data/future_bs/corpus/active_learning_queue.csv`

Local JPL kernels are configured but git-ignored: DE440 plus both DE441 split kernel files.

## 6. Tests Added

- Computed committee posterior, precedent tower, perturbation robustness, claim readiness, Calendar VaR, 2083 replay, false-green reporting, prediction artifact validity, external-sheet audit script, Calendar VaR script, and model-risk latency tests.
- Existing calendar platform regression tests remain in place.

## 7. Test Results

Latest backend gate runs:

```text
py -3.11 -m pytest -q tests\unit\future_bs\test_committee_rule_posterior.py tests\unit\future_bs\test_precedent_tower.py tests\unit\future_bs\test_perturbation_robustness.py tests\unit\future_bs\test_calendar_var.py tests\unit\future_bs\test_claim_readiness.py tests\accuracy\test_2083_ashwin_replay.py tests\accuracy\test_false_green_rate.py tests\accuracy\test_prediction_artifact_validity.py tests\integration\test_calendar_var_report.py tests\integration\test_external_sheet_audit.py tests\performance\test_calendar_model_risk_latency.py
14 passed in 5.10s

py -3.11 -m pytest -q
602 passed in 88.57s
```

Static and frontend gates:

```text
py -3.11 -m ruff check backend\app scripts tests
All checks passed.

npm run build
built successfully in 4.02s

npm run test
24 test files passed, 109 tests passed
```

## 8. Performance Results

Measured after the first pass with FastAPI `TestClient`:

- `/v4/api/future-bs/month-lengths/2112`: 73.47 ms
- `/v4/api/future-bs/backtest`: 818.67 ms
- `/v5/api/calendar-model-risk/prediction/2089/6`: 6.26 ms
- `/v5/api/calendar-model-risk/claim-readiness`: 868.58 ms

The focused latency tests also pass for prediction payload under 100 ms and claim readiness under 3 seconds.

## 9. Accuracy Benchmark Results

`data/future_bs/reports/claim_readiness_v7.json`:

- Official cases: 72
- Required official cases: 528
- Official-only top1 accuracy in strict holdout: 100.0%
- Green-zone accuracy in strict holdout: 100.0%
- Green-zone coverage in strict holdout: 91.67%
- False-green rate in strict holdout: 0.0
- Claim ready: false

`data/future_bs/reports/time_travel_official_v7.json`:

- Source policy: `official_only`
- Range: 2078-2083 BS
- Month cases: 72
- Rolling top1 accuracy: 87.5%
- Rolling green-zone accuracy: 94.74%
- Rolling green-zone coverage: 79.17%
- Rolling false-green rate: 0.052632
- Claim ready: false

## 10. 2083 Ashwin Replay Result

Generated `data/future_bs/reports/case_2083_ashwin_replay.json`.

- Train end: 2082 BS
- Target: Ashwin 2083
- Official/reference result: 31 days
- Pre-publication computed prediction: 31 days
- 95% prediction set: `[30, 31]`
- Static 30-day assumption failure mode: one-day month-end shift
- One-day interest exposure example: NPR 32,876.71 on NPR 100,000,000 at 12%
- Recommended policy: `override_ready_until_official_publication`

## 11. Invalid Future Year Total Summary

The future prediction artifact still contains 48 years with 364/367 totals. They are not treated as normal:

- `risk_label`: `RED`
- `claimable`: false
- `manual_review_required`: true
- reason: `invalid_or_exceptional_year_total`

The active-learning queue prioritizes these years for official/printed verification.

## 12. Claim-Readiness Summary

Current claim-readiness is false. The blockers are:

- Official/printed final-test corpus has 72 month cases; target is 528.
- 48 future BS years have invalid/exceptional totals.
- Rolling time-travel green-zone accuracy and coverage are below target.
- Rolling time-travel false-green rate is above target.

The system is complete enough to report the blocker honestly instead of making a 99%+ claim.

## 13. Known Limitations

- The official verified corpus is too small for a broad public 99%+ official accuracy claim.
- Rolling time-travel results do not yet meet the desired 99% green-zone target.
- The precomputed 2084-2200 artifact has invalid/exceptional year totals that require reconciliation or verified source review.
- PDF generation currently uses a dependency-light report writer; richer branded rendering can be added later.
- Future predictions remain computed operational guidance, not official calendar publication.

## 14. Remaining TODOs

- Expand the official/printed corpus toward 528+ verified month cases.
- Promote active-learning queue rows through source review.
- Improve future artifact generation so invalid year totals are either evidence-supported reconciliations or explicitly removed from claimable surfaces.
- Add richer report templates after the data posture is stronger.
- Continue residual work on rolling time-travel misses before any 99%+ positioning.

## 15. Exact Regeneration Commands

```powershell
py -3.11 scripts\download_jpl_kernel.py --kernel de440
py -3.11 scripts\download_jpl_kernel.py --kernel de441-part1
py -3.11 scripts\download_jpl_kernel.py --kernel de441-part2
py -3.11 scripts\future_bs\replay_2083_ashwin.py --out data\future_bs\reports\case_2083_ashwin_replay.json
py -3.11 scripts\future_bs\run_time_travel_backtest.py --source-policy official_only --start 2078 --end 2083 --out data\future_bs\reports\time_travel_official_v7.json
py -3.11 scripts\future_bs\generate_claim_readiness_report.py --out data\future_bs\reports\claim_readiness_v7.json
py -3.11 scripts\future_bs\generate_residual_report.py --out data\future_bs\reports\residual_report_v7.md
py -3.11 scripts\future_bs\audit_external_bs_sheet.py --sample --start 2084 --end 2200 --out data\future_bs\reports\parva_shadow_audit_sample.xlsx --pdf data\future_bs\reports\parva_shadow_audit_sample.pdf
py -3.11 scripts\future_bs\generate_calendar_var_report.py --sample --out data\future_bs\reports\parva_calendar_var_sample.pdf --json data\future_bs\reports\parva_calendar_var_sample.json
```

## 16. Exact Test Commands

```powershell
py -3.11 -m ruff check backend\app scripts tests
py -3.11 -m pytest -q
cd frontend
npm run build
npm run test
```

## 17. Safe Claims for InfoDevelopers Email

- Parva provides computed predictions, not official future publication.
- Parva can separate high-confidence months from risky months.
- Parva can audit an external future BS month-length sheet.
- Parva can estimate financial exposure of one-day mismatches.
- Parva can replay 2083 Ashwin-style failures before official publication and recommend an override-ready policy.

## 18. Unsafe Claims to Avoid

- Parva guarantees official future calendar to 2200 BS.
- Parva replaces the Panchanga Nirnayak Samiti.
- Parva's future predictions are official.
- Parva has achieved a claim-ready 99%+ rolling green-zone benchmark.

## Safe InfoDevelopers Positioning

Parva is not another copied future calendar table.
Parva is a complete Nepali calendar infrastructure platform with an independent Calendar Model-Risk Engine.
It computes future BS month lengths algorithmically, validates against source-labeled historical data, separates high-confidence predictions from risky months, compares against an external future month-length sheet, and estimates loan/interest exposure from one-day mismatches.
The strongest benchmark is whether Parva can predict or flag 2083 Ashwin-style failures before official panchanga publication.
All future outputs are computed_prediction_not_official and must be reconciled when official publication arrives.
