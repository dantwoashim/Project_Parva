# Project Parva — Weekly Implementation Plan: Year 1

> **Year 1: Nepal Gold Standard** (March 2026 – February 2027)
> 
> **Exit Criteria**: Every festival date from a single V2 engine, ≥99% accuracy on official overlap, confidence + method + provenance in every response, reproducible benchmark published.

---

## Monthly Cadence (Applies to Every Month)

| Week | Focus |
|---|---|
| Week 1 | Specification lock, algorithm work, interface definitions, test case design |
| Week 2 | Implementation, code review, contract updates |
| Week 3 | Data verification, benchmark rerun, discrepancy triage |
| Week 4 | Hardening, docs, release candidate, postmortem, next-month prep |

---

## M1: Enforce One Calculation Path (Mar 2–29, 2026)

### Week 1 (Mar 2–8) — Audit & Spec

**Workstream focus**: Core Engine, Quality Engineering

| Day | Deliverables |
|---|---|
| Mon | Full audit of all API routes — list every endpoint and which calculator it uses (V1 vs V2). Document in spreadsheet: route path, handler function, calculator called, response schema. |
| Tue | Map all code paths from `calculator.py` (V1) — identify every import, every call site in routes, evaluation scripts, and frontend hooks. Create dependency graph. |
| Wed | Map all code paths from `calculator_v2.py` — same treatment. Identify differences in festival coverage, Adhik Maas handling, rule format (`festival_rules.json` vs `festival_rules_v3.json`). |
| Thu | Write migration specification: for each V1 call site, document the exact V2 replacement, expected behavior change, and test case needed to verify equivalence. |
| Fri | Define unified response contract: every date endpoint returns `{ date, confidence, method, engine_version }`. Write JSON Schema for this contract. |
| Sat | Design ritual timeline adapter spec: document current `daily_rituals` array format in `festivals.json` vs expected `ritualSequence.days` in frontend. Write transformation function spec. |
| Sun | Buffer / review |

**Definition of Done**: Migration spec document complete, unified response schema defined, all V1 call sites catalogued.

---

### Week 2 (Mar 9–15) — V1→V2 Migration

**Workstream focus**: Core Engine, API Platform

| Day | Deliverables |
|---|---|
| Mon | Redirect `backend/app/calendar/routes.py` — all `/api/calendar/convert`, `/api/calendar/today`, `/api/calendar/panchanga` endpoints to use V2 engine internally. Keep external contract stable. |
| Tue | Redirect `backend/app/festivals/repository.py` — ensure `get_festival_dates()` uses only `calculator_v2.calculate_festival_date_v2()`. Remove any fallback to V1. |
| Wed | Redirect `backend/app/festivals/routes.py` — `/api/festivals/upcoming`, `/api/festivals/{id}/dates` must call V2 exclusively. Add `engine_version: "v2"` to all responses. |
| Thu | Update `backend/tools/evaluate.py` to import and use `calculator_v2` instead of `calculator`. Run evaluation — compare new results against old `evaluation.csv`. |
| Fri | Fix ritual timeline adapter: create `backend/app/festivals/adapters.py` with `normalize_ritual_data(festival_json) → RitualSequence` that handles both `daily_rituals` array and legacy formats. |
| Sat | Wire adapter into `/api/festivals/{id}` response — ritual data now always arrives in correct shape for frontend `RitualTimeline.jsx`. |
| Sun | Buffer / review |

**Definition of Done**: Zero imports of `calculator.py` in any active route. All endpoints return V2 results.

---

### Week 3 (Mar 16–22) — Verification & Ground Truth

**Workstream focus**: Data Quality, Quality Engineering

| Day | Deliverables |
|---|---|
| Mon | Build baseline ground-truth file: extract all festivals from MoHA PDFs for 2080 BS using existing OCR pipeline. Cross-reference with `ground_truth_overrides.json`. |
| Tue | Extend ground truth for 2081 BS — same process. Document extraction confidence per entry. |
| Wed | Extend ground truth for 2082 BS — same process. Merge all three years into `data/ground_truth/baseline_2080_2082.json` with source citations. |
| Thu | Create discrepancy register: `data/ground_truth/discrepancies.json` — for every festival where V2 calculation differs from ground truth, log: `{ festival_id, year, calculated, official, delta_days, probable_cause }`. |
| Fri | Run full evaluation: `python backend/tools/evaluate.py` against new ground truth. Generate accuracy scorecard: by-festival and by-rule breakdown. |
| Sat | Investigate each discrepancy — classify as: rule error, data error, edge case (Adhik Maas), or genuine limitation. |
| Sun | Buffer / review |

**Definition of Done**: Ground truth file for 2080–2082 complete. Discrepancy register created. Accuracy scorecard generated.

---

### Week 4 (Mar 23–29) — Hardening & Release

**Workstream focus**: Quality Engineering, API Platform

| Day | Deliverables |
|---|---|
| Mon | Write integration tests for every migrated endpoint — `tests/integration/test_v2_migration.py`: test that `/api/festivals/dashain/dates` returns V2 results, test response schema includes `engine_version`. |
| Tue | Write regression tests: for every festival in ground truth, assert calculated date matches. `tests/integration/test_ground_truth.py`. |
| Wed | Remove dead code: mark `calculator.py` as deprecated with module-level warning. Remove `festival_rules.json` (V1 rules) references from active code paths. Keep files for reference. |
| Thu | Update API documentation: Swagger/OpenAPI spec reflects new response shapes. Update `README.md` and `TECHNICAL_README.md`. |
| Fri | M1 postmortem: document what went well, what was harder than expected, what to watch for in M2. Update `CHANGELOG.md`. |
| Sat | Git tag `v2.0.1-m1`. Prepare M2 spec. |
| Sun | Buffer / rest |

**Definition of Done**: All tests pass. No active code uses V1 calculator. Response contracts unified. M1 shipped.

---

## M2: Stabilize Architecture (Mar 30 – Apr 26, 2026)

### Week 5 (Mar 30 – Apr 5) — Module Boundary Design

**Workstream focus**: Core Engine, API Platform

| Day | Deliverables |
|---|---|
| Mon | Design new module layout: `backend/app/engine/` (pure computation, no I/O), `backend/app/rules/` (festival rules, rule DSL), `backend/app/sources/` (data loading, OCR, overrides), `backend/app/api/` (routes, serialization). Write README for each. |
| Tue | Define `EngineInterface` protocol: abstract class/protocol that any calendar engine must implement — `calculate_tithi(dt) → TithiResult`, `calculate_panchanga(dt) → PanchangaResult`, `convert_date(from, to, date) → ConversionResult`. |
| Wed | Define `SourceInterface` protocol: `load_ground_truth() → dict`, `load_festival_rules() → list[FestivalRule]`, `get_source_priority() → list[SourcePriority]`. |
| Thu | Define strict type contracts using Pydantic v2: `TithiResult`, `PanchangaResult`, `ConversionResult`, `FestivalDateResult` — each with `confidence`, `method`, `source` fields. Write in `backend/app/engine/types.py`. |
| Fri | Document source-priority policy: when MoHA, Rashtriya Panchang, computed, and OCR-derived dates disagree, which wins? Write `docs/SOURCE_PRIORITY.md`. |
| Sat | Review architecture with mermaid diagram — update `docs/SYSTEM_DIAGRAMS.md`. |
| Sun | Buffer |

---

### Week 6 (Apr 6–12) — Module Extraction

| Day | Deliverables |
|---|---|
| Mon | Create `backend/app/engine/` directory. Move `ephemeris/`, `tithi/`, `panchanga.py`, `sankranti.py`, `lunar_calendar.py`, `adhik_maas.py` into it. Update all imports. |
| Tue | Create `backend/app/rules/` directory. Move `calculator_v2.py`, `festival_rules_v3.json`, `festival_rules_loader.py` into it. Update imports. |
| Wed | Create `backend/app/sources/` directory. Move `overrides.py`, `ground_truth_overrides.json`, `bs_overrides.json`, `sources.json`, `constants.py` into it. Update imports. |
| Thu | Refactor `backend/app/api/` — move `calendar/routes.py` → `api/calendar_routes.py`, `festivals/routes.py` → `api/festival_routes.py`, etc. `main.py` imports only from `api/`. |
| Fri | Run full test suite — fix any broken imports. Ensure 100% test pass rate after restructure. |
| Sat | Update all documentation references to reflect new paths. |
| Sun | Buffer |

---

### Week 7 (Apr 13–19) — Type Contracts & Validation

| Day | Deliverables |
|---|---|
| Mon | Implement `EngineInterface` as abstract base — `backend/app/engine/interface.py`. Current ephemeris engine implements this interface. |
| Tue | Add Pydantic validators to all response types: `TithiResult.confidence` must be one of `exact|computed|estimated`. `ConversionResult.source_range` required when confidence is `estimated`. |
| Wed | Add request validation: all date inputs validated for range, timezone awareness enforced, invalid dates return 422 with helpful message. |
| Thu | Add response serialization middleware: every API response passes through `serialize_response()` that ensures contract compliance. |
| Fri | Write contract tests: `tests/contract/test_response_shapes.py` — assert every endpoint returns fields required by contract. |
| Sat | Review and document all type contracts in `docs/API_CONTRACTS.md`. |
| Sun | Buffer |

---

### Week 8 (Apr 20–26) — M2 Hardening

| Day | Deliverables |
|---|---|
| Mon | Integration test full API surface with new module boundaries. |
| Tue | Performance benchmark: measure latency of each endpoint before/after restructure. Ensure no regression. |
| Wed | Source precedence integration test: when override exists, override wins. When no override, calculation wins. |
| Thu | Documentation pass: all module READMEs written, all interface docstrings complete. |
| Fri | M2 postmortem. Update `CHANGELOG.md`. Git tag `v2.0.2-m2`. |
| Sat | Prepare M3 spec: list exact ephemeris hardening tasks. |
| Sun | Buffer / rest |

**M2 Definition of Done**: Clean module boundaries (`engine/`, `rules/`, `sources/`, `api/`). Pluggable engine interface defined. Source precedence documented and enforced. All tests pass.

---

## M3: Ephemeris Core Hardening (Apr 27 – May 24, 2026)

### Week 9 (Apr 27 – May 3) — UTC & Timezone Audit

| Day | Deliverables |
|---|---|
| Mon | Audit every `datetime` usage in `engine/` — catalogue which are naive, which are aware, which assume UTC, which assume NPT. |
| Tue | Enforce rule: all internal engine computation uses UTC-aware datetimes. Create `engine/time_utils.py` with `ensure_utc(dt)`, `to_npt(dt)`, `from_npt(dt)`. |
| Wed | Refactor `ephemeris/swiss_eph.py`: all calls to `swe.julday()` and `swe.calc_ut()` use UTC-aware input. Add assertion guards. |
| Thu | Refactor `tithi/tithi_core.py`: sunrise calculation receives UTC, converts to NPT only for display. |
| Fri | Write timezone edge-case tests: midnight NPT crossover, DST-less calendar, date-line scenarios for diaspora. `tests/unit/test_timezone.py` — 30+ cases. |
| Sat | Run full suite — fix any timezone-related failures. |
| Sun | Buffer |

---

### Week 10 (May 4–10) — Sidereal/Tropical Configuration

| Day | Deliverables |
|---|---|
| Mon | Implement `EphemerisConfig` dataclass: `ayanamsa` (Lahiri/Raman/KP), `coordinate_system` (sidereal/tropical), `ephemeris_mode` (Moshier/Swiss). |
| Tue | Thread `EphemerisConfig` through all engine calculations — every `calculate_*` function accepts optional config. Default = Lahiri sidereal Moshier. |
| Wed | Add config endpoint: `GET /api/engine/config` returns current configuration. Add header `X-Parva-Ephemeris: moshier-lahiri` to all responses. |
| Thu | Write comparison tests: same date with Lahiri vs Raman ayanamsa — verify expected difference in longitude. `tests/unit/test_ayanamsa.py`. |
| Fri | Update documentation: clarify Moshier (not DE431) in all docs. Fix README, ephemeris_spec.md, PROJECT_BIBLE.md. |
| Sat | Document: "Why Moshier is sufficient" — accuracy comparison table vs DE431 for our date range. |
| Sun | Buffer |

---

### Week 11 (May 11–17) — 500-Timestamp Verification

| Day | Deliverables |
|---|---|
| Mon | Generate 500 random timestamps across 2000–2100 AD using script. For each, compute Sun longitude and Moon longitude. |
| Tue | Collect reference values: scrape/compute using independent source (Drik Panchang API, or JPL Horizons web interface for spot checks). Store in `tests/fixtures/ephemeris_500.json`. |
| Wed | Write tolerance test: `tests/unit/test_ephemeris_500.py` — Sun longitude within 0.01°, Moon longitude within 0.05° of reference. |
| Thu | Run tests. Investigate any failures — classify as: Moshier limitation, ayanamsa difference, or bug. |
| Fri | Fix any bugs found. Document known Moshier limitations for extreme dates. |
| Sat | Write ephemeris accuracy report: `docs/EPHEMERIS_ACCURACY.md`. |
| Sun | Buffer |

---

### Week 12 (May 18–24) — M3 Hardening

| Day | Deliverables |
|---|---|
| Mon | End-to-end test: from API request through UTC conversion through ephemeris through tithi through response — verify no timezone corruption at any stage. |
| Tue | Add ephemeris health check: `GET /api/engine/health` returns `{ ephemeris: "ok", ayanamsa: "lahiri", mode: "moshier" }`. |
| Wed | Performance profiling: measure ephemeris calculation time per call. Establish baseline for caching decisions. |
| Thu | Documentation: update `EVALUATOR_TECHNICAL_REPORT.md` to reflect corrected ephemeris claims. |
| Fri | M3 postmortem. Git tag `v2.0.3-m3`. |
| Sat | Prepare M4 spec. |
| Sun | Buffer / rest |

**M3 Definition of Done**: All engine computation uses UTC-aware datetimes. Ephemeris passes 500-timestamp tolerance test. Sidereal/tropical configurable. Documentation matches code.

---

## M4: Correct Tithi Semantics (May 25 – Jun 21, 2026)

### Week 13 (May 25–31) — Udaya Tithi Specification

| Day | Deliverables |
|---|---|
| Mon | Write formal spec for udaya tithi: definition, algorithm, edge cases (vriddhi, ksheepana). `docs/UDAYA_TITHI_SPEC.md`. |
| Tue | Audit current implementation: does `tithi_udaya.py` correctly use sunrise or does it use midnight? Document actual behavior vs correct behavior. |
| Wed | Implement `calculate_sunrise(date, lat, lon) → datetime_utc` using `swe.rise_trans()`. Verify against known Kathmandu sunrise times (almanac data). |
| Thu | Write sunrise test corpus: 50 dates across the year, expected sunrise time ±1 minute. `tests/fixtures/sunrise_kathmandu_50.json`. Source from timeanddate.com. |
| Fri | Run sunrise tests. Fix any failures. |
| Sat | Document sunrise calculation method and accuracy. |
| Sun | Buffer |

---

### Week 14 (Jun 1–7) — Udaya Tithi Implementation

| Day | Deliverables |
|---|---|
| Mon | Refactor `tithi_core.py`: `calculate_tithi(dt)` now takes explicit datetime (not date). Add `calculate_tithi_at_sunrise(date, location)` convenience function. |
| Tue | Implement vriddhi detection: when same tithi prevails at two consecutive sunrises, both days have that tithi. Add `detect_vriddhi(date, location) → bool`. |
| Wed | Implement ksheepana detection: when a tithi starts and ends between two sunrises, it's skipped. Add `detect_ksheepana(date, location) → bool`. |
| Thu | Build boundary-case corpus: 30 dates where tithi transitions happen within 2 hours of sunrise. `tests/fixtures/tithi_boundaries_30.json`. Source from Drik Panchang. |
| Fri | Run boundary tests. Each test asserts correct tithi number, paksha, vriddhi/ksheepana flag. |
| Sat | Fix any failures. Document edge cases. |
| Sun | Buffer |

---

### Week 15 (Jun 8–14) — API Integration & Method Metadata

| Day | Deliverables |
|---|---|
| Mon | Update `/api/calendar/today` response: add `tithi.method: "ephemeris_udaya"`, `tithi.reference_time: "sunrise"`, `tithi.sunrise_used: "2026-06-08T05:42:00+05:45"`. |
| Tue | Update `/api/calendar/panchanga` response: same treatment. Add `tithi.confidence: "exact"` for dates within ephemeris range. |
| Wed | Update `/api/calendar/tithi` endpoint (if exists) or create it: accepts date + optional location, returns full tithi details with method metadata. |
| Thu | Write API contract tests for new tithi fields: `tests/contract/test_tithi_response.py`. |
| Fri | Frontend integration: update calendar hooks to display tithi method info in tooltip/detail. |
| Sat | Cross-engine verification: compare tithi output against Drik Panchang for 10 random dates. |
| Sun | Buffer |

---

### Week 16 (Jun 15–21) — M4 Hardening

| Day | Deliverables |
|---|---|
| Mon | Moon-phase classifier refactor: ensure `elongation / 12°` formula is used everywhere, not synodic approximation. Grep for `29.53` — remove any synodic constants from active paths. |
| Tue | Full regression: run entire test suite including new boundary corpus. |
| Wed | Performance check: tithi calculation should be < 50ms per call. Profile and cache if needed. |
| Thu | Update evaluator report with corrected tithi methodology. |
| Fri | M4 postmortem. Git tag `v2.0.4-m4`. |
| Sat | Prepare M5 spec. |
| Sun | Buffer / rest |

**M4 Definition of Done**: Udaya tithi uses real sunrise. Vriddhi/ksheepana detected. Boundary corpus passes. API exposes method metadata.

---

## M5: Correct Lunar Month Model (Jun 22 – Jul 19, 2026)

### Week 17 (Jun 22–28) — Lunar Month Boundary Specification

| Day | Deliverables |
|---|---|
| Mon | Write formal spec: Amavasya→Amavasya month boundaries for Amant system. Purnimant naming convention (month named by Sun's rashi at Purnima). `docs/LUNAR_MONTH_SPEC.md`. |
| Tue | Audit current `lunar_calendar.py`: verify correctly uses Amavasya boundaries. Document deviations from spec. |
| Wed | Audit `adhik_maas.py`: verify "no sankranti in lunar month = adhik month" rule is correctly implemented. |
| Thu | Collect reference data: list of all Adhik Maas months from 2000–2030 BS from Rashtriya Panchang. Store in `tests/fixtures/adhik_maas_reference.json`. |
| Fri | Write Adhik Maas classification tests: for each reference year, assert Parva correctly identifies whether Adhik month exists and which month it is. |
| Sat | Run tests, document failures. |
| Sun | Buffer |

---

### Week 18 (Jun 29 – Jul 5) — Boundary Implementation

| Day | Deliverables |
|---|---|
| Mon | Implement `find_amavasya(search_start) → datetime`: find next Amavasya (tithi 30) using binary search on elongation approaching 360°/0°. |
| Tue | Implement `lunar_month_boundaries(year) → list[tuple[datetime, datetime]]`: return all Amavasya→Amavasya boundaries for a given year. |
| Wed | Implement `name_lunar_month(start_amavasya, end_amavasya) → str`: determine Sun's rashi at Purnima midpoint, return Purnimant name. |
| Thu | Implement `detect_adhik_maas(month_start, month_end) → bool`: check if any sankranti occurs within boundaries. If not, month is Adhik. |
| Fri | Integration: wire lunar month model into festival calculation pipeline — festivals using lunar month rules now use canonical boundaries. |
| Sat | Test: run festival calculations for Adhik Maas years — verify festivals shift correctly. |
| Sun | Buffer |

---

### Week 19 (Jul 6–12) — Sankranti Root-Finder

| Day | Deliverables |
|---|---|
| Mon | Audit `sankranti.py`: verify binary search for solar transit is correct. Test edge case where query time is already inside target rashi. |
| Tue | Implement Brent's method for transit finding — more robust than binary search for finding exact crossing point. Replace or supplement existing root-finder. |
| Wed | Write sankranti test corpus: 24 sankranti crossings (12 per year × 2 years). Verify against Drik Panchang. `tests/fixtures/sankranti_24.json`. |
| Thu | Run tests. Fix failures. Document accuracy. |
| Fri | Wire sankranti into BS month boundary detection: BS month starts when Sun enters next rashi. |
| Sat | End-to-end test: BS conversion → lunar month → festival date for monsoon festivals (most affected by Adhik Maas). |
| Sun | Buffer |

---

### Week 20 (Jul 13–19) — M5 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full regression including Adhik Maas years. Verify no month-shift regressions. |
| Tue | Update discrepancy register — any newly resolved mismatches. |
| Wed | Performance profiling of lunar month boundary computation (involves multiple ephemeris calls). |
| Thu | Documentation: update `LUNAR_MONTH_SPEC.md` with implementation notes. |
| Fri | M5 postmortem. Git tag `v2.0.5-m5`. |
| Sat | Prepare M6 spec. |
| Sun | Buffer / rest |

**M5 Definition of Done**: Amavasya→Amavasya boundaries implemented. Adhik Maas detection passes reference cases. Mid-year lunar festivals stable in overlap years.

---

## M6: 200-Year Conversion Strategy (Jul 20 – Aug 16, 2026)

### Week 21 (Jul 20–26) — Dual-Mode Conversion Design

| Day | Deliverables |
|---|---|
| Mon | Document current BS lookup table range (2070–2095). List all BS month-length data sources. Write `docs/BS_CONVERSION_STRATEGY.md`. |
| Tue | Design estimated-mode algorithm: use sankranti detection to find BS month boundaries astronomically. Each month starts at solar transit, month length = days between consecutive transits. |
| Wed | Implement `estimated_bs_to_gregorian(year, month, day) → date` using sankranti-based computation. |
| Thu | Implement `estimated_gregorian_to_bs(date) → BSDate` — reverse direction. |
| Fri | Build overlap dataset: for every date in official table range (2070–2095), compute both lookup and estimated. Store deltas. `tests/fixtures/bs_overlap_comparison.json`. |
| Sat | Analyze overlap deltas — characterize error distribution. Expected: most match, some ±1 day near month boundaries. |
| Sun | Buffer |

---

### Week 22 (Jul 27 – Aug 2) — Confidence Labeling

| Day | Deliverables |
|---|---|
| Mon | Implement `BSConversionResult` type: `{ year, month, day, month_name, confidence: "official"|"estimated", source_range: "2070-2095"|null }`. |
| Tue | Implement router function: `convert_bs(date)` → if in official range, use lookup + `confidence: "official"`. Else, use estimated + `confidence: "estimated"`. |
| Wed | Wire confidence into all API endpoints that return BS dates: `/convert`, `/today`, `/panchanga`, festival date responses. |
| Thu | Write tests: conversion at boundary of official range (2070-01-01, 2095-12-30). Verify confidence label transitions correctly. |
| Fri | Write tests for estimated mode: dates in 2000 BS, 2100 BS, 2150 BS. Verify results are reasonable and confidence is `estimated`. |
| Sat | Generate overlap error report: markdown table showing estimated vs official for every month of overlap. `docs/BS_OVERLAP_REPORT.md`. |
| Sun | Buffer |

---

### Week 23 (Aug 3–9) — Extended Range Validation

| Day | Deliverables |
|---|---|
| Mon | Collect known historical BS dates: 2050-01-01 BS, 2060-01-01 BS, etc. from reliable sources. Store in `tests/fixtures/bs_historical.json`. |
| Tue | Collect known future BS dates from pattern analysis and Nepal Patro projections. |
| Wed | Run estimated conversion against all collected dates. Compute accuracy on historical subset. |
| Thu | Implement error bound estimation: for estimated mode, compute typical error range based on overlap analysis. Add to response: `estimated_error_days: 0-1`. |
| Fri | Document limitations: "Beyond 2095 BS, dates are astronomically estimated and may differ from official calendar by ±1 day near month boundaries." |
| Sat | Write user-facing explanation text for the "why this date says estimated" UI feature (M10). |
| Sun | Buffer |

---

### Week 24 (Aug 10–16) — M6 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full regression including extended range conversions. |
| Tue | API contract tests: verify `confidence` field present in all BS date responses. |
| Wed | Frontend: ensure calendar display handles `confidence` field gracefully (show indicator for estimated dates). |
| Thu | Update evaluator report with conversion range claims matching actual implementation. |
| Fri | M6 postmortem. Git tag `v2.0.6-m6`. |
| Sat | Prepare M7 spec. |
| Sun | Buffer / rest |

**M6 Definition of Done**: Dual-mode conversion working. Every BS date carries `confidence`. Overlap error report generated. Extended range (2000–2200 BS) functional.

---

## M7: Data Ingestion Reliability (Aug 17 – Sep 13, 2026)

### Week 25 (Aug 17–23) — OCR Pipeline Hardening

| Day | Deliverables |
|---|---|
| Mon | Audit `backend/tools/ingest_moha_pdfs.py`: document current pipeline stages, success rate per stage, known failure modes. |
| Tue | Implement second-pass correction rules: common Nepali digit substitutions (० vs 0, ९ vs 9), month name spelling variants, common OCR errors. |
| Wed | Implement confidence scoring per extracted line: high (clean parse), medium (corrections applied), low (uncertain parse). |
| Thu | Add de-duplication logic: when same festival extracted from multiple PDFs, merge with conflict resolution. |
| Fri | Write OCR accuracy tests: run pipeline on 2080 PDF, compare against manually verified ground truth. Compute precision/recall. |
| Sat | Document OCR pipeline architecture and error handling in `docs/OCR_PIPELINE.md`. |
| Sun | Buffer |

---

### Week 26 (Aug 24–30) — Source Normalization

| Day | Deliverables |
|---|---|
| Mon | Define canonical festival name mapping: handle Nepali→English variants, alternative spellings, regional names. `data/festival_name_map.json`. |
| Tue | Implement `normalize_festival_name(raw_name) → canonical_id|null` with fuzzy matching for OCR-degraded inputs. |
| Wed | Implement source normalization jobs: standardize date formats, calendar types, and metadata across all ingested sources. |
| Thu | Build source comparison report: for each festival, show date from each source (MoHA, Rashtriya Panchang, computed). Highlight disagreements. |
| Fri | Add source metadata to `ground_truth_overrides.json`: each entry includes `source`, `confidence`, `extraction_date`, `notes`. |
| Sat | Automated source comparison runs as CI check — new discrepancies flagged immediately. |
| Sun | Buffer |

---

### Week 27 (Aug 31 – Sep 6) — Backfill Campaign

| Day | Deliverables |
|---|---|
| Mon | Identify available official sources for BS 2070–2079 (prior to existing 2080–2082). Search for MoHA PDFs, digital archives. |
| Tue | If PDFs found: run OCR pipeline on 2–3 years. If not: document gaps. |
| Wed | Cross-reference with Nepal Patro / Hamro Patro historical data for backfill years. |
| Thu | Merge all backfilled data into ground truth. Update discrepancy register. |
| Fri | Generate expanded accuracy scorecard: now covering 10+ years where data is available. |
| Sat | Document data gaps and strategy for future backfill. |
| Sun | Buffer |

---

### Week 28 (Sep 7–13) — M7 Hardening

| Day | Deliverables |
|---|---|
| Mon | End-to-end OCR pipeline test: take a raw PDF → produce overrides JSON → verify against ground truth. |
| Tue | Precision/recall tracking added to CI: `scripts/ocr_quality_check.py` runs after each pipeline execution. |
| Wed | Source normalization integration tests. |
| Thu | Documentation finalization: `docs/OCR_PIPELINE.md`, `docs/DATA_SOURCES.md` updated. |
| Fri | M7 postmortem. Git tag `v2.0.7-m7`. |
| Sat | Prepare M8 spec. |
| Sun | Buffer / rest |

**M7 Definition of Done**: OCR pipeline has second-pass correction. Precision/recall tracked. 10+ years of data backfilled where available. Source normalization operational.

---

## M8: Continuous Evaluation System (Sep 14 – Oct 11, 2026)

### Week 29 (Sep 14–20) — Evaluation Harness

| Day | Deliverables |
|---|---|
| Mon | Design evaluation harness: `backend/tools/evaluate_v4.py` — loads ground truth, runs V2 calculator for each entry, compares, produces structured report. |
| Tue | Implement harness with configurable parameters: year range, festival filter, output format (JSON, CSV, Markdown). |
| Wed | Add by-festival breakdown: for each festival, show pass/fail across all years. Identify systematically failing festivals. |
| Thu | Add by-rule breakdown: for each calculation rule type (lunar tithi, solar transit, BS fixed), show aggregate accuracy. |
| Fri | Implement delta analysis: when calculated differs from official, compute `delta_days` and classify cause. |
| Sat | Run initial evaluation. Generate `reports/evaluation_M8.md`. |
| Sun | Buffer |

---

### Week 30 (Sep 21–27) — Scorecard & Dashboard

| Day | Deliverables |
|---|---|
| Mon | Design monthly scorecard format: overall accuracy %, by-category accuracy, newly passing, newly failing, mismatch details. |
| Tue | Implement scorecard generator: `scripts/generate_scorecard.py` — produces markdown report. |
| Wed | Implement trend tracking: store evaluation results per run with timestamp. Plot accuracy trend over time. |
| Thu | Add scorecard to CI: evaluation runs on every PR that touches `engine/`, `rules/`, or `sources/`. PR blocked if accuracy drops. |
| Fri | Generate comparison scorecard: V2 accuracy now vs V1 accuracy (from M1 baseline). Show improvement. |
| Sat | Document evaluation methodology in `docs/EVALUATION_METHODOLOGY.md`. |
| Sun | Buffer |

---

### Week 31 (Sep 28 – Oct 4) — Mismatch Triage

| Day | Deliverables |
|---|---|
| Mon | For each remaining mismatch in evaluation: open investigation. Check rule, check ground truth source, check calendar boundaries. |
| Tue | Classify mismatches: fixable rule errors → fix immediately. Data errors in ground truth → correct source. Genuine limitations → document. |
| Wed | Implement fixes for fixable rule errors. Re-run evaluation after each fix. |
| Thu | Update ground truth for data errors (with audit trail). |
| Fri | Document genuine limitations with explanation of why they can't be algorithmically resolved. |
| Sat | Re-run full evaluation. Update scorecard. |
| Sun | Buffer |

---

### Week 32 (Oct 5–11) — M8 Hardening

| Day | Deliverables |
|---|---|
| Mon | Annual rerun pipeline: script that ingests new MoHA PDF (when published for 2083) and reruns full evaluation. `scripts/annual_rerun.sh`. |
| Tue | Evaluation comparison tests: verify scorecard generation works correctly. |
| Wed | CI gate tests: simulate accuracy drop, verify PR is blocked. |
| Thu | Documentation: `docs/EVALUATION_METHODOLOGY.md` finalized. |
| Fri | M8 postmortem. Git tag `v2.0.8-m8`. |
| Sat | Prepare M9 spec. |
| Sun | Buffer / rest |

**M8 Definition of Done**: Automated evaluation harness running. Monthly scorecard produced. CI blocks accuracy regressions. Every mismatch classified and documented.

---

## M9: External Contract Maturity (Oct 12 – Nov 8, 2026)

### Week 33 (Oct 12–18) — API v2 Specification

| Day | Deliverables |
|---|---|
| Mon | Write complete OpenAPI 3.1 specification for all endpoints. Use Pydantic-generated schemas as source of truth. |
| Tue | Add `method` fields to all calculation-related responses. Add `confidence` fields universally. Add `provenance` placeholder objects (filled in M11). |
| Wed | Version API paths: all endpoints now served under `/v2/`. Old paths redirect with deprecation header. |
| Thu | Publish OpenAPI spec at `/v2/openapi.json`. Set up Redoc at `/v2/docs`. |
| Fri | Write client examples in docs: curl, Python requests, JavaScript fetch — 3 examples per endpoint. |
| Sat | Review spec for completeness and consistency. |
| Sun | Buffer |

---

### Week 34 (Oct 19–25) — Contract Tests

| Day | Deliverables |
|---|---|
| Mon | Generate contract tests from OpenAPI spec: for each endpoint, automatically test that response matches schema. `tests/contract/test_openapi_compliance.py`. |
| Tue | Write backward compatibility tests: if v1 callers exist, verify v2 responses are superset-compatible. |
| Wed | Write client compatibility tests: simulate SDK-like calls, verify deserialization works for all response types. |
| Thu | Set up schema snapshot testing: golden schema files checked into repo. Any schema change requires explicit update. |
| Fri | Add deprecation infrastructure: `Deprecation` and `Sunset` headers on old endpoints. Log usage of deprecated paths. |
| Sat | Document deprecation timeline: old endpoints sunset in 6 months (M15). |
| Sun | Buffer |

---

### Week 35 (Oct 26 – Nov 1) — Developer Documentation

| Day | Deliverables |
|---|---|
| Mon | Write API Getting Started guide: `docs/API_GETTING_STARTED.md` — 5-minute tutorial from zero to first API call. |
| Tue | Write API Reference: auto-generated from OpenAPI spec with additional examples and notes. |
| Wed | Write error handling guide: every error code, what it means, how to fix it. |
| Thu | Write rate limiting and usage policy (even if no rate limiting now — plan for future). |
| Fri | Create example integration: minimal HTML page that calls Parva API and displays panchanga. Host in `examples/`. |
| Sat | Review all developer-facing documentation. |
| Sun | Buffer |

---

### Week 36 (Nov 2–8) — M9 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full E2E test: call every v2 endpoint, verify response against schema. |
| Tue | Load test: 100 concurrent requests to panchanga endpoint. Verify no errors on free-tier hardware profile. |
| Wed | Deprecation mechanism test: verify old endpoints return correct headers and redirects. |
| Thu | Documentation review: all links work, all examples run. |
| Fri | M9 postmortem. API v2 declared stable. Git tag `v2.1.0-stable`. |
| Sat | Prepare M10 spec. |
| Sun | Buffer / rest |

**M9 Definition of Done**: OpenAPI v2 spec published. Contract tests passing. Developer docs complete. Deprecation clock started on old endpoints.

---

## M10: UX Correctness-First (Nov 9 – Dec 6, 2026)

### Week 37 (Nov 9–15) — Frontend-Backend Schema Alignment

| Day | Deliverables |
|---|---|
| Mon | Audit all frontend API calls (`services/api.js`, hooks) — list every field consumed by every component. |
| Tue | Generate schema diff: fields frontend expects vs fields v2 API provides. List all mismatches. |
| Wed | Fix frontend hooks to consume v2 schemas: update `useFestivals.js`, `useFestivalDetail.js`, `useCalendar.js`. |
| Thu | Fix component PropTypes/types to match v2 response shapes. No more shape mismatches. |
| Fri | Write frontend contract tests (Jest): mock API responses with v2 schema, verify components render without errors. |
| Sat | Run full frontend build — zero warnings related to missing props or type mismatches. |
| Sun | Buffer |

---

### Week 38 (Nov 16–22) — "Why This Date" Explain Panel

| Day | Deliverables |
|---|---|
| Mon | Design explain panel UI: side panel or modal that shows "Why is Dashain on Oct 2, 2025?" with rule, calendar, tithi, source. |
| Tue | Implement `ExplainPanel.jsx` component — receives `calculation_trace_id` or inline explanation data. |
| Wed | Implement `ExplainPanel.css` — clean, readable, with code-like formatting for rule display. |
| Thu | Backend: add `/v2/festivals/{id}/explain?year=2082` endpoint that returns human-readable explanation: "Dashain = Ashwin Shukla 10. Ashwin Shukla 1 found on Sep 23 via udaya tithi. Count 10 days → Oct 2." |
| Fri | Wire frontend: "Why this date?" button on FestivalDetail → opens ExplainPanel → calls explain endpoint. |
| Sat | Polish: ensure explanation is understandable to non-technical user. Add Nepali calendar terms with tooltips. |
| Sun | Buffer |

---

### Week 39 (Nov 23–29) — Ritual Timeline & Empty States

| Day | Deliverables |
|---|---|
| Mon | Fix RitualTimeline rendering: verify `normalizeRitualData` adapter from M1 works for all 15 priority festivals. |
| Tue | Fix empty states: if festival has no ritual data, show "Ritual information coming soon" instead of empty tab. |
| Wed | Fix: if festival has no mythology, show curated placeholder. If no connections, show "Connections being documented." |
| Thu | Add loading skeletons to all async components: FestivalCard, FestivalDetail, RitualTimeline, Map. |
| Fri | Add error boundaries with retry buttons. Network failure → friendly message + retry. |
| Sat | Responsive audit: test all paths at 320px, 768px, 1024px, 1440px. Fix layout issues. |
| Sun | Buffer |

---

### Week 40 (Dec 1–6) — M10 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full usability walkthrough: Land → browse → select → read mythology → check ritual → see explain → check map. Screenshot each state. |
| Tue | Mobile usability walkthrough: same flow on 375px viewport. |
| Wed | Fix any UX issues found in walkthroughs. |
| Thu | Frontend build passes with zero warnings. All contract tests pass. |
| Fri | M10 postmortem. Git tag `v2.1.1-m10`. |
| Sat–Sun | Buffer / rest |

**M10 Definition of Done**: Frontend consumes only v2 schemas. No empty ritual tabs for valid data. "Why this date" explanation available. Loading/error/empty states polished.

---

## M11: Trust Primitives (Dec 7, 2026 – Jan 3, 2027)

### Week 41 (Dec 7–13) — Dataset & Rule Hashing

| Day | Deliverables |
|---|---|
| Mon | Implement `hash_dataset(festivals_json, ground_truth_json) → sha256`. Deterministic: if data hasn't changed, hash is identical. |
| Tue | Implement `hash_rules(festival_rules_v3.json, engine_config) → sha256`. Captures rule set + engine parameters. |
| Wed | Implement `create_snapshot(dataset_hash, rules_hash, timestamp) → SnapshotRecord` with unique `snapshot_id`. |
| Thu | Store snapshots in `data/snapshots/` as JSON. Each includes creation timestamp, hashes, engine version, data file paths. |
| Fri | Implement `verify_snapshot(snapshot_id) → { valid: bool, details }` — re-hash current data, compare against stored. |
| Sat | Write snapshot creation/verification tests: create snapshot, tamper with data, verify detection. |
| Sun | Buffer |

---

### Week 42 (Dec 14–20) — Merkle Proof Integration

| Day | Deliverables |
|---|---|
| Mon | Audit existing `merkle.py`: verify Merkle tree construction is correct. Add unit tests for tree building and proof generation. |
| Tue | Integrate Merkle tree with festival date snapshots: each festival's computed date for a given year is a leaf. Tree root = snapshot hash. |
| Wed | Implement `generate_proof(festival_id, year, snapshot_id) → MerkleProof` — inclusion proof for a specific festival date in the snapshot. |
| Thu | Implement `verify_proof(proof, root) → bool` — standalone verification that doesn't require the full dataset. |
| Fri | Add proof endpoint: `GET /v2/provenance/proof?festival=dashain&year=2082&snapshot=snap_2026Q4`. |
| Sat | Write tamper-detection tests: modify one festival date, verify Merkle proof fails. |
| Sun | Buffer |

---

### Week 43 (Dec 21–27) — Response Metadata

| Day | Deliverables |
|---|---|
| Mon | Add `provenance` object to all date-returning responses: `dataset_hash`, `rules_hash`, `snapshot_id`. |
| Tue | Add `verify_url` field: points to verification endpoint for this specific calculation. |
| Wed | Implement snapshot creation as part of deployment: every deploy creates a new snapshot of current data+rules. |
| Thu | Write verification script: external user can call `verify_url`, get proof, independently verify against published root. `scripts/verify_parva_response.py`. |
| Fri | Document trust system: `docs/TRUST_AND_PROVENANCE.md` — how snapshots work, how to verify, what's guaranteed. |
| Sat | Holiday buffer. |
| Sun | Holiday buffer. |

---

### Week 44 (Dec 28 – Jan 3) — M11 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full provenance integration test: make API call → extract provenance → verify proof → confirm integrity. |
| Tue | Tamper simulation: modify data → verify proof fails → restore → verify proof passes. |
| Wed | Performance: provenance adds < 5ms to response time. Profile and optimize if needed. |
| Thu | Documentation review. Git tag `v2.1.2-m11`. |
| Fri | M11 postmortem. Prepare M12 spec. |
| Sat–Sun | Rest / new year buffer |

**M11 Definition of Done**: Dataset + rule hashing operational. Merkle proofs for every festival date. Provenance metadata in all responses. Tamper detection verified.

---

## M12: Nepal Gold Release (Jan 4 – Feb 1, 2027)

### Week 45 (Jan 4–10) — Evaluator-Grade Technical Report

| Day | Deliverables |
|---|---|
| Mon | Write comprehensive technical report: architecture, algorithms, data pipeline, accuracy results, trust system. Target: 30+ pages. `docs/NEPAL_GOLD_TECHNICAL_REPORT.md`. |
| Tue | Include: algorithm specifications with equations, accuracy tables with per-festival breakdown, comparison against existing tools. |
| Wed | Include: limitation disclosures, known edge cases, future work. |
| Thu | Include: reproducibility instructions — exact commands to replicate every result. |
| Fri | Peer review report (self-review with critical eye). Revise. |
| Sat | Format for evaluator readability: table of contents, numbered sections, clean formatting. |
| Sun | Buffer |

---

### Week 46 (Jan 11–17) — Reproducible Benchmark Package

| Day | Deliverables |
|---|---|
| Mon | Create `benchmark/` directory: contains all test data, evaluation scripts, expected results. |
| Tue | Write `benchmark/README.md`: step-by-step instructions to run benchmark from scratch. |
| Wed | Write `benchmark/run_benchmark.sh`: single command that runs full evaluation and produces comparison report. |
| Thu | Test: clone repo fresh → install → run benchmark → verify results match published report. |
| Fri | Package as reproducible artifact: pin all dependency versions, include checksums for data files. |
| Sat | Create benchmark result summary: one-page PDF/MD showing headline accuracy and key metrics. |
| Sun | Buffer |

---

### Week 47 (Jan 18–24) — Annual Verification Dossier

| Day | Deliverables |
|---|---|
| Mon | Compile all verification results from M1–M11: scorecard history, mismatch register, resolution log. |
| Tue | Add 2083 BS verification: if MoHA calendar published, run OCR → ground truth → evaluate. If not, document as pending. |
| Wed | Compile mismatch audit: for every discrepancy that existed at M1 start, document final resolution (fixed, documented limitation, or data error). |
| Thu | Create accuracy trend chart: monthly accuracy from M1 through M12. Show trajectory. |
| Fri | Package into `docs/VERIFICATION_DOSSIER_2027.md`. |
| Sat | Review all verification artifacts for completeness. |
| Sun | Buffer |

---

### Week 48 (Jan 25 – Feb 1) — M12 Release & Retrospective

| Day | Deliverables |
|---|---|
| Mon | Final full regression: all tests pass. All evaluation gates pass. Nepal overlap accuracy ≥99%. |
| Tue | Freeze `v2.1` branch. Create release notes. |
| Wed | Deploy to free-tier hosting (Render/Railway + Vercel). Verify live endpoints match local results. |
| Thu | Publish: technical report, benchmark package, verification dossier. Git tag `v2.1.0-gold`. |
| Fri | Year 1 retrospective: what worked, what didn't, what to adjust for Year 2. `docs/YEAR_1_RETROSPECTIVE.md`. |
| Sat | Celebrate. Plan Year 2 kickoff. |
| Sun | Rest |

**M12 Definition of Done**: Nepal overlap accuracy ≥99%. Evaluator-grade technical report published. Reproducible benchmark available. v2.1 frozen and deployed. Year 1 complete. 🎉

---

*End of Year 1 Weekly Plan — 48 weeks, ~240 working days, from one-engine migration through Nepal Gold Standard release.*

---

## Year 1 Closure Extension (Weeks 49–52)

> Post-release closure sprint to fully package Year 1 for evaluator handover and deployment readiness.

### Week 49 — Closure Automation
- Add one-command closeout validation script.
- Generate closure logs and summary report artifact.

### Week 50 — Deployment Readiness
- Publish deployment runbook for free-tier targets.
- Add live smoke checker script for deployed URL verification.

### Week 51 — Handover Pack
- Publish artifact index for evaluator/supervisor navigation.
- Ensure all weekly status logs are discoverable and linked.

### Week 52 — Final Completion
- Publish Year 1 completion report.
- Freeze Year 1 documentation and closure evidence.
