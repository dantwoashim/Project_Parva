# Project Parva Audit, Honest Review, and Zero-Budget Launch Guide

Audit date: 2026-03-13

Repository audited: `d:\Project_Parva-main\Project_Parva-main`

## 1. Scope and method

This audit covered:

- product idea and positioning
- backend, frontend, SDK, scripts, docs, and data layout
- local verification of tests, lint, build, type checks, conformance, and audits
- current web research on competitors, hosting constraints, and Nepal digital market context

Important limitations:

- The provided workspace is not a Git repository, so commit history, author ownership, blame, and release history could not be audited.
- No live production deployment was provided, so runtime findings come from local execution and code inspection.
- "0 issues", "almost sure commercial success", and "most accurate on the planet" are not honest guarantees any competent reviewer can make. The realistic goal is: no known P0/P1 defects at launch, artifact-backed accuracy claims, fast incident response, and a commercial wedge strong enough to earn trust and revenue.

## 2. Executive summary

### One-sentence verdict

Project Parva is a strong, ambitious, unusually thoughtful public-beta foundation for Nepal-focused temporal infrastructure, but it is not yet an authority-grade, commercially launch-ready product.

### What is already genuinely strong

- The core idea is good: open, API-first, explainable Nepal calendrical infrastructure is more differentiated than "another calendar app."
- The backend architecture is serious enough to become production software.
- The docs are better than most projects at this stage.
- The Python test base is real, not fake.
- The project already has meaningful launch ingredients: provenance, explainability, health endpoints, contract freeze checks, precompute scripts, security headers, and operational docs.

### What is not yet true

- It is not currently accurate enough to market as the most accurate engine on Earth.
- It is not currently consistent enough to market as a single authoritative product surface.
- It is not currently production-ready on the advertised zero-dollar Render path.
- It is not currently ready to win the broad consumer "calendar + astrology + utility super-app" battle against incumbents.

### Current maturity assessment

| Area | Score | Comment |
|---|---:|---|
| Product idea | 8/10 | Real need, good differentiation if narrowed correctly |
| Backend architecture | 7/10 | Strong foundation with some sprawl and error-swallowing |
| Accuracy credibility | 4/10 | Good ambition, but raw evidence does not support strongest claims |
| Frontend readiness | 6/10 | Attractive direction, but contract drift and flaky tests remain |
| Content completeness | 3/10 | Too much of the catalog is still shallow |
| Ops readiness | 5/10 | Good internal scaffolding, weak real zero-budget production path |
| Commercial readiness | 3/10 | Needs focus, distribution, proof, and a narrower moat |

### Blunt bottom line

If launched today as "the definitive Nepali temporal authority app/API," it would likely earn curiosity, then skepticism, once advanced users compare disputed dates, thin content, missing source citations, and inconsistent frontend detail rendering.

If narrowed and rebuilt around "the most transparent, verifiable Nepal calendar and festival API," it has real potential.

## 3. What Parva actually is right now

### Product identity

Based on the repository and docs, Parva is trying to be:

- a Nepal-focused temporal computation engine
- a public `v3` API under `/v3/api/*`
- a frontend experience for festival discovery, panchanga, calendar exploration, feeds, personal panchanga, muhurta, kundali, and temporal explainability
- an explainable and provenance-aware alternative to black-box calendar apps

Core product references:

- `README.md`
- `docs/PROJECT_BIBLE.md`
- `docs/VISION.md`
- `docs/AS_BUILT.md`

### Repository size snapshot

Measured locally:

| Area | Files | Lines | Notes |
|---|---:|---:|---|
| `backend/app` | 158 Python files | 22,767 | main application code |
| `frontend/src` | 80 JS/JSX/CSS files | 12,012 | app UI |
| `tests` | 65 Python files | 3,470 | primary Python tests |
| `frontend/src/test` | 8 files | 997 | frontend tests |
| `scripts` | 35 Python files | 4,672 | release, spec, precompute, security |
| `sdk/python` | 6 Python files | 424 | mixed old/new SDK state |
| `data` | 1,376 JSON files | 50,227 | major data footprint |

### Major backend domains

Top-level backend packages under `backend/app/`:

- `bootstrap`: app factory, middleware, request guards, access control
- `calendar`: BS conversion, tithi, panchanga, sankranti, kundali, muhurta, ephemeris
- `festivals`: models, repository, public routes
- `rules`: v4 catalog, rule execution, variants, service wrapper
- `provenance`: traceability and verification surfaces
- `reliability`: metrics, status, SLO helpers
- `api`: personal stack routes and feature-specific APIs
- `services`: service-layer helpers
- `cache`: precomputed artifacts

### Major frontend domains

Top-level frontend packages under `frontend/src/`:

- `pages`: route-level screens
- `components`: reusable UI
- `hooks`: API state hooks
- `services`: fetch wrapper and endpoint clients
- `context`: shared temporal state
- `styles`: design tokens and shared styling

### Route footprint

Rough count from router decorators: about 108 endpoint declarations across backend route modules.

That is a lot of API surface for a zero-budget team and materially increases:

- testing cost
- documentation cost
- accuracy burden
- support burden
- commercial positioning confusion

## 4. Local verification results

Commands run during the audit:

| Command | Result | Interpretation |
|---|---|---|
| `npm --prefix frontend run lint` | passed | frontend lint baseline is healthy |
| `npm --prefix frontend run test -- --run` | failed | 2 `AppRoutes` tests timed out |
| `npm --prefix frontend run build` | passed | frontend builds |
| `py -3.11 -m pytest -q` | `329 passed` | strong Python test baseline |
| `py -3.11 -m ruff check backend tests scripts sdk` | failed | 7 lint issues, mostly SDK/import order |
| `py -3.11 -m mypy` | passed | but only on a narrow subset of files |
| `py -3.11 scripts/check_path_leaks.py` | passed | no local path leak findings |
| `py -3.11 scripts/check_docs_links.py` | passed | docs links locally valid |
| `py -3.11 scripts/validate_festival_catalog.py` | passed | 49-entry festival catalog validates |
| `py -3.11 scripts/release/check_contract_freeze.py` | passed | v3 contract freeze script passes |
| `py -3.11 scripts/spec/run_conformance_tests.py` | passed | only 6 in-process conformance cases |
| `py -3.11 scripts/release/check_license_compliance.py` | passed | licensing guard passes |
| `py -3.11 scripts/security/run_audit.py` | failed | pip/npm audit findings present |
| production import with `PARVA_ENV=production` and no `PARVA_SOURCE_URL` | failed on startup | production deployment guard works, blueprint misses required env |

### Important nuance on "green" signals

- `mypy` passing is not a whole-codebase pass. `pyproject.toml` only targets a small subset of files.
- the conformance suite covers only 6 cases, while the API surface is much larger
- frontend build and lint passing do not cancel out failing frontend tests
- the benchmark script can report a perfect score while still not proving real-world date correctness

## 5. Architecture guide

### 5.1 Boot and runtime flow

The app startup story is one of the strongest parts of the repo.

Key files:

- `backend/app/main.py`
- `backend/app/bootstrap/app_factory.py`
- `backend/app/bootstrap/settings.py`
- `backend/app/bootstrap/router_registry.py`
- `backend/app/bootstrap/middleware.py`
- `backend/app/bootstrap/access_control.py`

What this layer already does well:

- validates risky production settings at startup
- publishes `/health/live`, `/health/ready`, `/health/startup`
- has request-size and query-length guards
- supports scoped API keys for non-public surfaces
- adds request IDs and structured logs
- handles frontend serving and `/source` redirection

### 5.2 Calendar and accuracy engine

Important files:

- `backend/app/calendar/bikram_sambat.py`
- `backend/app/calendar/tithi.py`
- `backend/app/calendar/tithi/tithi_core.py`
- `backend/app/calendar/tithi/tithi_udaya.py`
- `backend/app/calendar/panchanga.py`
- `backend/app/calendar/ephemeris/swiss_eph.py`
- `backend/app/calendar/calculator.py`
- `backend/app/calendar/calculator_v2.py`
- `backend/app/calendar/lunar_calendar.py`
- `backend/app/calendar/overrides.py`

Reality:

- the codebase contains multiple generations of calculation logic
- newer paths do use ephemeris-backed and sunrise-based logic
- older/legacy/fallback calculation paths still exist
- overrides are used to align outputs with official or ground-truth expectations

### 5.3 Festival content and public discovery

Important files:

- `backend/app/festivals/models.py`
- `backend/app/festivals/repository.py`
- `backend/app/festivals/routes.py`
- `data/festivals/festivals.json`
- `data/festivals/festival_rules_v4.json`

This layer combines:

- structured festival content
- next-occurrence computation
- rule quality metadata
- explainability and provenance

### 5.4 Rule and variant layer

Important files:

- `backend/app/rules/catalog_v4.py`
- `backend/app/rules/execution.py`
- `backend/app/rules/service.py`
- `backend/app/rules/variants.py`

This is the heart of Parva's authority story, but it is also where naming, confidence, and coverage semantics need the most cleanup.

### 5.5 Provenance, explainability, trust

Important files:

- `backend/app/explainability/store.py`
- `backend/app/provenance/routes.py`
- `backend/app/provenance/snapshot.py`
- `backend/app/provenance/transparency.py`

This is one of the most differentiated parts of the project.

Most incumbents compete on habit, utility bundling, or astrology scale.
Parva can compete on:

- traceability
- verifiability
- openly inspectable assumptions
- contract stability

### 5.6 Frontend composition

Important files:

- `frontend/src/App.jsx`
- `frontend/src/services/api.js`
- `frontend/src/hooks/useFestivals.js`
- `frontend/src/hooks/useCalendar.js`
- `frontend/src/pages/FestivalExplorerPage.jsx`
- `frontend/src/pages/FestivalDetailPage.jsx`
- `frontend/src/pages/TemporalCompassPage.jsx`
- `frontend/src/pages/PanchangaPage.jsx`
- `frontend/src/pages/ParvaPage.jsx`
- `frontend/src/components/Festival/FestivalDetail.jsx`

The frontend has a real product shape, not just placeholder pages.
The main concern is not "ugly UI."
The main concern is consistency and truthfulness of the data it renders.

## 6. Detailed technical findings

### 6.1 Accuracy claims are ahead of the evidence

This is the single biggest issue in the project.

Evidence:

- `data/ground_truth/scorecard_2080_2082.json`
- `backend/app/calendar/calculator_v2.py`
- `backend/app/calendar/overrides.py`
- `backend/app/calendar/ground_truth_overrides.json`

Key numbers from the scorecard:

- raw exact-match rate: `24.44%`
- exact-match rate with overrides: `86.67%`

Interpretation:

- the raw algorithmic engine is not yet strong enough to carry the strongest authority claims by itself
- a large part of the current practical accuracy comes from manual authoritative overrides
- the project is currently a hybrid rules-plus-overrides system, not yet a dominantly self-sufficient authority engine

This does not make the project bad.
It does mean the messaging must change immediately.

### 6.2 The "323 computed rules" headline is directionally useful but commercially misleading

Evidence:

- `docs/PROJECT_BIBLE.md`
- `docs/public_beta/month9_release_dossier.md`
- `data/festivals/festival_rules_v4.json`

Observed rule-catalog facts:

- total rules: `453`
- computed: `323`
- provisional: `130` in raw catalog status accounting
- only `21` of the computed rules are `high` confidence
- computed high-confidence share: about `6.5%`

Top rule families in the v4 file include many repeating observance families:

- `weekly_vrata`: `84`
- multiple monthly rule families at `24` each

Why this matters:

- rule count is not the same as user-perceived festival coverage
- many of the counted rules are recurring observances, not flagship Nepal-specific public-holiday wins
- a marketing claim like "300+ computed rules" sounds stronger than the user experience actually is

Related content reality:

- user-facing festival content entries: `49`

So the project currently has a much bigger rules story than content story.

### 6.3 Manual override dependence is real and currently under-explained

Evidence:

- `backend/app/calendar/overrides.py`
- `backend/app/calendar/ground_truth_overrides.json`

Observed facts:

- 67 override pairs across 5 year buckets (`2023` to `2027`)
- override-first behavior exists in `calculator_v2`

That can be acceptable if communicated honestly.
It becomes dangerous when hidden behind "fully computed" language.

### 6.4 Public evidence artifacts are inconsistent

Evidence:

- `data/ground_truth/scorecard_2080_2082.json`
- `data/ground_truth/discrepancies.json`

Problem:

- `scorecard_2080_2082.json` shows significant raw mismatches
- `discrepancies.json` reports `failure_count: 0`
- `discrepancies.json` claims it was generated from `reports/evaluation_v4/evaluation_v4.json` (generated artifact), but that file is not present in the audited workspace

Impact:

- trust in the project's accuracy reporting is weakened
- reviewers cannot easily tell which artifact is canonical

### 6.5 Frontend festival detail route is stale and mismatched against the backend contract

Evidence:

- `frontend/src/App.jsx`
- `frontend/src/pages/FestivalDetailPage.jsx`
- `frontend/src/components/Festival/FestivalDetail.jsx`
- `backend/app/festivals/models.py`

What is happening:

- the main router serves `FestivalDetailPage`
- the dashboard uses a different `FestivalDetail` component
- the component appears more aligned to the backend contract than the route page

Specific mismatches in `FestivalDetailPage.jsx`:

- expects `festival.calendar_system`, but backend model exposes `calendar_type`
- expects `festival.regions`, but backend model exposes `regional_focus`
- uses `festival.deities.join(', ')`, but backend model defines `deities` as `List[DeityLink]`
- references `dates?.calculation_method`, which is not part of the `FestivalDates` model

Impact:

- blank or broken fields on real data
- misleading tests if mocks use the wrong shape
- duplicated maintenance burden

### 6.6 There are two competing festival detail implementations

Evidence:

- route page: `frontend/src/pages/FestivalDetailPage.jsx`
- canonical component: `frontend/src/components/Festival/FestivalDetail.jsx`
- dashboard usage: `frontend/src/pages/ParvaPage.jsx`

Impact:

- duplicated UI logic
- inconsistent contract assumptions
- higher chance of regressions

### 6.7 The local fallback in `useCalendar` undermines trust if surfaced too casually

Evidence:

- `frontend/src/hooks/useCalendar.js`

The file itself warns:

- the fallback is a simplified approximation
- it can be off by up to around 15 days near month boundaries

But the fallback payload also sets:

- `estimatedErrorDays: '0-1'`

That is contradictory.

Impact:

- confidence labels become unreliable
- users may assume precision that the code explicitly does not provide

### 6.8 Frontend tests are flaky or broken at route level

Evidence:

- `frontend/src/test/AppRoutes.test.jsx`
- local run of `npm --prefix frontend run test -- --run`

Observed behavior:

- 2 tests timed out
- React warnings indicated Suspense/state update timing issues not fully wrapped in `act(...)`

Impact:

- CI confidence is lower than it appears
- route-level navigation can regress undetected

### 6.9 CI and type coverage do not cover the whole repo

Evidence:

- `.github/workflows/ci.yml`
- `pyproject.toml`

Important gaps:

- CI runs `ruff check backend tests scripts`, but not `sdk`
- `mypy` only checks a narrow hand-picked subset of files
- frontend route tests are currently red locally

Translation:

- "CI exists" is true
- "the repo is fully quality-gated" is not true

### 6.10 The Python SDK is in a mixed and confusing state

Evidence:

- old package: `sdk/python/parva/__init__.py`
- newer package: `sdk/python/parva_sdk/client.py`
- tests: `tests/unit/sdk/test_python_sdk.py`

Findings:

- the new SDK defaults to `/v3/api` and is the only one meaningfully tested
- the old SDK still points to dead or legacy endpoints such as:
  - `/api/calendar/cross/convert`
  - `/api/calendar/ical`
  - `/api/engine/health`
  - `/api/engine/config`

Impact:

- high risk of shipping a broken public SDK experience
- confusing package story for users and maintainers

### 6.11 The codebase still has version and generation sprawl

Examples:

- `calculator.py`
- `calculator_v2.py`
- `festival_rules.json`
- `festival_rules_v3.json`
- `festival_rules_v4.json`
- public v3 API plus experimental `/v2`, `/v4`, `/v5`

Why it matters:

- the project vision says to avoid version proliferation in the public narrative
- the codebase still carries a lot of historical and parallel logic
- every extra version path increases accuracy ambiguity

### 6.12 Error handling is often too broad in critical paths

Observed across:

- `backend/app/festivals/repository.py`
- `backend/app/rules/execution.py`
- `backend/app/calendar/calculator.py`
- `backend/app/calendar/calculator_v2.py`
- `backend/app/calendar/routes.py`
- `backend/app/calendar/ephemeris/swiss_eph.py`

Impact:

- failures are silently converted into `None`, fallback outputs, or generic responses
- root causes become harder to triage
- correctness bugs can hide behind degraded behavior

### 6.13 The repo has a latent package import fragility and circular import risk

Evidence:

- `backend/app/cache/__init__.py`
- `backend/app/cache/precomputed.py`
- `backend/app/reliability/__init__.py`
- `backend/app/reliability/status.py`

Observed during audit:

- importing `app.rules.catalog_v4` directly caused a circular import failure through `app.cache` and `app.reliability`

This is not yet a production-stopper, but it is a maintainability smell and a sign that package-level imports are too eager.

### 6.14 Content completeness is far behind product ambition

Measured from `data/festivals/festivals.json`:

- total festivals: `49`
- `complete`: `16`
- `basic`: `9`
- `minimal`: `24`
- festivals with mythology summary: `3`
- festivals with origin story: `3`
- festivals with daily rituals: `2`
- festivals with detailed `deities`: `0`
- festivals with `locations`: `0`
- festivals with `images`: `0`
- festivals with `sources`: `0`

This is one of the strongest reasons the product is not yet authority-grade.

You cannot credibly claim deep cultural explainability when almost all content lacks source citations.

### 6.15 Regional and variant coverage is still thin

Measured from `festival_rules_v4.json`:

- rules with region data: `34`
- rules with variant profiles: `3`

That is not enough to claim broad jurisprudential coverage across Nepal's real regional and ritual differences.

### 6.16 There is still API surface duplication

Examples:

- `/v3/api/calendar/festivals/upcoming`
- `/v3/api/festivals/upcoming`

Duplication is survivable, but on zero budget it increases:

- documentation burden
- SDK burden
- deprecation burden

### 6.17 The benchmark script is easy to over-read

Evidence:

- `backend/tools/benchmark_runner.py`

The benchmark mostly checks:

- round-trips
- shape validity
- whether festival calculations return something

It does not prove:

- official holiday alignment
- doctrinal correctness
- regional correctness

So a high or perfect benchmark result should not be marketed as high real-world accuracy.

### 6.18 Security posture is better than average for this stage, but not ready for confident launch claims

What is good:

- request size guard
- query-length guard
- request IDs
- structured logs
- security headers
- rate limiting
- scoped keys for non-public surfaces
- startup validation

What still needs work:

- local `pip_audit` surfaced 14 vulnerabilities in 5 packages, several from ambient environment packages not declared in `pyproject.toml`
- local `npm audit` surfaced 1 high-severity issue in `flatted`, transitively via ESLint tooling
- the current audit script does not distinguish runtime risk from dev-only or environment-only noise

Conclusion:

- the project has a healthy security foundation
- the security reporting workflow still needs policy, scoping, and triage discipline

### 6.19 The advertised zero-budget Render deployment path is not production-ready

Evidence:

- `render.yaml`
- `Dockerfile`
- `backend/app/bootstrap/settings.py`
- `docs/DEPLOYMENT.md`

Problems:

- production startup requires `PARVA_SOURCE_URL`
- `render.yaml` does not set `PARVA_SOURCE_URL`
- official Render docs explicitly say Free web services spin down after 15 minutes idle and should not be used for production

This is a hard contradiction between repo guidance and actual platform limitations.

### 6.20 In-process conformance is not the same as live deployment confidence

Evidence:

- `scripts/spec/run_conformance_tests.py`
- `tests/conformance/conformance_cases.v1.json`

What passed:

- 6 conformance checks

What that does not mean:

- 108 endpoints are well-covered
- deployment, CDN, proxy, env-var, or cold-start behavior is covered
- private-route POST behavior is fully tested

## 7. Honest product review

### What this project is best at today

Parva is best today as:

- an ambitious research or prototype platform
- a public-beta API foundation
- a trust-oriented alternative to black-box calendrical products
- a serious internal base for a future Nepal temporal infrastructure company

### What it is not best at today

Parva is not best today as:

- a mass-market consumer calendar super-app
- a production-grade astrology platform
- a culturally complete and sourced encyclopedia
- a proven top-accuracy engine across all disputed cases

### My most honest judgment

The project's strongest asset is not its current accuracy.
Its strongest asset is the combination of:

- openness
- technical seriousness
- explainability
- structure
- a product vision centered on trust instead of pure engagement

That is rare.
It is also not enough by itself.

Without a much stronger accuracy corpus, better source-backed content, and a sharper market wedge, the project risks becoming "impressive to engineers, not decisive to users."

## 8. Market and competitor research

Research date: 2026-03-13

### 8.1 Market context

Relevant current signals:

- DataReportal's latest Nepal report says there were about `16.6 million` internet users in Nepal in late 2025 and 2026-level reporting, around `56.0%` penetration.
- IMF reporting continues to show Nepal as highly remittance-linked, with remittances averaging roughly `23%` of GDP over 2015-2024.

Implication:

- this is not just a domestic holiday app market
- diaspora use cases matter
- location-sensitive festival correctness matters
- cross-border Nepali identity products can have real demand even if Nepal's domestic ad market is limited

Sources:

- https://datareportal.com/reports/digital-2026-nepal
- https://www.imf.org/en/News/Articles/2025/03/14/pr25063-nepal-imf-completes-the-fifth-review-under-the-extended-credit-facility-arrangement
- https://www.imf.org/-/media/Files/Publications/CR/2025/English/1nplea2025002-source-pdf.ashx

### 8.2 Direct consumer competitors

| Competitor | What they are strong at | What this means for Parva |
|---|---|---|
| Hamro Patro | habit, utility bundling, scale, super-app behavior | very hard to beat head-on in broad consumer utility |
| Nepali Patro | mainstream calendar, news, astrology, reminders | basic calendar feature parity is not enough |
| Mero Patro and similar | day-to-day utility convenience | the commodity calendar app space is crowded |
| Digital Patro and Simple Patro | clean, lightweight, modern alternatives | even minimal calendar app is now contested |

Relevant sources:

- https://apps.apple.com/us/app/hamro-patro-nepali-calendar/id401074157
- https://english.hamropatro.com/news/details/8487492033134839
- https://apps.apple.com/us/app/nepali-patro/id664588996
- https://apps.apple.com/us/app/mero-patro-nepali-calendar/id1006815700
- https://apps.apple.com/us/app/digital-patro-nepali-calendar/id6747698614
- https://www.simplepatro.com/

### 8.3 Accuracy-led or astrology-scale competitors

| Competitor | Core strength | Threat to Parva |
|---|---|---|
| Drik Panchang | explicit accuracy branding, precise calculations, 100,000+ city support | users already associate it with serious calendrical computation |
| AstroSage | massive astrology scale, 70M+ app downloads, heavy product breadth | extremely hard to outcompete on kundali or astrology alone |

Sources:

- https://www.drikpanchang.com/
- https://www.astrosage.com/about-us.asp
- https://www.astrosage.com/mobileapps/astrosage-kundli-best-astrology-app-by-astrosage.asp

### 8.4 What the market is actually telling us

The market does not need another generic Nepali calendar app.

The market already has:

- bundled utility incumbents
- lightweight calendar alternatives
- giant astrology players
- many app-store clones

The white space is narrower:

- verifiable Nepal festival and date API infrastructure
- source-linked, explainable festival date resolution
- embeddable widgets for media, schools, municipalities, diaspora groups, and organizations
- open-source trust with commercial hosting convenience

### 8.5 Best realistic wedge

The best wedge is not:

- the biggest Nepali app
- the best astrology app
- the free everything app

The best wedge is:

- the most transparent Nepal temporal authority layer for developers, institutions, and serious users

That is where Parva can be truly differentiated.

## 9. Feasibility assessment

### Feasible on zero budget

- open-source credibility
- static documentation and SEO pages
- public read-only API with strict rate limits
- institutional pilots with schools, media, and diaspora organizations
- GitHub-based distribution and community feedback
- annual artifact publication and source archives
- a narrow hosted MVP if infrastructure is kept very lean

### Not realistically feasible on zero budget in the short term

- broad always-on consumer super-app scale
- enterprise-grade uptime with no infra cost at all
- top-in-class astrology breadth versus AstroSage
- 0 issues
- immediate global-best accuracy across all dispute cases

### Production hosting reality

For true zero-dollar hosting:

- free Render is not a real production answer
- a more plausible backend host is Oracle Cloud Free Tier or Always Free compute, with important caveats around sign-up friction, capacity, region availability, and operational burden
- the frontend can live on a static host such as GitHub Pages or Cloudflare Pages

Sources:

- https://render.com/docs/free
- https://www.oracle.com/cloud/free/
- https://docs.oracle.com/iaas/Content/FreeTier/freetier.htm
- https://docs.oracle.com/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

## 10. Production-readiness gap list

This is the short list of blockers that matter most.

### P0 blockers

1. Accuracy messaging is ahead of raw evidence.
2. The zero-budget production deployment guidance is internally inconsistent.
3. The main festival detail route is not aligned to the backend data contract.
4. Old SDK code points to dead or legacy endpoints.

### P1 blockers

5. Artifact-based accuracy reporting is inconsistent.
6. Content catalog lacks source citations and depth.
7. Regional and variant coverage is thin.
8. Frontend route tests are failing locally.
9. CI quality gates do not fully cover SDK and most typing surface.
10. Broad exception swallowing hides correctness failures.

### P2 concerns

11. Version sprawl increases maintenance burden.
12. Benchmark messaging can be over-read.
13. API duplication should be reduced.
14. Package import side effects are fragile.
15. In-memory rate limiting is fine for one node, weak for scale.

## 11. Detailed implementation plan to fix the codebase

The goal here is not fantasy perfection.
The goal is a launchable system with no known severe defects, strong evidence, honest claims, and a real path to revenue.

### Phase 0: Stop making any claim the repo cannot defend

Time: 2-4 days

Tasks:

- change product copy from "most accurate" to "most transparent and evidence-backed public beta"
- expose three labels everywhere: `official`, `override`, `computed`
- add a public "known accuracy limits" panel to festival explain and detail pages
- remove or rewrite any benchmark copy that implies authoritative correctness from shape or consistency tests
- rewrite the deployment docs so they no longer imply Render free is production-ready

Acceptance criteria:

- no public-facing text overstates the current evidence
- deployment docs match platform reality

### Phase 1: Repair contract drift and remove stale paths

Time: 1-2 weeks

Tasks:

- replace `FestivalDetailPage` with the canonical `FestivalDetail` contract or align the page fully to backend models
- standardize on `calendar_type`, `regional_focus`, and `connected_deities` for UI display
- remove or deprecate the old Python SDK package `sdk/python/parva`
- update README and packaging to bless a single SDK path
- fix `useCalendar` fallback confidence semantics
- either delete duplicate endpoints or formally document one as compatibility-only

Acceptance criteria:

- festival detail page renders correct real payloads
- SDK package story is singular and tested
- no contradictory confidence or error-window messaging remains

### Phase 2: Make accuracy work artifact-driven, not vibe-driven

Time: 3-6 weeks

Tasks:

- define one canonical accuracy report artifact and deprecate conflicting ones
- add a single reproducible script that produces the launch scorecard
- attach source URLs and provenance metadata to every override row
- create an override debt dashboard:
  - festival
  - year
  - source
  - why override exists
  - whether raw engine now matches
- target a launch corpus of the most commercially important festivals first:
  - Dashain
  - Tihar
  - Teej
  - Shivaratri
  - Janai Purnima
  - Buddha Jayanti
  - Lhosar variants
  - major Newari festivals

Acceptance criteria:

- one canonical scorecard exists
- every override is source-tagged
- launch corpus raw accuracy is materially improved and published

### Phase 3: Improve data quality and sourceability

Time: 3-8 weeks

Tasks:

- require `sources` for every `complete` and `basic` festival record
- add content source schema:
  - title
  - source type
  - URL or archive path
  - access date
  - confidence
- expand structured fields before writing more prose:
  - connected deities
  - locations
  - ritual sequence
  - region focus
- promote only source-backed entries from `minimal` to `basic` or `complete`

Acceptance criteria:

- every non-minimal festival has sources
- content status actually reflects evidence depth

### Phase 4: Tighten quality gates

Time: 1-2 weeks

Tasks:

- expand `mypy` coverage step-by-step beyond the current narrow subset
- include `sdk` in CI linting
- make frontend route tests deterministic
- add a smoke test that renders the real festival detail route with actual backend-shaped payloads
- add regression tests for:
  - `calendar_type`
  - `regional_focus`
  - `connected_deities`
  - override labeling
  - source publication requirement in production

Acceptance criteria:

- CI covers the parts of the code users actually touch
- route-level frontend tests are green and non-flaky

### Phase 5: Production hardening

Time: 2-4 weeks

Tasks:

- update `render.yaml` or replace it with an actually launchable blueprint
- document the true recommended backend host for zero budget
- add scheduled GitHub Actions:
  - daily health-check
  - daily accuracy artifact generation
  - weekly dependency audit
- add backup and export routine for generated artifacts and source archives
- formalize incident playbooks:
  - wrong festival date
  - source URL missing
  - ephemeris degraded
  - cache or precompute missing

Acceptance criteria:

- a documented operator can deploy and verify the service without guesswork
- launch build starts cleanly in production mode

### Phase 6: Narrow to a commercially credible wedge

Time: 2-6 weeks

Tasks:

- position Parva first as:
  - Nepal calendar and festival API
  - embeddable explainable date authority
  - institutional calendar toolkit
- keep kundali and muhurta as secondary modules, not the main go-to-market story
- publish embeddable widgets:
  - today in BS and AD
  - festival countdown
  - ICS export
  - why-this-date explainer
- build institutional landing pages for:
  - schools
  - newsrooms
  - municipalities
  - diaspora organizations

Acceptance criteria:

- homepage and docs explain one sharp value proposition
- product no longer feels like five startups in one repo

## 12. Commercialization plan with most features free

### Core principle

Do not charge for the truth itself.
Charge for convenience, hosting, integration, workflow, and reliability.

### Free forever layer

- BS and AD conversion
- public calendar today endpoint
- public panchanga for daily use
- core festival explorer
- source code access
- source-linked explain pages
- ICS feeds
- rate-limited public API

### Paid layer

- hosted SLA-backed API keys
- higher rate limits
- white-label widgets
- custom branded embeds for media and institutions
- annual verified holiday and festival export packs
- organization admin dashboard
- change alerts when an official date or override shifts
- priority support and integration help

### Best zero-budget customer segments

Start with customers who care about correctness and distribution, not novelty:

- Nepali media publishers
- schools and colleges
- municipalities and local governments
- temples and cultural organizations
- diaspora associations
- travel or culture publishers
- fintech, payroll, or HR products needing Nepali date support

### Worst first customer segments

- generic consumer astrology audience
- everyone in Nepal at once
- ad-supported mass entertainment audience

### Why this can still make money while keeping most features free

Because the commercial product is not just calendar pages.
The commercial product is:

- trusted hosted infrastructure
- integration labor avoided
- compliance and traceability comfort
- branded delivery
- reliability and support

## 13. Go-to-market plan at zero budget

### Growth loops that cost time, not cash

1. SEO pages for every major festival and date question.
2. Public explainers for "why is this date different this year?"
3. Free embeddable widgets with attribution.
4. GitHub credibility plus public evidence artifacts.
5. Outreach to Nepali publishers and institutions with a free pilot.
6. Annual source-backed holiday release pack shared publicly.

### Content strategy that actually matches Parva's strengths

Publish pages like:

- Dashain 2026 date in Nepal
- Why Teej date changed this year
- BS 2083 to AD converter
- Panchanga today in Kathmandu
- Nepal holiday API
- Nepali festival ICS calendar

This is far more aligned with Parva's real moat than trying to outdo Hamro Patro's utility bundle.

## 14. What I would do first if this were my project

If I had to maximize odds of success under the current constraints, I would do this in order:

1. Fix the festival detail route contract and delete stale UI paths.
2. Remove the old SDK package and bless one supported client.
3. Rewrite all public claims to match the real evidence.
4. Build one canonical accuracy report with override and source debt tracking.
5. Focus the next 60 days on 15-20 flagship festivals only.
6. Launch Parva as a trust-first Nepal temporal API and widget platform, not a broad astrology app.
7. Pilot it with one newsroom, one school, and one diaspora organization before trying to go viral.

## 15. Final judgment

Project Parva is worth taking seriously.

It is not yet the finished authority product it wants to be, but it is much closer to a real company-worthy foundation than most ambitious side projects ever get.

The path forward is not more breadth.
The path forward is:

- less hype
- more evidence
- fewer surfaces
- stronger flagship accuracy
- clearer commercial wedge

If you do that, the project can become genuinely valuable.

If you keep trying to be:

- the most accurate
- the most complete
- the broadest app
- the best astrology product
- and all of it on zero budget immediately

then the scope itself will kill the product before competitors do.

## 16. Source links used for market research

- https://datareportal.com/reports/digital-2026-nepal
- https://www.imf.org/en/News/Articles/2025/03/14/pr25063-nepal-imf-completes-the-fifth-review-under-the-extended-credit-facility-arrangement
- https://www.imf.org/-/media/Files/Publications/CR/2025/English/1nplea2025002-source-pdf.ashx
- https://render.com/docs/free
- https://www.oracle.com/cloud/free/
- https://docs.oracle.com/iaas/Content/FreeTier/freetier.htm
- https://docs.oracle.com/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://apps.apple.com/us/app/hamro-patro-nepali-calendar/id401074157
- https://english.hamropatro.com/news/details/8487492033134839
- https://apps.apple.com/us/app/nepali-patro/id664588996
- https://apps.apple.com/us/app/mero-patro-nepali-calendar/id1006815700
- https://apps.apple.com/us/app/digital-patro-nepali-calendar/id6747698614
- https://www.simplepatro.com/
- https://www.drikpanchang.com/
- https://www.astrosage.com/about-us.asp
- https://www.astrosage.com/mobileapps/astrosage-kundli-best-astrology-app-by-astrosage.asp
