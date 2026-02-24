# Project Parva — Project Bible (As-Built v3)

This is the complete, practical handbook for Project Parva as it exists now in this repository.

It is written for:
1. Evaluators and collaborators who need to understand the system quickly.
2. New developers onboarding to the codebase.
3. Maintainers who need a single, truthful reference for architecture, features, APIs, and operations.

---

## 1. What Project Parva Is

Project Parva is a Nepal-focused temporal computation platform.

In plain language, it answers:
- "What date is this in BS and AD?"
- "What is today's panchanga?"
- "When is this festival this year?"
- "Why was this date computed?"
- "What does my personal panchanga, muhurta, and kundali look like?"

Core direction:
- Public API profile is **v3** (`/v3/api/*`) with `/api/*` convenience alias.
- Experimental API tracks (`/v2`, `/v4`, `/v5`) are disabled by default.
- Truth-first policy: implementation claims must be verifiable by tests/reports.

---

## 2. Problem It Solves

Nepali festival and observance dates can be hard to coordinate because they depend on:
- Lunisolar rules (tithi, paksha, lunar months).
- Solar transitions (sankranti).
- Bikram Sambat to Gregorian conversion.
- Regional/practice variation.

Project Parva solves this through:
- A deterministic calendar engine.
- Rule-based festival computation.
- Explainability and trace metadata.
- Developer-friendly API and feed outputs.

---

## 3. Glossary (Beginner-Friendly)

- **AD / Gregorian**: International civil calendar.
- **BS (Bikram Sambat)**: Nepali official civil calendar.
- **Tithi**: Lunar day, derived from Sun-Moon angular separation.
- **Paksha**: Waxing (`shukla`) or waning (`krishna`) half of the lunar cycle.
- **Panchanga**: Five traditional daily elements (tithi, nakshatra, yoga, karana, vaara).
- **Udaya tithi**: Tithi at local sunrise (important for observance selection).
- **Adhik Maas**: Intercalary (leap) lunar month.
- **Sankranti**: Solar ingress/transit (Sun entering a zodiac sign).
- **Muhurta**: Favorable time window.
- **Kundali**: Birth-chart style astrological layout.

---

## 4. Current Capability Snapshot

Authoritative as-built status is in `docs/AS_BUILT.md`.

Latest release-gate artifacts in `docs/public_beta/month9_release_dossier.md` report:
- Computed festival rules: `323`
- Provisional rules: `111`
- Inventory/content-only rules: `19`
- Rule catalog total: `453`

Important nuance:
- "Catalog total" is not the same as "computed from first principles".
- Public scoreboards expose split metrics to avoid misleading claims.

---

## 5. Feature Catalog

### 5.1 Calendar Core

Implemented core calendar functions:
- BS ↔ Gregorian conversion.
- Tithi calculation.
- Panchanga daily computation.
- Sankranti-aware logic.
- Adhik handling in festival rule workflows.

Key API endpoints:
- `GET /v3/api/calendar/today`
- `GET /v3/api/calendar/convert?date=YYYY-MM-DD`
- `GET /v3/api/calendar/convert/compare?date=YYYY-MM-DD`
- `GET /v3/api/calendar/tithi?date=YYYY-MM-DD&latitude=&longitude=`
- `GET /v3/api/calendar/panchanga?date=YYYY-MM-DD`
- `GET /v3/api/calendar/panchanga/range?start=YYYY-MM-DD&days=7`

### 5.2 Festival Discovery + Explainability

Implemented festival features:
- List/search/filter festival catalog.
- Upcoming festivals.
- Festival detail and date range projection.
- Explanation endpoint for computed festival date rationale.
- Coverage scoreboards with quality bands.

Key API endpoints:
- `GET /v3/api/festivals`
- `GET /v3/api/festivals/upcoming`
- `GET /v3/api/festivals/{id}`
- `GET /v3/api/festivals/{id}/explain`
- `GET /v3/api/festivals/{id}/dates`
- `GET /v3/api/festivals/on-date/YYYY-MM-DD`
- `GET /v3/api/festivals/coverage`
- `GET /v3/api/festivals/coverage/scoreboard`

Quality filters:
- `quality_band=computed|provisional|inventory|all`
- `algorithmic_only=true|false`

### 5.3 Personal Stack (Major Expansion)

Implemented personal modules:
- Personal Panchanga.
- Muhurta day windows and auspicious ranking profiles.
- Rahu-kalam endpoint.
- Kundali v2 outputs with lagna/aspects/yoga/dosha/dasha structures.

Key API endpoints:
- `GET /v3/api/personal/panchanga?date=&lat=&lon=&tz=`
- `GET /v3/api/muhurta?date=&lat=&lon=&tz=&birth_nakshatra=`
- `GET /v3/api/muhurta/auspicious?date=&type=&...`
- `GET /v3/api/muhurta/rahu-kalam?date=&lat=&lon=&tz=`
- `GET /v3/api/kundali?datetime=&lat=&lon=&tz=`
- `GET /v3/api/kundali/lagna?datetime=&lat=&lon=&tz=`

Response metadata includes:
- `engine_version`
- `calculation_trace_id`
- `confidence`
- `method_profile`
- `quality_band`
- `assumption_set_id`
- `advisory_scope`
- `policy`

### 5.4 Feeds + Integrations

Implemented feed surfaces:
- All festivals iCal feed.
- Category-specific iCal feeds.
- Custom iCal by selected festival IDs.

Key API endpoints:
- `GET /v3/api/feeds/all.ics`
- `GET /v3/api/feeds/national.ics`
- `GET /v3/api/feeds/newari.ics`
- `GET /v3/api/feeds/custom.ics`

### 5.5 Plugin Quality and Engine Profile

Implemented plugin quality visibility:
- `GET /v3/api/engine/calendars`
- `GET /v3/api/engine/convert`
- `GET /v3/api/engine/plugins/quality`

Current plugin set includes:
- bs
- ns
- tibetan
- islamic
- hebrew
- chinese
- julian

### 5.6 Trust/Trace Support

Implemented support layers:
- Deterministic trace IDs and explain outputs.
- Provenance and reliability modules in backend.

Exposure behavior:
- Some trust routes are environment-gated by bootstrap configuration.
- Public profile remains v3-first and can keep trust surfaces minimal.

---

## 6. Frontend Product Surface

Frontend app (`frontend/src/App.jsx`) provides routes:
- `/` — Festival Explorer
- `/festivals/:festivalId` — Festival Detail
- `/panchanga` — Panchanga Viewer
- `/personal` — Personal Panchanga
- `/muhurta` — Muhurta Finder
- `/kundali` — Kundali Studio
- `/feeds` — iCal Subscriptions
- `/dashboard` — Authority/Dashboard view

Key component groups:
- Festival components (`FestivalCard`, `FestivalDetail`, `RitualTimeline`, `ExplainPanel`, etc.)
- Calendar components (`LunarPhase`, `TemporalNavigator`)
- Map components (`FestivalMap`)
- UI support (`AuthorityInspector`, `ErrorBoundary`)

Ritual timeline adapter fix (important):
- `FestivalDetail` normalizes backend ritual payloads before rendering `RitualTimeline`.
- This resolves schema mismatch where timeline expected `ritualSequence.days`.
- File: `frontend/src/components/Festival/FestivalDetail.jsx`.
- Regression test: `frontend/src/test/FestivalDetailRitualSchema.test.jsx`.

---

## 7. Backend Architecture

### 7.1 App Bootstrap

Primary entry + composition:
- `backend/app/main.py`
- `backend/app/bootstrap/app_factory.py`
- `backend/app/bootstrap/middleware.py`
- `backend/app/bootstrap/router_registry.py`

Responsibilities:
- Build FastAPI app.
- Read env config.
- Attach CORS and request guards.
- Register v3 public routers.
- Optionally enable experimental tracks.

### 7.2 Domain Modules

Core areas:
- `backend/app/calendar/` — calendar math, panchanga, tithi, sankranti, personal stack math.
- `backend/app/festivals/` — festival APIs/models/workflows.
- `backend/app/rules/` — rule catalog, DSL conversion, execution, triad pipeline.
- `backend/app/engine/plugins/` — pluggable calendar backends and quality validations.
- `backend/app/explainability/` — trace handling.
- `backend/app/provenance/`, `backend/app/reliability/` — trust/reliability surfaces.

### 7.3 Data and Content

Main content and rule files:
- `data/festivals/festivals.json`
- `data/festivals/festival_rules_v4.json`
- `data/festivals/rule_ingestion_seed.json`
- `data/festivals/rule_execution_templates.json`
- `data/festivals/rule_triads/`
- `data/festivals/festival_locations.json`
- `data/festivals/temples.json`

Runtime-derived files (git-trimmed policy):
- snapshots under `backend/data/snapshots/` (minimal retained set)
- traces generated at runtime (not tracked long-term)

---

## 8. Rule System: What "Computed" Means Here

Project Parva uses a quality model for rules:
- `computed`
- `provisional`
- `inventory`

A rule should be treated as production-grade computed only when it has:
1. Executable DSL/rule path.
2. Evidence artifact.
3. Validation case coverage.

Rule triad artifacts are generated and stored under:
- `data/festivals/rule_triads/<rule-id>/rule.json`
- `data/festivals/rule_triads/<rule-id>/evidence.json`
- `data/festivals/rule_triads/<rule-id>/validation_cases.json`

---

## 9. Testing and Quality Gates

### 9.1 Test Stack

Backend tests:
- unit + integration + contract + conformance packs.

Frontend tests:
- route tests
- feature tests
- visual baseline snapshots (Vitest)

### 9.2 Primary Commands

Local quality checks:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
PYTHONPATH=backend python3 -m pytest -q
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

Contract and conformance:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py
```

Full release gate pack:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
bash scripts/release/run_month9_release_gates.sh
```

---

## 10. Deployment and Operations

Deployment profile is documented in `docs/DEPLOYMENT.md`.

Current practical production approach (zero-budget friendly):
- Frontend/static artifacts: GitHub Pages or similar free tier.
- Backend API: Render/Railway/Fly free tier.
- CORS + profile flags controlled via env vars.

Important environment variables:
- `CORS_ALLOW_ORIGINS`
- `PARVA_ENABLE_EXPERIMENTAL_API` (default `false`)
- `PARVA_ENV`
- `PARVA_MAX_REQUEST_BYTES`
- `PARVA_MAX_QUERY_LENGTH`

Smoke test script:
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
python3 scripts/live_smoke.py --base https://<your-backend-host>
```

---

## 11. Truthful Production Readiness Position

Project Parva is production-ready for a scoped v3 launch when:
1. Release gates are green.
2. Deploy config env vars are set correctly.
3. Live smoke checks pass against deployed host.

It is not claiming:
- Universal religious authority across all traditions.
- Fully complete global calendar standardization.
- Community/AR layers as finished production modules.

---

## 12. Known Limits (Must Read)

See `docs/KNOWN_LIMITS.md` for the canonical list.

Key themes:
- Regional observance interpretation can differ.
- Some rule entries remain provisional.
- Boundary conditions depend on location/timezone assumptions.
- Personal stack is advisory/informational.
- Free-tier infra may show cold-start latency.

---

## 13. How To Extend Safely

If you are adding features:
1. Add feature code.
2. Add/adjust tests (unit + integration + contract as needed).
3. Run release gates.
4. Update docs in this order:
   - `docs/AS_BUILT.md` (what is actually done)
   - `docs/API_REFERENCE_V3.md` (interface changes)
   - this Project Bible (system-level understanding)

If adding festival rules:
1. Update seed/rule catalog.
2. Generate triad artifacts.
3. Validate quality band and scoreboard impact.
4. Ensure dashboard/report outputs stay truthful.

---

## 14. Fast Onboarding Checklist

For a new teammate, do this in order:
1. Read this file (`docs/PROJECT_BIBLE.md`).
2. Read `docs/AS_BUILT.md`.
3. Run backend + frontend locally.
4. Hit `/v3/api/calendar/today` and `/v3/api/festivals/upcoming`.
5. Run tests and release gates.
6. Open frontend routes and validate happy/error/loading states.

---

## 15. Canonical Companion Docs

- `docs/AS_BUILT.md`
- `docs/API_REFERENCE_V3.md`
- `docs/ENGINE_ARCHITECTURE.md`
- `docs/ACCURACY_METHOD.md`
- `docs/KNOWN_LIMITS.md`
- `docs/DEPLOYMENT.md`
- `docs/EVALUATOR_GUIDE.md`
- `docs/spec/PARVA_TEMPORAL_SPEC_V1.md`
- `docs/public_beta/month9_release_dossier.md`

---

## 16. One-Sentence Summary

Project Parva is a v3-first Nepali temporal computation platform with a strong calendar core, rule-based festival intelligence, personal planning modules, and a truth-first quality pipeline designed for reproducible real-world use.
