# Project Parva Implementation Report

Generated: 2026-05-08

## 1. Existing Features Preserved

The platform boundary is preserved and documented in `docs/CURRENT_FEATURES.md`.

- BS/AD conversion, fiscal-year logic, enterprise calendar routes, holidays, festivals, panchanga, muhurta, kundali, reliability, provenance, frontend, SDK, deployment, and governance files remain in place.
- Existing `/v4/api/future-bs/*` APIs remain additive beside the new model-risk layer.
- Future unpublished outputs are labeled `computed_prediction_not_official`.

## 2. New Modules Added

- Computed posterior, precedent, prediction-set, perturbation, year-total, claim-readiness, Calendar VaR, and 2083 replay modules under `backend/app/future_bs`.
- Accuracy objective, risk thresholds, sequence decoder, and accuracy-lab orchestration under `backend/app/future_bs`.
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
- `scripts/future_bs/accuracy_lab.py`
- `scripts/future_bs/run_accuracy_loop.py`
- `scripts/future_bs/run_model_search.py`
- `scripts/future_bs/search_civil_rules.py`
- `scripts/future_bs/search_ayanamsha_offsets.py`
- `scripts/future_bs/tune_precedent_tower.py`
- `scripts/future_bs/train_sequence_model.py`
- `scripts/future_bs/tune_risk_thresholds.py`
- `scripts/future_bs/diagnose_mismatches.py`
- `scripts/future_bs/generate_accuracy_candidate_report.py`
- `scripts/future_bs/calibrate_probabilities.py`

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
- `data/future_bs/accuracy_lab/best_model_config.json`
- `data/future_bs/accuracy_lab/best_metrics.json`
- `data/future_bs/accuracy_lab/model_search_history.json`
- `data/future_bs/accuracy_lab/threshold_search_history.json`
- `data/future_bs/accuracy_lab/civil_rule_search_results.json`
- `data/future_bs/accuracy_lab/best_civil_rule_table.json`
- `data/future_bs/accuracy_lab/precedent_tower_search_results.json`
- `data/future_bs/accuracy_lab/best_precedent_config.json`
- `data/future_bs/accuracy_lab/probability_calibration_report.json`
- `data/future_bs/accuracy_lab/corpus_quality_report.json`
- `data/future_bs/accuracy_lab/residual_analysis.json`
- `data/future_bs/accuracy_lab/residual_analysis.md`
- `data/future_bs/accuracy_lab/active_learning_queue.csv`
- `data/future_bs/accuracy_lab/accuracy_readiness_final.json`
- `data/future_bs/accuracy_lab/accuracy_readiness_final.md`
- `data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json`
- `data/future_bs/predictions/parva_future_bs_accuracy_best_claimable_subset.json`

Local JPL kernels are configured but git-ignored: DE440 plus both DE441 split kernel files.

## 6. Tests Added

- Computed committee posterior, precedent tower, perturbation robustness, claim readiness, Calendar VaR, objective scoring, sequence decoding, accuracy-lab final run, 2083 replay, false-green reporting, prediction artifact validity, external-sheet audit script, Calendar VaR script, and model-risk latency tests.
- Existing calendar platform regression tests remain in place.

## 7. Test Results

Latest backend gate runs:

```text
py -3.11 -m pytest -q tests\unit\future_bs\test_committee_rule_posterior.py tests\unit\future_bs\test_precedent_tower.py tests\unit\future_bs\test_perturbation_robustness.py tests\unit\future_bs\test_calendar_var.py tests\unit\future_bs\test_claim_readiness.py tests\accuracy\test_2083_ashwin_replay.py tests\accuracy\test_false_green_rate.py tests\accuracy\test_prediction_artifact_validity.py tests\integration\test_calendar_var_report.py tests\integration\test_external_sheet_audit.py tests\performance\test_calendar_model_risk_latency.py
14 passed in 5.10s

py -3.11 -m pytest -q
606 passed in 80.67s
```

Static and frontend gates:

```text
py -3.11 -m ruff check backend\app scripts tests
All checks passed.

npm run build
built successfully in 3.53s

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

Selected model from `data/future_bs/accuracy_lab/best_model_config.json`:

- Best candidate: `parva_solar_civil_v1`
- Rejected candidate: `solar_statistical_stack_holdout` because it produced wrong GREEN predictions on the official rolling window.
- Objective: false-confidence first, then coverage, then top1.

`data/future_bs/reports/time_travel_official_v7.json`:

- Source policy: `official_only`
- Range: 2078-2083 BS
- Month cases: 72
- Rolling top1 accuracy: 100.0%
- Rolling green-zone accuracy: 100.0%
- Rolling green-zone coverage: 91.67%
- Rolling false-green rate: 0.0
- Wrong GREEN count: 0
- Claim ready: false

## 10. 2083 Ashwin Replay Result

Generated `data/future_bs/reports/case_2083_ashwin_replay.json`.

- Train end: 2082 BS
- Target: Ashwin 2083
- Official/reference result: 31 days
- Pre-publication computed prediction: 31 days
- 95% prediction set: `[30, 31]`
- Risk label: `YELLOW`
- Static 30-day assumption failure mode: one-day month-end shift
- One-day interest exposure example: NPR 32,876.71 on NPR 100,000,000 at 12%
- Recommended policy: `override_ready_until_official_publication`

## 11. Invalid Future Year Total Summary

The selected best prediction artifact no longer contains invalid 364/367 totals:

- Artifact: `data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json`
- Range: 2084-2200 BS
- Invalid future year totals: 0
- Decoder: year-level dynamic programming over supported month candidates with allowed totals `{365, 366}`

The old v6 artifact remains historical comparison material, but the precomputed store now prefers the selected best artifact when it exists.

## 12. Claim-Readiness Summary

Current claim-readiness is false. The blockers are:

- Official/printed final-test corpus has 72 month cases; target is 528.
- The current rolling official benchmark satisfies the green-zone target, but the verified source count is too small for a public 99%+ claim.

The system is complete enough to report the blocker honestly instead of making a 99%+ claim.

## 13. Known Limitations

- The official verified corpus is too small for a broad public 99%+ official accuracy claim.
- The current 100% rolling official result covers only 72 official month cases.
- Future outputs remain computed predictions and need reconciliation when official publication arrives.
- PDF generation currently uses a dependency-light report writer; richer branded rendering can be added later.

## 14. Remaining TODOs

- Expand the official/printed corpus toward 528+ verified month cases.
- Promote active-learning queue rows through source review.
- Add richer report templates after the data posture is stronger.
- Re-run the accuracy lab whenever new official/printed source rows are promoted.

## 15. Exact Regeneration Commands

```powershell
py -3.11 scripts\download_jpl_kernel.py --kernel de440
py -3.11 scripts\download_jpl_kernel.py --kernel de441-part1
py -3.11 scripts\download_jpl_kernel.py --kernel de441-part2
python scripts\future_bs\run_accuracy_loop.py --final
python scripts\future_bs\run_model_search.py
python scripts\future_bs\search_civil_rules.py
python scripts\future_bs\tune_precedent_tower.py
python scripts\future_bs\train_sequence_model.py
python scripts\future_bs\tune_risk_thresholds.py
python scripts\future_bs\diagnose_mismatches.py
python scripts\future_bs\generate_accuracy_candidate_report.py
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
