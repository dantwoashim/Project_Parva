# Project Parva Implementation Report

Generated: 2026-05-08

## Existing Features Preserved

The new work is additive. Existing calendar conversion, fiscal-year logic, holiday/calendar routes, panchanga-related surfaces, enterprise routes, frontend/demo files, SDK/client code, deployment files, and existing docs were not removed.

Verification run:

```powershell
python -m pytest tests/regression
```

Result: 4 passed.

## High-Trust Source Acquisition Summary

The high-trust acquisition pass attempted all requested source families and cached accessible public pages/files under `data/future_bs/raw_sources/`.

Generated outputs include:

- `data/future_bs/witnesses/new_high_trust_witnesses.csv`
- `data/future_bs/witnesses/new_high_trust_witnesses.jsonl`
- `data/future_bs/witnesses/rajpatra_witnesses.csv`
- `data/future_bs/witnesses/moha_holiday_witnesses.csv`
- `data/future_bs/witnesses/gorkhapatra_masthead_witnesses.csv`
- `data/future_bs/witnesses/archive_panchanga_witnesses.csv`
- `data/future_bs/witnesses/public_notice_witnesses.csv`
- `data/future_bs/witnesses/independent_newspaper_witnesses.csv`
- `data/future_bs/data_acquisition/high_trust_source_manifest.json`
- `data/future_bs/data_acquisition/new_source_coverage_report.json`
- `data/future_bs/data_acquisition/manual_acquisition_targets.csv`
- `data/future_bs/data_acquisition/library_publisher_request_plan.md`
- `data/future_bs/data_acquisition/request_email_nepali.md`
- `data/future_bs/data_acquisition/request_email_english.md`

Measured result:

- Source families attempted: 6
- Source attempts recorded: 52
- Successful cached public sources/pages/files: 31
- Failed or blocked attempts: 21
- Machine-clear new high-trust AD/BS witness rows: 0
- New Tier 1 rows: 0
- New Tier 2 rows: 0
- New Tier 3 rows: 0
- Rows promoted: 0

No source was promoted by inference. If a public page or PDF did not expose a machine-clear AD <-> BS month-start witness, it was cached/logged for manual review instead of being converted into calendar truth.

## Sources Attempted And Blockers

Attempted source families:

- Nepal Rajpatra / Department of Printing
- Ministry of Home Affairs public holiday notices
- Gorkhapatra public daily mastheads
- Archive.org printed panchanga/patro searches
- Public institution notice archives
- Independent newspaper e-paper families

Key blocker:

- The bounded public attempts did not yield additional machine-clear AD <-> BS month-start pairs. Several sources were accessible enough to cache, but the extracted text did not provide enough structured evidence to safely create new witness rows.

The exact attempt log is in:

- `data/future_bs/data_acquisition/source_attempts.jsonl`
- `data/future_bs/data_acquisition/failed_sources.jsonl`
- `data/future_bs/data_acquisition/new_source_coverage_report.md`

## Corpus Merge And Reconstruction

Merge result from `data/future_bs/data_acquisition/post_acquisition_delta_report.md`:

- Existing witness rows before merge: 4,022
- New high-trust rows available: 0
- Rows after merge: 4,022
- New rows added: 0
- Conflicts resolved: 0
- Conflicts after reconstruction: 83
- Official-claim usable month rows after: 62
- Printed verified witness rows after: 24
- Public daily witness rows after: 0

Reconstructed corpus state:

- Reconstructed month starts: 1,205
- Reconstructed month lengths: 1,200
- Complete reconstructed BS years: 100
- Medium/high complete years: 20
- Human-review queue rows: 857

Generated corpus outputs:

- `data/future_bs/corpus/reconstructed_month_starts.csv`
- `data/future_bs/corpus/reconstructed_month_lengths.csv`
- `data/future_bs/corpus/source_agreement_graph.json`
- `data/future_bs/corpus/month_start_confidence.csv`
- `data/future_bs/corpus/human_review_queue.csv`
- `data/future_bs/corpus/human_review_queue.md`
- `data/future_bs/corpus/corpus_quality_report.json`
- `data/future_bs/corpus/corpus_quality_report.md`

## Source-Policy Separation

Implemented strict source policies in `backend/app/future_bs/source_policy.py`.

Generated metrics:

- `data/future_bs/accuracy_lab/source_policy_metrics.json`
- `data/future_bs/accuracy_lab/official_strict_metrics.json`
- `data/future_bs/accuracy_lab/medium_high_training_metrics.json`
- `data/future_bs/accuracy_lab/all_witness_experimental_metrics.json`

Current policy cases:

- `official_strict`: 62 month cases
- `medium_high_training`: 391 month cases
- `all_witness_experimental`: 1,112 month cases

Tier 5/6 witnesses are excluded from `official_strict` claim-readiness.

## Official Witness Mismatch Explanation

The witness corpus contains 72 official witness rows, but the strict official claim policy currently admits 62 month cases. The gap comes from conflict handling, verification status, and invalid/fragile reconstructed rows. Weak or conflicted evidence is not counted as official-claim usable.

Excluded reconstructed rows:

- 2091-08
- 2091-12
- 2092-09
- 2095-08
- 2095-12

Generated exclusion files:

- `data/future_bs/accuracy_lab/excluded_rows.json`
- `data/future_bs/accuracy_lab/excluded_rows.md`

## Accuracy Architecture Executed

The full architecture pass was wired into:

```powershell
python scripts/future_bs/run_accuracy_loop.py --final
```

It generated:

- Weak-label fusion: `data/future_bs/accuracy_lab/weak_label_fusion_results.json`
- Source independence graph: `data/future_bs/accuracy_lab/source_independence_graph.json`
- Source-copy report: `data/future_bs/accuracy_lab/source_copy_detection_report.md`
- Latent truth model: `data/future_bs/accuracy_lab/latent_truth_month_starts.json`
- Month-start corpus/features: `data/future_bs/accuracy_lab/month_start_corpus.json`, `data/future_bs/accuracy_lab/month_start_features.json`
- Hidden-rule inversion: `data/future_bs/accuracy_lab/hidden_rule_inversion.json`
- Regime detection: `data/future_bs/accuracy_lab/regime_change_report.json`
- Program synthesis: `data/future_bs/accuracy_lab/program_synthesis_results.json`, `data/future_bs/accuracy_lab/best_rule_program.json`
- Precedent/witness report: `data/future_bs/accuracy_lab/precedent_tower_report.md`
- Hard-case benchmark: `data/future_bs/accuracy_lab/hard_case_benchmark.json`
- Month-start lattice decoder: `data/future_bs/accuracy_lab/month_start_lattice_decoding.json`
- GREEN certification: `data/future_bs/accuracy_lab/green_certification_report.json`
- Risk threshold report: `data/future_bs/accuracy_lab/risk_threshold_report.md`
- Human review promotion plan: `data/future_bs/accuracy_lab/human_review_promotion_plan.csv`

## Model Search And Metrics

Selected model: `parva_solar_civil_v1`

Best measured metrics from `data/future_bs/accuracy_lab/best_metrics.json`:

- Objective score: 1375.0001
- Overall top1 accuracy: 100.0%
- Green-zone accuracy: 100.0%
- Green-zone coverage: 91.67%
- False-green rate: 0.0
- Wrong GREEN count: 0
- Invalid future year total rate: 0.0
- Metric threshold passed: true
- Claim ready with sufficient corpus: false

Interpretation: the current strict official window passes the metric threshold, but it is only 62 strict official month cases in the architecture output. The 99% public claim remains blocked by corpus size.

## Claim Readiness

Current final readiness from `data/future_bs/accuracy_lab/accuracy_readiness_final.json`:

- Claim ready 99 green-zone: false
- Claim ready 99 overall: false
- Official strict cases: 62
- Required official cases: 528
- Wrong GREEN count: 0
- Green-zone accuracy: 100.0%
- Green-zone coverage: 91.67%

Blockers:

- Official strict cases are below the required threshold.
- More Tier 1 or strong reviewed Tier 2 evidence is required before a public 99%+ claim is supportable.

## Human Review Promotion Plan

Generated:

- `data/future_bs/accuracy_lab/human_review_promotion_plan.csv`
- `data/future_bs/accuracy_lab/human_review_promotion_plan.md`

The plan ranks the top 100 rows by expected accuracy and claim-readiness gain. Highest priority remains source disagreements, Ashwin/Kartik boundary rows, and weak/fragile reconstructed rows.

## Commands Run

```powershell
python scripts/future_bs/research_and_collect_high_trust_sources.py
python scripts/future_bs/merge_high_trust_witnesses.py
python scripts/future_bs/reconstruct_month_starts.py
python scripts/future_bs/build_source_agreement_graph.py
python scripts/future_bs/audit_witness_corpus.py
python scripts/future_bs/run_accuracy_loop.py --final
python scripts/future_bs/run_model_search.py
python scripts/future_bs/tune_risk_thresholds.py
python scripts/future_bs/generate_human_review_promotion_plan.py
py -3.11 -m ruff check backend\app\future_bs scripts\future_bs tests\data_acquisition tests\accuracy tests\future_bs
python -m pytest tests/data_acquisition
python -m pytest tests/accuracy
python -m pytest tests/future_bs/test_weak_label_fusion.py tests/future_bs/test_source_independence.py tests/future_bs/test_latent_truth_model.py tests/future_bs/test_regime_change_detection.py tests/future_bs/test_month_start_lattice_decoder.py tests/future_bs/test_green_certification.py tests/future_bs/test_human_review_promotion_plan.py
python -m pytest tests/regression
```

One parallel run of `run_model_search.py` raced with `tune_risk_thresholds.py` while both wrote the same accuracy artifact and failed with a Windows replace permission error. The command was rerun alone and passed.

## Test Results

- `tests/data_acquisition`: 12 passed
- `tests/accuracy`: 24 passed
- Focused `tests/future_bs` architecture tests: 7 passed
- `tests/regression`: 4 passed
- Ruff check: passed after import formatting fixes

Full repository `pytest` was not run in this final pass.

## Known Limitations

- No additional machine-clear high-trust AD/BS witness rows were extracted from the bounded public source attempts.
- Official-grade claim-readiness remains blocked by strict corpus size.
- The current 100% green-zone result should be read as a measured result on the available strict window, not a broad official proof.
- Public/weak sources help reconstruction, residual analysis, and active learning, but do not establish official future calendar truth.
- Future outputs remain `computed_prediction_not_official` and must be reconciled when official publication arrives.

## Safe Claims

- Parva provides computed future BS predictions, not official future publication.
- Parva separates official, medium/high, and weak experimental evidence.
- Parva can identify high-confidence months, risky months, conflicts, and manual-review targets.
- Parva can run an independent source-policy accuracy architecture over a source-labeled witness corpus.
- Parva can show exactly why a 99%+ public claim is or is not supported.

## Unsafe Claims

- Parva guarantees the official future calendar.
- Parva replaces official panchanga publication.
- Weak public/software witnesses prove official accuracy.
- The current corpus supports a blanket public 99%+ future-calendar claim.
