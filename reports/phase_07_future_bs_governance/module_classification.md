# Phase 07 Future-BS Module Classification

Generated for the red-check closure sprint on 2026-05-14.

Scope: classify the current Future-BS routes, backend modules, scripts, tests,
documentation, and artifacts so public verification can distinguish
metadata-only public surfaces from private/research exact-output work.

Public rule: exact unpublished Future-BS outputs remain private and must keep
`publication_status = computed_prediction_not_official`. Public profiles may
expose only capability, methodology, source-policy, risk-label, and aggregate
validation metadata.

| Path | Classification | Public allowed? | Data dependency | Claim risk | Action |
| --- | --- | --- | --- | --- | --- |
| `backend/app/api/future_bs_routes.py` | public_preview_risk | Metadata-only endpoints yes; exact-output endpoints no | Route profile, experimental/research flags, admin/API-key auth | High if private routes are mounted publicly | Keep `/v4/api/future-bs/capabilities` and `/v5/api/calendar-model-risk/capabilities` public-safe; keep exact routes behind research/private gates. |
| `backend/app/services/future_bs_service.py` | research_private | No | Future-BS engine outputs and comparison helpers | High: exact future payloads can be misread as official | Use only from guarded research-private routes. |
| `backend/app/services/calendar_model_risk_service.py` | research_private | Capabilities payload only | Future-BS prediction, Calendar VaR, stress, loan-impact helpers | High for financial/legal misuse | Keep capabilities public-safe; keep prediction, audit, stress, and loan-impact paths private. |
| `backend/app/future_bs/models.py` | public_safe_metadata | Yes, for method/version labels only | Static model metadata | Medium: version labels can be overstated | Use for labels and reproducibility, not authority claims. |
| `backend/app/future_bs/source_policy.py` | public_safe_metadata | Yes | Source-tier policy metadata | Medium | Public docs may summarize tier policy. |
| `backend/app/future_bs/source_registry.py` | public_preview_risk | Public summaries only | Public source registry plus local policy state | Medium | Avoid exposing private source archive paths. |
| `backend/app/future_bs/precomputed_store.py` | generated_artifact_required | No | Generated precomputed prediction artifacts | High | Keep exact generated predictions out of public profiles and docs. |
| `backend/app/future_bs/backtest.py` | wide_corpus_required | No | Official holdout and wider historical corpus inputs | Medium | Public lane may run only public-data holdout tests; broad corpus runs stay explicit. |
| `backend/app/future_bs/accuracy.py` | wide_corpus_required | No | Backtest and corpus metrics | Medium | Do not turn broad stress metrics into official claims. |
| `backend/app/future_bs/accuracy_lab.py` | experimental | No | Research scoring experiments | High | Keep out of public runtime and public OpenAPI. |
| `backend/app/future_bs/accuracy_architecture.py` | experimental | No | Research model architecture scoring | High | Keep as research-only implementation detail. |
| `backend/app/future_bs/accuracy_objective.py` | experimental | No | Research optimization objectives | Medium | Keep research/private. |
| `backend/app/future_bs/ayanamsha.py` | public_preview_risk | No exact outputs | Astronomical method assumptions | Medium | Mention only as methodology where needed. |
| `backend/app/future_bs/ayanamsha_calibration.py` | research_private | No | Calibration candidates and evaluation data | High | Keep private/research. |
| `backend/app/future_bs/boundary_risk.py` | public_preview_risk | Metadata only | Risk labels and boundary heuristics | Medium | Public-safe only as risk vocabulary. |
| `backend/app/future_bs/calendar_var.py` | research_private | No | Schedule/financial impact scenarios | High: financial misuse | Keep behind review-required research/private routes. |
| `backend/app/future_bs/calibration.py` | research_private | No | Calibration corpus | High | Keep private. |
| `backend/app/future_bs/challenger/*` | private_source_required | No | External sheets, comparison workflows, source audits | High | Keep out of public routes and SDK defaults. |
| `backend/app/future_bs/corpus.py` | private_source_required | No | Source corpus rows and archive metadata | High | Do not expose local archive paths. |
| `backend/app/future_bs/data_acquisition.py` | private_source_required | No | Acquisition sources and local source files | High | Local operator tool only. |
| `backend/app/future_bs/ephemeris/*` | generated_artifact_required | No | Local ephemeris kernels or astronomy adapters | Medium | Public verification must not require private/local kernels. |
| `backend/app/future_bs/exports.py` | research_private | No | Exact prediction/export artifacts | High | Keep authenticated/private only. |
| `backend/app/future_bs/finance/*` | research_private | No | Financial stress and interest-impact simulations | High | Require review-required semantics; no public claims. |
| `backend/app/future_bs/hard_cases/*` | experimental | No | Adversarial/generated hard-case benchmarks | Medium | Research-only stress testing. |
| `backend/app/future_bs/high_trust_acquisition.py` | private_source_required | No | Source collection workflows | High | Keep private/operator-only. |
| `backend/app/future_bs/loan_impact.py` | research_private | No | Loan schedule impact scenarios | High | Never present as banking authority or approval. |
| `backend/app/future_bs/market_shadow.py` | experimental | No | Shadow-market comparison data | High | Research/private only. |
| `backend/app/future_bs/model_search/*` | experimental | No | Generated model search outputs | Medium | Keep out of public runtime. |
| `backend/app/future_bs/month_start/*` | wide_corpus_required | No | Month-start inversion corpus and features | Medium | Research lane only unless reduced to public methodology text. |
| `backend/app/future_bs/precedent/*` | research_private | No | Witness precedent and source evidence | High | Avoid public source-path leakage. |
| `backend/app/future_bs/program_synthesis/*` | experimental | No | Program/rule search experiments | Medium | Research/private only. |
| `backend/app/future_bs/red_team_2083.py` | research_artifact | No | Generated replay/proof artifact | Medium | Keep as policy artifact/test; do not expose exact future predictions publicly. |
| `backend/app/future_bs/regime/*` | research_artifact | No | Regime detection/model artifacts | Medium | Research lane only. |
| `backend/app/future_bs/regime_ensemble.py` | research_artifact | No | Generated/reconciled prediction sets | High | Keep exact outputs private. |
| `backend/app/future_bs/report_store.py` | generated_artifact_required | No | Generated report storage | High | Public routes must not read private reports. |
| `backend/app/future_bs/residual_analysis.py` | research_artifact | No | Residual rows and model diagnostics | High | Keep private/research. |
| `backend/app/future_bs/risk/*` | public_safe_metadata | Metadata only | Risk labels and reason code policy | Medium | Public-safe as labels/vocabulary only. |
| `backend/app/future_bs/rule_inversion/*` | research_artifact | No | Inversion workbench outputs | Medium | Research lane only. |
| `backend/app/future_bs/sequence/*` | research_artifact | No | Lattice/sequence model artifacts | Medium | Research lane only. |
| `backend/app/future_bs/truth_fusion/*` | research_private | No | Source reliability/fusion/copy-detection data | High | Keep private unless aggregated and path-scrubbed. |
| `scripts/check_future_bs_public_leakage.py` | public_safe_metadata | Yes | Config and route/profile checks | Low | Keep in public verification gate. |
| `scripts/precompute_future_bs_predictions.py` | generated_artifact_required | No | Generated exact prediction artifacts | High | Operator/research command only. |
| `scripts/backtest_future_bs_model.py` | wide_corpus_required | No | Backtest corpus | Medium | Run intentionally in research/wide-corpus lane. |
| `scripts/calibrate_future_bs_rules.py` | research_artifact | No | Calibration outputs | Medium | Research lane only. |
| `scripts/export_future_bs_predictions.py` | research_private | No | Exact prediction exports | High | Never public by default. |
| `scripts/future_bs/*.py` | private_source_required | No | Collection, parsing, calibration, report, and model-search inputs | High | Keep as local operator/research tooling. |
| `docs/future_bs/RESEARCH_BOUNDARY.md` | public_safe_metadata | Yes | Public policy text | Low | Keep explicit public/private boundary. |
| `docs/future_bs/PUBLIC_CLAIMS_POLICY.md` | public_safe_metadata | Yes | Public policy text | Low | Keep overclaim guardrails current. |
| `docs/future_bs/PRIVATE_DATA_POLICY.md` | public_safe_metadata | Yes | Public policy text | Low | Keep private data boundary explicit. |
| `docs/future_bs/ACCURACY_REPRODUCIBILITY.md` | public_preview_risk | Yes, with limits | Public reproducibility instructions and research lane commands | Medium | Separate public holdout from wide/private corpus runs. |
| `docs/future_bs/WRONG_GREEN_POLICY.md` | public_safe_metadata | Yes | Public policy text | Low | Keep wrong-green rules public. |
| `docs/future_bs/MODEL_REGISTRY.md` | public_preview_risk | Yes, metadata only | Model/version metadata | Medium | Avoid exact future outputs or authority claims. |
| `docs/future_bs/*.md` | public_safe_metadata | Yes, when claim-safe | Public methodology, limitations, source policy, API boundary | Medium | Keep scanned by leakage checker. |
| `data/future_bs/public/official_holdout_2078_2083.csv` | public_safe_metadata | Yes | Public official-verified holdout window | Medium | Supports limited validation only, not future authority. |
| `data/future_bs/public/source_tier_schema.json` | public_safe_metadata | Yes | Public schema metadata | Low | Public-safe. |
| `data/future_bs/benchmarks/official_holdout_v1.csv` | public_safe_metadata | Yes | Public benchmark/holdout data | Medium | Use for limited official-window metrics only. |
| `data/future_bs/benchmarks/accuracy_thresholds.json` | public_safe_metadata | Yes | Claim threshold metadata | Medium | Keep thresholds conservative. |
| `data/future_bs/examples/*` | public_safe_metadata | Yes | Example sheet/schema data | Low | Keep sample-only; no official claims. |
| `data/future_bs/private/README.md` | private_source_required | No | Boundary placeholder for private artifacts | Low | Keep as private-data boundary marker. |
| `data/future_bs/astronomy/solar_ingress_events_sample.json` | public_preview_risk | Yes, sample only | Sample astronomy events | Medium | Do not treat as full ephemeris authority. |
| `data/ephemeris/jpl/` | private_source_required | No | Local JPL kernels | Medium | Public verification must not require these local kernels. |
| `reports/phase_07_future_bs_governance/module_classification.md` | public_safe_metadata | Yes | This classification report | Low | Keep non-empty and updated when Future-BS surfaces change. |
| `reports/phase_08_performance_sre/latency_baseline.json` | generated_artifact_required | Yes, generated report | Public route latency smoke output | Low | Regenerate with the public-reference smoke command. |
| `docs/api-docs/openapi.json` | public_preview_risk | Yes | Static public OpenAPI mirror | High if private routes leak | Regenerate and check drift after route changes. |
| `docs/api-docs/openapi.public-reference.json` | public_preview_risk | Yes | Public-reference OpenAPI profile | High if private routes leak | Must not include exact Future-BS routes. |
| `docs/api-docs/openapi.developer-preview.json` | public_preview_risk | Yes | Developer-preview OpenAPI profile | High if private routes leak | Must not include research-private exact outputs. |
| `packages/parva-js/src/*` | public_preview_risk | Yes, public/default SDK only | Public SDK route helpers | High if private tokens appear | Keep exact Future-BS route tokens out of public defaults. |
| `packages/parva-python/parva/*` | public_preview_risk | Yes, public/default SDK only | Public SDK route helpers | High if private tokens appear | Keep exact Future-BS route tokens out of public defaults. |
| `frontend/src/config/routeCapabilities.js` | public_safe_metadata | Yes | Public capability metadata | Medium | Show capabilities only; do not link exact Future-BS outputs publicly. |
| `tests/accuracy/test_future_bs_official_holdout.py` | public_safe_metadata | Yes | Public official 2078-2083 holdout | Medium | Keep in public lane while it uses public official holdout only. |
| `tests/accuracy/test_green_zone_accuracy.py` | public_safe_metadata | Yes | Public official 2078-2083 holdout | Medium | Keep in public lane; assertions must stay conservative. |
| `tests/accuracy/test_2083_ashwin_replay.py` | research_artifact | Yes only as local public test if generated artifact is available | Red-team replay artifact | Medium | Mark research_artifact if it starts requiring private/generated inputs. |
| `tests/accuracy/test_future_bs_performance.py` | generated_artifact_required | Yes only while it uses checked-in public-safe precompute path | Future-BS precompute/cache behavior | Medium | Mark research_artifact if it starts requiring private precomputed data. |
| `tests/future_bs/*` | research_artifact | No by default | Research model, fusion, inversion, and calibration behavior | Medium | Keep out of public lane when they require generated/private/wide artifacts. |
| `tests/performance/test_calendar_model_risk_latency.py` | public_preview_risk | Yes only while it exercises available public-safe fixture years | Calendar model-risk service latency | High if exact predictions are exposed publicly | Keep route exposure private; mark research_artifact if generated artifacts become required. |
| `tests/performance/*` | public_safe_metadata | Yes, for public route latency coverage | Public-safe route and service latency tests | Low | Preserve public performance coverage. |

## Intentional Research Commands

Run the public-safe lane:

```bash
python -m pytest -q -m "not private_source and not wide_corpus and not research_artifact"
```

Run Future-BS focused public-safe coverage:

```bash
python -m pytest tests/future_bs tests/accuracy tests/artifacts tests/performance -q -m "not private_source and not wide_corpus and not research_artifact"
```

Run private/wide/research-only tests only when the needed private source archive
or generated research artifacts are intentionally present:

```bash
python -m pytest -q -m "private_source or wide_corpus or research_artifact"
```

This report does not certify official future BS dates, government approval,
legal authority, tax authority, payroll authority, banking authority, or
religious authority.
