# Project Parva Implementation Report

Generated: 2026-05-08

## 1. Existing Features Preserved

Project Parva remains a complete Nepali calendar infrastructure project. The Future BS / Calendar Model-Risk work is additive and does not replace existing BS/AD conversion, fiscal year logic, known month-length lookup, holiday/calendar surfaces, panchanga-related routes, enterprise routes, frontend/demo files, SDK/client code, deployment files, or existing documentation.

Current preservation evidence:

- `python -m pytest tests/regression`
- Result: 4 passed in 2.99s

## 2. Operational Blockers Fixed

- Added artifact-backed report loading in `backend/app/future_bs/report_store.py`.
- Made claim readiness artifact-first by default in `backend/app/future_bs/claim_readiness.py`.
- Made `/v5/api/calendar-model-risk/claim-readiness` artifact-first.
- Made `/v5/api/calendar-model-risk/red-team/2083-ashwin` artifact-first.
- Added `/v5/api/calendar-model-risk/infodevelopers-readiness`.
- Updated 2083 replay script and backend logic so default execution uses cached/generated artifacts and only recomputes with an explicit force path.
- Allowed read-only use of trusted precomputed JPL DE440 cache even when local live JPL kernels are unavailable.
- Added top-level `publication_status: computed_prediction_not_official` to v5 prediction payloads.
- Added repo-local Python 3.11 handoff in `sitecustomize.py` so bare `python` commands inside this repo use the Python version declared by `pyproject.toml`.

## 3. Accuracy Loop Executed

The final accuracy loop was run with:

```powershell
python scripts\future_bs\run_accuracy_loop.py --final
```

Selected model:

- `parva_solar_civil_v1`

Best measured metrics from `data/future_bs/accuracy_lab/best_metrics.json`:

- Objective score: 1375.0001
- Overall top1 accuracy: 100.0%
- Green-zone accuracy: 100.0%
- Green-zone coverage: 91.67%
- False-green rate: 0.0%
- Wrong GREEN count: 0
- Invalid future year total rate: 0.0%
- Metric threshold passed: true
- Claim ready with sufficient corpus: false

Important interpretation: the metric target passes on the current strict official window, but the public 99%+ claim is not ready because the official verified corpus is too small.

## 4. Claim Readiness

Final claim readiness artifacts:

- `data/future_bs/reports/claim_readiness_v_final.json`
- `data/future_bs/accuracy_lab/accuracy_readiness_final.json`
- `data/future_bs/accuracy_lab/accuracy_readiness_final.md`

Current state:

- Claim ready 99 green-zone: false
- Claim ready 99 overall: false
- Official cases: 72
- Required official cases: 528
- Official-only top1 accuracy: 100.0%
- Green-zone accuracy: 100.0%
- Green-zone coverage: 91.67%
- False-green rate: 0.0%
- Invalid future year totals: 0

Blocker:

- The verified official/printed final-test corpus has 72 month cases; target is 528.

## 5. 2083 Ashwin Replay

Final replay artifacts:

- `data/future_bs/reports/case_2083_ashwin_replay_v_final.json`
- `data/future_bs/reports/case_2083_ashwin_replay_v_final.md`

Replay result:

- Train end: 2082 BS
- Target: Ashwin 2083
- Official/reference result: 31 days
- Parva pre-publication computed prediction: 31 days
- Prediction set 95: `[30, 31]`
- Risk label: YELLOW
- Static 30-day assumption failure mode: one-day month-end shift
- Example one-day interest exposure: NPR 32,876.71 on NPR 100,000,000 at 12%
- Recommended policy: `override_ready_until_official_publication`

Because the 95% prediction set has two values, the replay is intentionally YELLOW, not GREEN.

## 6. Future Year Totals

Final future prediction artifacts:

- `data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json`
- `data/future_bs/predictions/parva_future_bs_accuracy_best_claimable_subset.json`
- `data/future_bs/reports/invalid_year_total_reconciliation_v_final.json`

Result:

- Range: 2084-2200 BS
- Invalid 364/367 future year totals: 0
- Unsupported invalid totals would be marked RED/non-claimable by the verifier.

## 7. External Sheet Audit Sample

Generated files:

- `data/future_bs/infodevelopers_ready/sample_infodev_input_sheet.xlsx`
- `data/future_bs/reports/parva_shadow_audit_sample_v_final.xlsx`
- `data/future_bs/reports/parva_shadow_audit_sample_v_final.md`

The sample audit classifies agreements, disagreements, uncertain months, RED/non-claimable months, and review-needed cases. It does not claim the external sheet is wrong; it recommends review where model-risk evidence requires it.

## 8. Calendar Impact Sample

Generated files:

- `data/future_bs/reports/parva_calendar_var_sample_v_final.json`
- `data/future_bs/reports/parva_calendar_var_sample_v_final.md`

The sample is framed as a one-day schedule-impact and operational exposure estimate, not a guaranteed financial loss.

## 9. InfoDevelopers Package

Generated files:

- `data/future_bs/infodevelopers_ready/PARVA_INFODEVELOPERS_READINESS_SUMMARY.json`
- `data/future_bs/infodevelopers_ready/PARVA_INFODEVELOPERS_READINESS_SUMMARY.md`
- `docs/infodevelopers/INFODEVELOPERS_EXECUTIVE_SUMMARY.md`
- `docs/infodevelopers/INFODEVELOPERS_DEMO_SCRIPT.md`
- `docs/infodevelopers/SAFE_CLAIMS.md`
- `docs/infodevelopers/LIMITATIONS.md`
- `docs/infodevelopers/METHODOLOGY.md`

No final PDF files are claimed in this report. The verified final package uses JSON, Markdown, and XLSX artifacts.

## 10. Final Verification

Artifact verification:

```powershell
python scripts\future_bs\verify_final_artifacts.py
```

Result:

- `ok: true`
- Checked artifacts: 25
- Publication status: `computed_prediction_not_official`

Lint:

```powershell
py -3.11 -m ruff check backend\app scripts tests sitecustomize.py
```

Result:

- All checks passed.

Targeted required test command:

```powershell
python -m pytest tests/unit/future_bs tests/accuracy tests/artifacts tests/integration/test_calendar_model_risk_routes.py
```

Result:

- 64 passed in 4.01s

Existing route regression command:

```powershell
python -m pytest tests/regression
```

Result:

- 4 passed in 2.99s

Focused Future BS helper scripts were also run successfully:

```powershell
python scripts\future_bs\replay_2083_ashwin.py
python scripts\future_bs\run_model_search.py
python scripts\future_bs\search_civil_rules.py
python scripts\future_bs\tune_precedent_tower.py
python scripts\future_bs\train_sequence_model.py
python scripts\future_bs\tune_risk_thresholds.py
python scripts\future_bs\diagnose_mismatches.py
python scripts\future_bs\generate_accuracy_candidate_report.py
```

Full pytest and frontend npm tests were not rerun in this final pass.

## 11. API Smoke Results

Measured with FastAPI `TestClient` after final artifact generation:

- `/v5/api/calendar-model-risk/prediction/2089/6`: 200, 95.12 ms
- `/v5/api/calendar-model-risk/claim-readiness`: 200, 6.85 ms
- `/v5/api/calendar-model-risk/red-team/2083-ashwin`: 200, 6.49 ms
- `/v5/api/calendar-model-risk/infodevelopers-readiness`: 200, 15.86 ms

The artifact-backed routes are non-hanging under the final smoke test.

## 12. Commands To Regenerate

```powershell
python scripts\future_bs\run_accuracy_loop.py --final
python scripts\future_bs\generate_all_final_artifacts.py
python scripts\future_bs\verify_final_artifacts.py
python -m pytest tests/unit/future_bs tests/accuracy tests/artifacts tests/integration/test_calendar_model_risk_routes.py
```

Additional focused commands:

```powershell
python scripts\future_bs\replay_2083_ashwin.py
python scripts\future_bs\run_model_search.py
python scripts\future_bs\search_civil_rules.py
python scripts\future_bs\tune_precedent_tower.py
python scripts\future_bs\train_sequence_model.py
python scripts\future_bs\tune_risk_thresholds.py
python scripts\future_bs\diagnose_mismatches.py
python scripts\future_bs\generate_accuracy_candidate_report.py
```

## 13. Safe Claims

- Parva provides computed predictions, not official future publication.
- Parva can separate high-confidence months from risky months.
- Parva can audit an external future BS month-length sheet.
- Parva can estimate operational exposure from one-day month-length mismatches.
- Parva can replay 2083 Ashwin-style risks and recommend an override-ready policy before official publication.

## 14. Unsafe Claims

- Parva guarantees the official future calendar to 2200 BS.
- Parva replaces the Panchanga Nirnayak Samiti.
- Parva's future predictions are official.
- Parva has a public claim-ready 99%+ benchmark across a sufficiently large official corpus.

## 15. Known Limitations

- The official verified corpus remains too small for a broad public 99%+ accuracy claim.
- The current 100% rolling official result covers 72 official month cases, not the required 528 cases.
- Future outputs remain computed predictions and must be reconciled when official publication arrives.
- Final PDF generation was not included in the verified package; Markdown/JSON/XLSX fallbacks were generated and verified.

## 16. Remaining Work

- Expand the official/printed corpus toward 528+ verified month cases.
- Promote active-learning queue rows through source review.
- Re-run the accuracy lab whenever new verified rows are added.
- Add richer PDF rendering only after the data posture is stronger.

## Safe InfoDevelopers Positioning

Parva is not another copied future calendar table.
Parva is a complete Nepali calendar infrastructure platform with an independent Calendar Model-Risk Engine.
It computes future BS month lengths algorithmically, validates against source-labeled historical data, separates high-confidence predictions from risky months, compares against an external future month-length sheet, and estimates loan/interest exposure from one-day mismatches.
The strongest benchmark is whether Parva can predict or flag 2083 Ashwin-style failures before official panchanga publication.
All future outputs are computed_prediction_not_official and must be reconciled when official publication arrives.
