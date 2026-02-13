# Project Parva — Weekly Implementation Plan: Year 3

> **Year 3: Standardization, Defensibility, and Global Reliability** (March 2028 – February 2029)
>
> **Exit Criteria**: Published open benchmark standard, calibrated uncertainty, deterministic explainability, institutional offline packages, v3 LTS API, Parva Temporal Spec 1.0.

---

## M25: Benchmark Standard v1 (Mar 1–28, 2028)

### Week 97 (Mar 1–7) — Benchmark Schema Design

| Day | Deliverables |
|---|---|
| Mon | Survey existing calendar accuracy benchmarks in academia and industry. Document findings in `docs/BENCHMARK_SURVEY.md`. |
| Tue | Design Parva Benchmark Schema: JSON format for test packs containing `{ calendar_family, test_cases: [{ input, expected_output, source, tolerance }] }`. |
| Wed | Design test harness: `benchmark/harness.py` — loads any benchmark pack, runs against any calendar API (local or remote), produces comparison report. |
| Thu | Write harness specification: input/output formats, pass/fail criteria, tolerance rules, report schema. `docs/BENCHMARK_SPEC.md`. |
| Fri | Implement schema validator: `benchmark/validate_pack.py` — confirms a test pack is well-formed. |
| Sat–Sun | Buffer |

---

### Week 98 (Mar 8–14) — Building Benchmark Packs

| Day | Deliverables |
|---|---|
| Mon | Build BS conversion benchmark pack: 500+ cases across 2070–2095 (official) + 100 extended range with tolerance. |
| Tue | Build tithi benchmark pack: 200+ cases across 2020–2030 with sub-hour tolerance. Source from Drik Panchang and Rashtriya Panchang. |
| Wed | Build festival date benchmark pack: 15 festivals × 10 years = 150 cases with source citations. |
| Thu | Build panchanga benchmark pack: 100 full panchanga outputs verified against trusted sources. |
| Fri | Build multi-calendar pack: 50 cases each for Islamic, Hebrew, Chinese, Tibetan conversions. |
| Sat–Sun | Buffer |

---

### Week 99 (Mar 15–21) — Harness Implementation & Testing

| Day | Deliverables |
|---|---|
| Mon | Implement benchmark harness: loads pack → calls API → compares → generates structured report. |
| Tue | Implement report format: per-case pass/fail, aggregate accuracy, latency stats, comparison tables. |
| Wed | Implement remote API testing: harness can test against any HTTP endpoint that speaks Parva API contract. |
| Thu | Run Parva against all benchmark packs. Store baseline results in `benchmark/results/baseline_2028Q1.json`. |
| Fri | Write `benchmark/README.md`: how any external team can download packs + harness and replicate results. |
| Sat–Sun | Buffer |

---

### Week 100 (Mar 22–28) — M25 Hardening & Publication

| Day | Deliverables |
|---|---|
| Mon | Publish benchmark packs as downloadable artifacts (GitHub release or similar). |
| Tue | Run harness against one external service (Drik Panchang manual comparison) to demonstrate cross-system testing. |
| Wed | Regression: verify Parva still passes all existing test suites. |
| Thu | Documentation: `docs/BENCHMARK_SPEC.md` finalized. Blog post draft: "An Open Benchmark for Calendar Accuracy." |
| Fri | M25 postmortem. Git tag `v3.0.0-m25`. |
| Sat–Sun | Buffer |

**M25 Definition of Done**: Any external team can run benchmark packs and compare results apples-to-apples.

---

## M26: Uncertainty Modeling (Mar 29 – Apr 25, 2028)

### Week 101 (Mar 29 – Apr 4) — Uncertainty Framework Design

| Day | Deliverables |
|---|---|
| Mon | Define uncertainty categories: `exact` (official lookup match), `confident` (ephemeris within 2-hour tolerance), `estimated` (outside official range, ±1 day), `uncertain` (sparse data or approximation). |
| Tue | Design calibration methodology: for each category, compute historical frequency of correct predictions. Use as posterior probability. |
| Wed | Design `UncertaintyReport` type: `{ level, probability, interval_hours, calibration_data_size, methodology }`. |
| Thu | Write uncertainty specification: `docs/UNCERTAINTY_SPEC.md`. |
| Fri | Gather calibration data: historical predictions vs actuals from evaluation archive (M8 onwards). |
| Sat–Sun | Buffer |

---

### Week 102 (Apr 5–11) — Calibration Implementation

| Day | Deliverables |
|---|---|
| Mon | Implement `calibrate_uncertainty(history) → CalibrationModel`: builds probability model from historical prediction-vs-actual pairs. |
| Tue | Implement per-rule calibration: different festival rule types (lunar tithi, solar transit, BS-fixed) have different uncertainty profiles. |
| Wed | Implement confidence interval computation: for estimated BS dates, compute date range with 95% confidence. |
| Thu | Wire uncertainty into all date-returning API responses. Add `uncertainty` object alongside existing `confidence` field. |
| Fri | Test: verify uncertainty intervals actually contain the correct answer ≥95% of the time on held-out data. |
| Sat–Sun | Buffer |

---

### Week 103 (Apr 12–18) — Boundary-Sensitive Outputs

| Day | Deliverables |
|---|---|
| Mon | Identify boundary-sensitive outputs: tithi at sunrise when transition is within 30 minutes of sunrise, Adhik Maas years, BS month boundaries in estimated mode. |
| Tue | Add special uncertainty handling for boundary cases: if tithi transition is within 30 min of sunrise, flag `boundary_proximity_minutes` and widen uncertainty interval. |
| Wed | Frontend: display uncertainty indicators. For exact dates, show confidently. For estimated, show range. For boundary-sensitive, show explanation. |
| Thu | Write user-facing uncertainty explanation: "This date is estimated because..." |
| Fri | Test uncertainty display across 20 different scenarios. |
| Sat–Sun | Buffer |

---

### Week 104 (Apr 19–25) — M26 Hardening

| Day | Deliverables |
|---|---|
| Mon | Calibration validation: verify calibration model is well-calibrated (predicted 95% → actual ≥95%). |
| Tue | Regression: all existing tests still pass with uncertainty additions. |
| Wed | Performance: uncertainty computation adds < 2ms per request. |
| Thu | Documentation update. |
| Fri | M26 postmortem. Git tag `v3.0.1-m26`. |
| Sat–Sun | Buffer |

**M26 Definition of Done**: Responses include calibrated uncertainty, not just categorical confidence. Boundary cases explicitly flagged.

---

## M27: Differential Testing at Scale (Apr 26 – May 23, 2028)

### Week 105 (Apr 26 – May 2) — Differential Test Design

| Day | Deliverables |
|---|---|
| Mon | Identify differential test sources: Drik Panchang, Nepal Patro online, Hamro Patro data, prior Parva versions. |
| Tue | Design `DifferentialTest` framework: run same query against Parva and N reference sources, compare outputs, classify disagreements. |
| Wed | Implement source adapters: wrapper for each reference source that normalizes output to common format. |
| Thu | Design disagreement taxonomy: `agreement`, `minor_difference` (±1 day), `major_difference` (>1 day), `source_missing`, `incomparable`. |
| Fri | Write `docs/DIFFERENTIAL_TESTING.md`. |
| Sat–Sun | Buffer |

---

### Week 106 (May 3–9) — Implementation & Baseline

| Day | Deliverables |
|---|---|
| Mon | Implement differential test runner: for a given date range, query all sources, compute agreement matrix. |
| Tue | Implement drift detection: compare current Parva version against prior Parva version. Flag any date that changed. |
| Wed | Run baseline differential test: 100 festivals × 3 years vs available external sources. Store results. |
| Thu | Build drift alert system: if running differential test shows >2% change from prior version, flag for review. |
| Fri | Add to CI: PRs that touch `engine/` or `rules/` trigger differential test against prior stable release. |
| Sat–Sun | Buffer |

---

### Week 107 (May 10–16) — Disagreement Investigation

| Day | Deliverables |
|---|---|
| Mon–Tue | Investigate each major disagreement from baseline run. Classify: Parva correct, source correct, both plausible (regional variant), or data quality issue. |
| Wed–Thu | Fix any Parva errors found. Correct any test data errors. Document "both plausible" cases with reasoning. |
| Fri | Update disagreement taxonomy with findings. |
| Sat–Sun | Buffer |

---

### Week 108 (May 17–23) — M27 Hardening

| Day | Deliverables |
|---|---|
| Mon | CI gate: release blocked if drift exceeds threshold (configurable per calendar module). |
| Tue | Store disagreement taxonomy in structured format: `data/differential/disagreements.json`. |
| Wed | Regression. Documentation. |
| Thu–Fri | M27 postmortem. Git tag `v3.0.2-m27`. |
| Sat–Sun | Buffer |

**M27 Definition of Done**: Release blocked automatically if drift exceeds thresholds. Disagreement taxonomy maintained.

---

## M28: Long-Horizon Forecasting (May 24 – Jun 20, 2028)

### Week 109–112

| Week | Focus |
|---|---|
| Week 109 | Design forecasting API: `/v2/forecast/festivals?year=2050&festivals=dashain,tihar`. Define confidence decay model: accuracy decreases as horizon extends beyond official data range. Build error curves: plot accuracy vs forecast distance using historical overlap data. |
| Week 110 | Implement forecasting endpoints with explicit confidence decay. Response includes `horizon_years`, `estimated_accuracy`, `confidence_interval_days`. Build forecast for 2030–2050 for all 15 priority festivals. |
| Week 111 | Validate near-term forecasts against available data. Build 20-year forecast report. Frontend: timeline view showing forecast confidence fading with distance. User-facing explanation: "This date is a forecast based on astronomical computation." |
| Week 112 | M28 hardening. Regression. Documentation. Git tag `v3.0.3-m28`. |

**M28 Definition of Done**: Forecast APIs communicate confidence decay with horizon. Error curves published.

---

## M29: Zero-Cost Scale Architecture (Jun 21 – Jul 18, 2028)

### Week 113–116

| Week | Focus |
|---|---|
| Week 113 | Profiling: measure cold-start time, memory usage, response latency by endpoint. Identify hot paths. Design precomputation strategy: panchanga for a given date is static — precompute for current year + next 2 years. Store as JSON artifacts. Design edge-caching: static panchanga/festival data served from Cloudflare Workers (free tier: 100k req/day). |
| Week 114 | Implement precomputation pipeline: `scripts/precompute_panchanga.py` generates daily panchanga JSON for a date range. Implement static artifact serving: precomputed data served as static files, bypassing compute. Implement cache layer: Cloudflare Worker or Vercel Edge Function that serves cached responses, falls back to compute for uncached requests. |
| Week 115 | Load testing: simulate Dashain/Tihar traffic spike (1000 req/min). Verify system stays within free-tier limits. Optimize: identify and eliminate redundant ephemeris calls (cache Sun/Moon positions per day). Profile cache-hit ratio. Target: >90% cache hit for panchanga, >80% for festival dates. |
| Week 116 | P95 and P99 latency targets met. Artifact size budget checked. Cold-start < 3s. M29 postmortem. Git tag `v3.0.4-m29`. |

**M29 Definition of Done**: P95 latency and cache-hit targets met under free infrastructure. >90% cache hit ratio.

---

## M30: Reliability Engineering (Jul 19 – Aug 15, 2028)

### Week 117–120

| Week | Focus |
|---|---|
| Week 117 | Define SLOs: availability (99.5% monthly), latency (P95 < 500ms), accuracy (≥99% on official overlap). Design alerting: free-tier UptimeRobot + Sentry error tracking. Write incident playbooks: "ephemeris library fails to load," "data file corrupted," "source outage." |
| Week 118 | Implement degraded-confidence mode: if ephemeris fails, fall back to cached results + `confidence: "degraded"`. If data file corrupted, serve last-known-good snapshot + alert. If source outage, continue computing + flag `source_status: "stale"`. |
| Week 119 | Chaos/fault-injection drills: kill ephemeris process mid-computation, corrupt a data file, simulate network timeout to external source. Verify: system recovers gracefully, returns degraded-confidence responses, alerts fire. |
| Week 120 | Document reliability guarantees: `docs/RELIABILITY.md`. SLO dashboard on public benchmark page. M30 postmortem. Git tag `v3.0.5-m30`. |

**M30 Definition of Done**: Service degrades gracefully. SLOs defined and tracked. Incident playbooks tested.

---

## M31: Security Hardening (Aug 16 – Sep 12, 2028)

### Week 121–124

| Week | Focus |
|---|---|
| Week 121 | Dependency audit: `pip-audit`, `npm audit`. Pin all dependency versions. Document supply-chain policy. Create `SECURITY.md` with vulnerability reporting process. |
| Week 122 | Implement signature verification in CI: all published artifacts (SDKs, benchmark packs, data snapshots) signed with project GPG key. Add secrets hygiene: no secrets in code, all config via environment variables, `.env.example` provided. |
| Week 123 | Pen-test style checklist: test for injection (query params), CORS misconfiguration, rate-limit bypass, data exfiltration. Build abuse-case suite: malformed dates, extreme ranges, oversized requests. Implement input sanitization and size limits. |
| Week 124 | Security baseline enforced in CI: audit check, signature verification, dependency pinning check all run on every PR. M31 postmortem. Git tag `v3.0.6-m31`. |

**M31 Definition of Done**: Security baseline documented and enforced. Supply-chain controls operational.

---

## M32: Compliance and Policy Clarity (Sep 13 – Oct 10, 2028)

### Week 125–128

| Week | Focus |
|---|---|
| Week 125 | Draft legal/policy disclaimers: "Parva provides computed observance dates for informational purposes. For religious observance, consult local authorities." Design policy model: per-response metadata indicating advisory vs informational status. Review open-source license (MIT) implications for institutional users. |
| Week 126 | Implement policy metadata in API responses: `policy: { usage: "informational", disclaimer_url: "..." }`. Add terms of service page. Write institutional usage guide: how universities/governments can use Parva data with proper attribution. |
| Week 127 | Policy QA: scenario tests — "User relies on Parva date for religious ceremony," "Government uses Parva for official calendar," "App redistributes Parva data." Ensure each scenario has clear policy guidance. |
| Week 128 | Documentation finalized: `docs/POLICY.md`, `docs/INSTITUTIONAL_USAGE.md`. M32 postmortem. Git tag `v3.0.7-m32`. |

**M32 Definition of Done**: Clear policy model shipped with API terms and response metadata.

---

## M33: Explainability Assistant (Oct 11 – Nov 7, 2028)

### Week 129 (Oct 11–17) — Reason Trace Design

| Day | Deliverables |
|---|---|
| Mon | Design `ReasonTrace` data structure: ordered list of computation steps, each with `{ step_type, input, output, rule_id, source, math_expression }`. |
| Tue | Implement trace collection: every engine computation call adds a step to the trace. Thread trace through entire pipeline. |
| Wed | Implement trace storage: traces stored ephemerally (in-memory for request duration) or persistently (by trace_id for later retrieval). |
| Thu | Implement `/v2/explain/{trace_id}` endpoint: returns full deterministic reason trace. |
| Fri | Write trace format specification: `docs/EXPLAIN_SPEC.md`. |
| Sat–Sun | Buffer |

---

### Week 130 (Oct 18–24) — UI Explanation Composer

| Day | Deliverables |
|---|---|
| Mon | Design explanation UI: step-by-step "How we calculated this date" panel. |
| Tue | Implement `ExplainView.jsx`: renders ReasonTrace as human-readable steps with expandable detail. |
| Wed | Add math rendering: show elongation formula, tithi calculation, sankranti detection with actual numbers. |
| Thu | Add source citations: each step shows which data source or rule was used. |
| Fri | Link explain view from every festival date in the UI: "How was this calculated?" button. |
| Sat–Sun | Buffer |

---

### Week 131 (Oct 25–31) — Validation & Consistency

| Day | Deliverables |
|---|---|
| Mon | Write trace consistency tests: for a given input, trace must be deterministic — same input always produces identical trace. |
| Tue | Validate explanation text against calculation: automated check that explanation narrative matches actual computed values. |
| Wed | Usability test: give explanation to non-technical user, verify they can understand why a date was chosen. |
| Thu | Add trace to provenance chain: trace_id links to snapshot_id and Merkle proof. |
| Fri | Regression and full test suite. |
| Sat–Sun | Buffer |

---

### Week 132 (Nov 1–7) — M33 Hardening

| Day | Deliverables |
|---|---|
| Mon–Tue | Performance: trace collection adds < 3ms to response time. |
| Wed | Documentation: `docs/EXPLAINABILITY.md`. |
| Thu–Fri | M33 postmortem. Git tag `v3.1.0-m33`. |
| Sat–Sun | Buffer |

**M33 Definition of Done**: Users and evaluators see exact rule/math/source path per date. Traces are deterministic and verifiable.

---

## M34: Institutional Packaging (Nov 8 – Dec 5, 2028)

### Week 133–136

| Week | Focus |
|---|---|
| Week 133 | Design offline verifier bundle: self-contained package that universities/governments can download and run locally to verify Parva outputs without network access. Contents: engine binary/script, benchmark packs, verification scripts, data snapshot, documentation. Design reproducible snapshot kit: Docker container or Python virtualenv with pinned dependencies that reproduces exact Parva outputs. |
| Week 134 | Implement offline bundle: `scripts/build_offline_bundle.sh` packages engine + data + benchmark into ZIP. Implement Docker image: `Dockerfile` that builds reproducible Parva environment. Test: build bundle, install on clean machine, run benchmark, verify results match online API. |
| Week 135 | Verify offline parity: run 100 queries against online API and offline bundle, assert identical results. Write institutional deployment guide: `docs/INSTITUTIONAL_DEPLOYMENT.md` — step-by-step for IT departments. Create reproducible hash: bundle itself has a checksum that verifies contents are untampered. |
| Week 136 | Publish bundle as GitHub release artifact. Write announcement. M34 postmortem. Git tag `v3.1.1-m34`. |

**M34 Definition of Done**: Institutions validate outputs without trusting hosted service. Offline parity verified.

---

## M35: v3 Stabilization (Dec 6, 2028 – Jan 2, 2029)

### Week 137 (Dec 6–12) — Contract Cleanup

| Day | Deliverables |
|---|---|
| Mon | Audit all API endpoints: list every field, type, and version introduced. |
| Tue | Identify deprecated fields from v2 evolution: remove or mark with `@deprecated` in OpenAPI spec. |
| Wed | Freeze v3 response schemas: no field additions, removals, or type changes allowed after this week. |
| Thu | Write v2→v3 migration guide: `docs/MIGRATION_V2_V3.md` — field-by-field mapping, breaking changes, timeline. |
| Fri | Hard deprecation: v2 endpoints return `410 Gone` with migration guide URL. |
| Sat–Sun | Buffer |

---

### Week 138 (Dec 13–19) — SDK Parity Update

| Day | Deliverables |
|---|---|
| Mon | Update Python SDK to v3 contract. Run parity tests. |
| Tue | Update TypeScript SDK to v3 contract. Run parity tests. |
| Wed | Update Go SDK to v3 contract. Run parity tests. |
| Thu | Publish SDK v3.0.0 to all registries. |
| Fri | Update all examples, documentation, and sample apps. |
| Sat–Sun | Buffer |

---

### Week 139 (Dec 20–26) — Full Regression

| Day | Deliverables |
|---|---|
| Mon | Run full regression across all modules: engine, rules, sources, API, SDKs, frontend. |
| Tue | Run all benchmark packs against v3 API. |
| Wed | Run differential tests against all external sources. |
| Thu | Run reliability drills (M30 playbooks). |
| Fri | Fix any issues found. |
| Sat–Sun | Holiday buffer |

---

### Week 140 (Dec 27 – Jan 2) — M35 Release

| Day | Deliverables |
|---|---|
| Mon | Declare v3 long-term stable (LTS). No breaking changes until v4 (minimum 2 years). |
| Tue | Publish LTS guarantee document: `docs/LTS_POLICY.md`. |
| Wed | Update all deployment configurations for v3. |
| Thu | M35 postmortem. Git tag `v3.0.0-stable`. |
| Fri–Sun | Holiday rest |

**M35 Definition of Done**: v3 declared LTS. Migration from v2 completed. SDK parity verified. Full regression passing.

---

## M36: Standard Publication (Jan 3 – Feb 1, 2029)

### Week 141 (Jan 3–9) — Parva Temporal Spec 1.0

| Day | Deliverables |
|---|---|
| Mon | Compile all specifications into unified document: calendar plugin interface, observance rule DSL, confidence model, uncertainty framework, provenance scheme, trust layer, benchmark schema. |
| Tue | Write Parva Temporal Spec 1.0 preamble: scope, goals, non-goals, versioning policy. |
| Wed | Write algorithm specifications section: ephemeris usage, tithi computation, sankranti detection, Adhik Maas, lunar month model — with equations and pseudocode. |
| Thu | Write data model section: all types, all response shapes, all metadata fields with complete semantics. |
| Fri | Write trust section: hashing, Merkle proofs, transparency logs, verification protocol. |
| Sat–Sun | Buffer |

---

### Week 142 (Jan 10–16) — Spec Review & Refinement

| Day | Deliverables |
|---|---|
| Mon | Self-review: read entire spec critically. Flag ambiguities, missing definitions, internal inconsistencies. |
| Tue | Fix all flagged issues. Add examples for every ambiguous section. |
| Wed | Write implementer's guide: "If you wanted to build a system compatible with Parva from scratch, here's how." |
| Thu | Write conformance test suite: minimal set of tests that any Parva-compatible implementation must pass. |
| Fri | Package conformance tests as standalone repo with instructions. |
| Sat–Sun | Buffer |

---

### Week 143 (Jan 17–23) — Independent Reproducibility

| Day | Deliverables |
|---|---|
| Mon | Prepare reproducibility package: spec + benchmark packs + conformance tests + offline bundle + reference results. |
| Tue | Test reproducibility: fresh machine, follow spec, run conformance tests, compare against reference results. Document any issues. |
| Wed | Fix any reproducibility gaps. Ensure zero-dependency path: anyone with Python 3.11+ can replicate. |
| Thu | Write academic-style abstract: 500 words summarizing the contribution for potential paper submission. |
| Fri | Write blog post: "Parva Temporal Spec 1.0: An Open Standard for Multi-Calendar Computation." |
| Sat–Sun | Buffer |

---

### Week 144 (Jan 24 – Feb 1) — Publication & Year 3 Retrospective

| Day | Deliverables |
|---|---|
| Mon | Publish Parva Temporal Spec 1.0 as PDF and Markdown in repo + hosted documentation. |
| Tue | Publish benchmark results: comprehensive accuracy tables for all calendar families. |
| Wed | Publish reproducibility package as GitHub release. |
| Thu | Final benchmark dashboard update. Git tag `v3.0.0-spec1.0`. |
| Fri | Year 3 retrospective: `docs/YEAR_3_RETROSPECTIVE.md`. 3-year retrospective: `docs/THREE_YEAR_RETROSPECTIVE.md`. |
| Sat | **Project milestone: Parva recognized as open, verifiable temporal infrastructure.** |
| Sun | Rest. Plan what comes next. |

**M36 Definition of Done**: Parva Temporal Spec 1.0 published. Benchmark results public. Independent reproducibility verified. 3-year plan complete. 🏆

---

## Year 3 Summary

| Month | Outcome | Tag |
|---|---|---|
| M25 | Open benchmark standard published | `v3.0.0-m25` |
| M26 | Calibrated uncertainty in every response | `v3.0.1-m26` |
| M27 | Differential testing with auto-block on drift | `v3.0.2-m27` |
| M28 | Long-horizon forecasting with confidence decay | `v3.0.3-m28` |
| M29 | Zero-cost scale (>90% cache hit, free-tier viable) | `v3.0.4-m29` |
| M30 | Reliability engineering (SLOs, playbooks, chaos drills) | `v3.0.5-m30` |
| M31 | Security hardened (supply-chain, audits, CI gates) | `v3.0.6-m31` |
| M32 | Policy and compliance clarity | `v3.0.7-m32` |
| M33 | Deterministic explainability engine | `v3.1.0-m33` |
| M34 | Institutional offline packages | `v3.1.1-m34` |
| M35 | v3 LTS stabilized | `v3.0.0-stable` |
| M36 | Parva Temporal Spec 1.0 published | `v3.0.0-spec1.0` |

---

*End of Year 3 Weekly Plan — Weeks 97–144, from benchmark standardization through Parva Temporal Spec 1.0 publication.*

*End of 3-Year Weekly Implementation Plan — 144 weeks, 36 months, 8 workstreams, $0 budget. The greatest festival timing system ever built.*
