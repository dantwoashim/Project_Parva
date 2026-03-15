# Project Parva Deep Audit, Honest Review, and Production Plan

Date: 2026-03-14  
Repository root: `D:\Project_Parva-main\Project_Parva-main`

## Executive Summary

Project Parva is a serious and unusually thoughtful Nepal-focused temporal computation platform. The core idea is strong: combine Bikram Sambat conversion, panchanga, festival intelligence, explainability, location-aware temporal calculations, and an API-first architecture into a trust-oriented product instead of just another ad-heavy calendar app.

My bottom-line assessment is:

- The idea is viable.
- The codebase is stronger than most early-stage hobby projects.
- The project is not yet production-ready.
- It is not credible today to claim "most accurate on the planet" or "0 issues."
- It does have a realistic path to become a respected, commercially useful Nepal temporal infrastructure product if it chooses the right wedge.

The single most important truth is this: the project already looks like a real product internally, but several flagship flows are still broken in a real browser, and some of the strongest accuracy/authority claims are not yet fully supported by the current evidence pipeline.

## What I Reviewed

This was a deep audit of the current checkout, but not a literal human line-by-line code review of every single source line. That would take days or weeks. Instead, I combined:

- Whole-tree inventory and module mapping.
- Direct reading of the critical backend, frontend, engine, routing, report, and SDK files.
- Real command execution across tests, lint, build, type checking, conformance, and release scripts.
- Real-browser verification using Playwright against a running local app.
- External research on market size, competitors, and monetization realities.

### Local evidence gathered

- Backend source counted: `158` Python files under `backend/app`
- Frontend source counted: `53` JS/JSX/TS/TSX files under `frontend/src`
- Automated tests counted: `73` source test files across backend and frontend
- Scripts counted: `35` Python files under `scripts`
- SDK source counted: `6` Python files under `sdk/python`

### Validation commands run

- `py -3.11 -m pytest -q` -> `329 passed`
- `npm --prefix frontend run lint` -> passed
- `npm --prefix frontend test -- --run` -> passed
- `npm --prefix frontend run build` -> passed
- `py -3.11 -m mypy` -> passed for configured targets
- `py -3.11 -m ruff check backend tests scripts` -> failed with 3 minor issues
- `py -3.11 scripts/check_path_leaks.py` -> passed
- `py -3.11 scripts/validate_festival_catalog.py` -> passed
- `py -3.11 scripts/release/check_license_compliance.py` -> passed
- `py -3.11 scripts/release/check_contract_freeze.py` -> passed
- `py -3.11 scripts/spec/run_conformance_tests.py` -> passed, `6/6`
- Playwright real-browser review against a locally served build
- Direct API reproduction of frontend failures with `requests.post`
- Direct dependency audit with `pip_audit`

### Important limitation

This checkout does not include `.git` metadata, so I could not do historical ownership, change-frequency, or bus-factor analysis from commit history.

## What The Product Actually Is

Project Parva is best understood as four products in one:

1. A Nepal temporal engine.
2. A user-facing reference application.
3. A provenance and explainability layer over date/festival calculations.
4. A potential API/platform business.

That is powerful, but it also means the project is currently trying to win on:

- correctness
- UX
- doctrinal trust
- developer ergonomics
- content completeness
- operational reliability
- commercialization

That is ambitious for a zero-budget project. The ambition is a strength, but it also creates risk if the launch story overclaims before the evidence and product polish catch up.

## Architecture Assessment

## Strengths

- Clean backend bootstrapping: app factory, route registry, middleware layering, settings loading, and versioned API posture are all signs of mature thinking.
- Good request hygiene: request IDs, request-size guards, rate limiting, API key parsing, version gating, and explicit headers are present in the backend middleware.
- Clear product documentation: the repo already contains unusually strong internal documentation such as `PROJECT_BIBLE`, `AS_BUILT`, `KNOWN_LIMITS`, `ENGINE_ARCHITECTURE`, `ACCURACY_METHOD`, and `DEPLOYMENT`.
- Domain specificity: this is not generic CRUD software. It has a real moat if accuracy, explainability, and regional trust are executed well.
- Good release discipline in several places: contract freeze, conformance checks, license compliance, catalog validation, and path-leak checks are all signs of a team thinking about shipping responsibly.

## Weaknesses

- The codebase has several oversized modules that will slow safe iteration.
- There is a mismatch between green tests and real-user behavior.
- The evidence chain for some public claims is incomplete or fragile.
- The frontend and backend contract is not enforced tightly enough.
- The root workspace contains unrelated project residue that undermines trust in repo hygiene.

## Module Map

### Backend

The backend is the strongest part of the codebase overall.

Key areas:

- `backend/app/bootstrap`: app setup, middleware, settings, access control.
- `backend/app/calendar`: core calendar logic, BS/AD handling, kundali, muhurta, ephemeris integration.
- `backend/app/festivals`: festival endpoints, repository, indexing.
- `backend/app/rules`: rule catalogs and execution logic.
- `backend/app/engine`: plugin registry, validation, engine wiring.
- `backend/app/api`: user-facing route surfaces for personal panchanga, temporal compass, muhurta, kundali, and related features.

Largest backend hotspots by line count:

- `backend/app/calendar/routes.py` -> 833 lines
- `backend/app/rules/catalog_v4.py` -> 645 lines
- `backend/app/calendar/muhurta.py` -> 624 lines
- `backend/app/calendar/bikram_sambat.py` -> 585 lines
- `backend/app/festivals/routes.py` -> 573 lines
- `backend/app/calendar/calculator.py` -> 545 lines

Interpretation:

- The architecture direction is good.
- The concentration of logic into very large files increases fragility, review cost, and regression risk.

### Frontend

The frontend is usable and conceptually well structured, but it is less reliable than the backend.

Key areas:

- `frontend/src/pages`: route-level experiences.
- `frontend/src/services/api.js`: API client layer.
- `frontend/src/context`: temporal state and defaults.
- `frontend/src/hooks`: data-fetching hooks.
- `frontend/src/components`: rendering and shared UI blocks.

Largest frontend hotspots by line count:

- `frontend/src/pages/FestivalDetailPage.jsx` -> 322 lines
- `frontend/src/components/Festival/FestivalDetail.jsx` -> 301 lines
- `frontend/src/services/api.js` -> 246 lines
- `frontend/src/pages/TemporalCompassPage.jsx` -> 242 lines
- `frontend/src/pages/KundaliPage.jsx` -> 208 lines
- `frontend/src/pages/MuhurtaPage.jsx` -> 192 lines

Interpretation:

- The frontend is feature-rich and coherent.
- Contract handling and integration realism are not yet strong enough.

### SDK

The Python SDK is a positive signal, but commercially it is still incomplete.

Current state:

- Good for basic client access patterns.
- Not enough coverage for the most commercially interesting POST-first endpoints such as personal panchanga, muhurta heatmap, and kundali workflows.

### Packaging and workspace hygiene

There is a major repo-hygiene issue at the root:

- `package.json` is named `viral-sync-workspace`
- it references workspaces like `app`, `relayer`, and `server/actions`
- `packages/shared/src/index.ts` exports unrelated Solana/relayer constants such as `LAMPORTS_PER_SOL`

This appears to be stale or foreign project residue, not part of Project Parva's actual architecture. It is one of the most visible trust-damaging problems in the repository.

## Feasibility Assessment

## What is feasible on a zero-dollar budget

- A technically credible public beta.
- A trust-first public reference app for Nepal calendar and festival intelligence.
- A narrow but real B2B/B2B2C product: embeddable widgets, API access, institutional feeds, or white-label calendar services.
- A diaspora and institutional adoption wedge built on clarity, speed, and transparency.
- A strong open-source trust position if the deployed source is easy to access and the release evidence is reproducible.

## What is not realistically feasible on a zero-dollar budget right now

- Beating Hamro Patro as a mass-market Nepali super-app.
- Guaranteeing zero issues.
- Guaranteeing commercial success.
- Truthfully claiming world-best accuracy today without a much stronger benchmark corpus and authority-validation program.
- Running high-traffic, low-latency, production-grade infrastructure on a free hosting tier indefinitely.

## Real Browser Findings

This is the most important operational section of the audit.

I served the built frontend locally from the FastAPI app and tested the real UI in a browser.

Observed results:

- `/festivals` worked
- `/kundali` worked
- `/` Temporal Compass failed with `422`
- `/personal` failed with `422`
- `/muhurta` failed with `422`

Root cause:

- The frontend sends numeric `lat` and `lon` from app state.
- Three backend POST schemas require `Optional[str]`.

Concrete evidence:

- `frontend/src/pages/TemporalCompassPage.jsx` sends `state.location?.latitude` and `state.location?.longitude`
- `frontend/src/pages/PersonalPanchangaPage.jsx` does the same
- `frontend/src/pages/MuhurtaPage.jsx` does the same
- `backend/app/api/temporal_compass_routes.py` defines `lat: Optional[str]` and `lon: Optional[str]`
- `backend/app/api/personal_routes.py` defines `lat: Optional[str]` and `lon: Optional[str]`
- `backend/app/api/muhurta_heatmap_routes.py` defines `lat: Optional[str]` and `lon: Optional[str]`
- `frontend/src/pages/KundaliPage.jsx` works because it converts coordinates to string state first

This is a release blocker because it breaks multiple flagship product flows in normal use even though the test suite is green.

## Test and Release Reliability Assessment

## What is good

- The repo has a broad automated test base.
- The backend test suite is sizable and fast enough to be used regularly.
- Frontend lint, unit tests, and build succeed.
- Several release-hardening scripts already exist.

## What is weak

- The tests do not protect against the most important real integration break I found.
- The frontend API tests use string coordinates like `'27.7172'` and `'85.3240'`, which masks the real state shape used by the app.
- There is no strong end-to-end browser regression suite protecting critical user journeys.
- Some report generators succeed structurally while still producing null or missing-quality fields.

## Release artifact integrity

This project has an evidence-pipeline problem, not just a code problem.

### Accuracy report generator failure

`scripts/generate_accuracy_report.py` opens `ground_truth_overrides.json` without `encoding="utf-8"`.

On this Windows environment it failed with a `UnicodeDecodeError`.

Why this matters:

- If the accuracy report cannot be generated reliably across environments, release evidence is fragile.
- Accuracy claims become harder to defend.

### Authority dashboard gaps

`scripts/generate_authority_dashboard.py` produced `reports/authority_dashboard.json` (generated artifact), but key fields were null:

- `rule_catalog_total`
- `rule_catalog_generated`
- `rule_catalog_coverage_pct`

It also referenced missing artifact paths such as:

- `reports/evaluation_v4/evaluation_v4.json` (generated artifact)
- `reports/rule_ingestion_summary.json` (generated artifact)

### Month 9 dossier gaps

`scripts/release/generate_month9_dossier.py` produced a dossier with incomplete quality gates:

- accuracy fields were null
- authority dashboard catalog fields were null

It also parses `docs/KNOWN_LIMITS.md` by looking only for dash-prefixed bullets, while that file currently uses numbered items. That means the generator effectively misses the authored known-limits list.

## Accuracy and Authority Claim Assessment

This is where I need to be extremely honest.

The project clearly cares about authority, provenance, and explainability. That is a real strength. But the current repo state does not justify maximal marketing claims yet.

Why:

- Some release evidence is missing or null.
- The generated accuracy pipeline is not robust across environments.
- Plugin validation evidence is too thin to support "best on the planet" positioning.
- The codebase itself still has user-visible contract failures in core flows.

My assessment:

- "More transparent than most competitors" -> credible direction.
- "Explainable and provenance-aware" -> credible direction.
- "Potentially more trustworthy than ad-heavy incumbents" -> credible direction.
- "Most accurate on the planet" -> not currently proven.
- "0 issues" -> impossible claim.

## Honest Quality Review

If I had to score the project as it exists today:

| Area | Score | Notes |
|---|---:|---|
| Product idea | 8.5/10 | Strong niche, real need, meaningful differentiation |
| Architecture direction | 8/10 | Good backend structure and release posture |
| Code quality overall | 6.5/10 | Better than average, but real integration gaps remain |
| Documentation | 9/10 | One of the strongest parts of the repo |
| Frontend reliability | 5/10 | Feature-rich but not yet trustworthy enough |
| Release-readiness | 4.5/10 | Good scaffolding, but blockers remain |
| Evidence for accuracy claims | 4/10 | Intent is strong; proof is incomplete |
| Commercial potential | 6/10 | Good niche potential; weak mass-market odds |

### The brutally honest version

This is not junk. It is not fake architecture. It is not "just a portfolio project."

It is a real attempt at building temporal infrastructure with seriousness.

But it is also not ready to be marketed as a finished authority product. Right now it is best described as:

- a strong alpha or early beta foundation
- with above-average engineering discipline
- and below-required launch reliability for its most sensitive claims

## Problem Register

The table below is the practical heart of the audit.

| Severity | Problem | Why it matters | Evidence | Required fix |
|---|---|---|---|---|
| P0 | Frontend/backend coordinate type mismatch breaks core flows | Users hit 422s on flagship pages | Temporal Compass, Personal Panchanga, Muhurta browser failures | Normalize coordinates on both sides, add contract tests and E2E smoke tests |
| P1 | Accuracy report generation breaks on Windows | Release evidence becomes non-reproducible | `scripts/generate_accuracy_report.py` missing explicit UTF-8 open | Use explicit encoding and cross-platform CI |
| P1 | Release dashboards contain null authority/accuracy fields | Claims are harder to defend | Generated dossier/dashboard artifacts have null metrics | Make artifact generation complete and fail hard on missing upstream data |
| P1 | Repo root contains unrelated workspace residue | Damages trust and onboarding clarity | `viral-sync-workspace`, relayer files, Solana constants | Remove or isolate unrelated files from this repo |
| P1 | Tests miss real integration failures | Green CI gives false confidence | Frontend tests use string coords; app sends numbers | Add browser E2E tests and schema contract tests |
| P1 | Public strongest claims exceed current proof | Launch risk, credibility risk | Missing/null metrics and thin validation corpus | Reduce claims until evidence is stronger |
| P2 | Date default uses UTC `toISOString()` slicing | Can drift around timezone boundaries | `frontend/src/context/temporalContextState.js` | Generate local or Nepal-time date explicitly |
| P2 | Large monolithic files | Slows safe iteration | Multiple 500-800+ line modules | Split by domain responsibility |
| P2 | Broad exception swallowing in critical paths | Can hide correctness bugs | Present in several backend/report areas | Replace with typed errors and observable failure paths |
| P2 | SDK incomplete for key POST workflows | Limits platform/commercial story | Python SDK mostly covers simpler client patterns | Add first-class typed methods for personal, muhurta, kundali |
| P2 | Python environment shows known package vulnerabilities | Hygiene and deployment concern | `pip_audit` found 14 vulnerabilities in environment packages | Pin and upgrade the actual deploy environment |
| P3 | Ruff violations remain | Minor but easy debt | 3 lint issues | Fix immediately |

## Market Reality

## Demand signal

The market is real.

The latest broadly available Nepal digital snapshot I found was the 2026 DataReportal report for Nepal, which reports about `16.6 million` internet users and internet penetration around `55.9%`. That is a meaningful addressable digital audience for calendar, ritual, festival, diaspora, and institutional date intelligence products.

This does not mean a new app automatically wins. It means the category is not imaginary.

## Competitor landscape

### 1. Hamro Patro

What it is:

- The dominant Nepal consumer category player.
- Multi-surface product: calendar, news, radio, horoscope, and broader daily-use utility.

What this means for Parva:

- You should not try to out-super-app Hamro Patro on zero budget.
- You can still beat it on trust, clarity, speed, explainability, and institutional usefulness.

### 2. Drik Panchang

What it is:

- A strong panchang and festival authority-style brand with broad Hindu calendar utility.

What this means for Parva:

- This is a trust and correctness competitor more than a "consumer super-app" competitor.
- Parva needs better proof, not just better UI, to compete here.

### 3. AstroSage

What it is:

- A very large astrology and kundli player with massive consumer reach.

What this means for Parva:

- If Parva leans too hard into generic astrology consumer monetization, it enters a brutally crowded battlefield.
- Parva's advantage is not being "another astrology app." It is being explainable Nepal temporal infrastructure.

### 4. MyPanchang

What it is:

- A long-running panchang and astrology utility brand.

What this means for Parva:

- Confirms continuing demand for panchang/muhurat/kundli products.

### 5. API competitors: Prokerala API and AstrologyAPI

What they show:

- There is already a commercial API market for astrology and panchang data.
- Infrastructure and developer-facing monetization are viable business models in this space.

What this means for Parva:

- The strongest commercial wedge for Parva is probably API + embeds + institutional feeds, not ad-funded consumer scale.

## Strategic conclusion

The right battle is:

- "clean, explainable, Nepal-specific temporal infrastructure"

Not:

- "the next Hamro Patro"

## Best Positioning For Commercial Success

Because the budget is `0$`, the only viable path is a trust moat plus narrow focus.

## Recommended positioning

"Project Parva is the explainable Nepal calendar and festival engine for users, institutions, and developers who need answers they can inspect."

That positioning is better than:

- generic astrology app
- ad-heavy consumer utility
- overclaimed religious authority

## Who to target first

Priority order:

1. Developers and product teams needing Nepal calendar/festival APIs.
2. Media, schools, municipalities, temples, and community sites needing accurate public festival/date widgets.
3. Diaspora users who value clarity and trust over feature bloat.
4. Specialist users who care about personal panchanga and muhurta.

## Free vs paid strategy

Keep free:

- BS/AD conversion
- public festival explorer
- daily panchanga
- basic temporal explanations
- public ICS/feed exports
- basic API tier with strict quotas

Charge for:

- higher API quotas and SLA
- white-label widgets
- institution-branded embeds
- custom regional or doctrinal profiles
- bulk export/reporting
- managed hosting/support
- commercial support for AGPL compliance and source availability

## Important pricing truth

Consumer willingness to pay in this category is usually low, especially when big incumbents are ad-supported or low-cost. The stronger money path is utility pricing for organizations and developers, not trying to force a mass subscription business from ordinary users.

## Zero-Budget Launch Reality

There is a hard contradiction in the user's requested constraints:

- zero budget
- production ready
- highest reliability
- zero issues

Those cannot all be maximized at once.

Official Render documentation for free web services explicitly says those free services are not intended for production use. So a no-budget launch can be a public beta, a low-volume pilot, or a community deployment, but not a truly no-compromise production posture.

The honest zero-budget target should be:

- stable public beta
- low-volume institutional pilots
- aggressive observability
- careful scope control

## Detailed Implementation Plan

## Phase 0: Immediate blockers and truth alignment

Target: 2 to 5 days

Objectives:

- stop core breakages
- stop claim/evidence mismatch
- clean the repo's trust-damaging rough edges

Tasks:

1. Fix the coordinate schema mismatch.
   - Accept numeric and string coordinates in backend request models.
   - Normalize coordinates centrally in the API layer.
   - Update frontend API calls to send consistent typed payloads.

2. Add browser-level smoke tests.
   - Required flows: home/Temporal Compass, Personal Panchanga, Muhurta, Kundali, Festivals.
   - Fail the build if any flagship page returns 4xx/5xx or renders fallback error states.

3. Fix `scripts/generate_accuracy_report.py`.
   - Open JSON with explicit UTF-8.
   - Run in Windows and Linux CI.

4. Fix `scripts/release/generate_month9_dossier.py`.
   - Parse numbered known-limit lists.
   - Fail hard if upstream artifacts are missing instead of silently returning partial truth.

5. Remove or quarantine unrelated root workspace files.
   - Either delete them from this repo or move them into a clearly marked archival folder outside the main product surface.

6. Fix the 3 Ruff issues.

Exit criteria:

- core browser flows all work
- release scripts run cleanly on at least one Windows and one Linux environment
- no unrelated workspace confusion at repo root

## Phase 1: Make claims reproducible

Target: 1 to 2 weeks

Objectives:

- every public claim should map to a reproducible artifact
- no null dashboard metrics

Tasks:

1. Define a single source of truth for:
   - rule coverage
   - source-validated coverage
   - conformance pass rate
   - accuracy report totals

2. Make report generation dependency-ordered.
   - If `authority_dashboard` depends on `rule_ingestion_summary`, generate it first or fail clearly.

3. Add CI gates for artifact completeness.
   - Null quality-gate fields should fail CI.
   - Missing artifact paths should fail CI.

4. Publish a simpler public truth standard.
   - Distinguish `computed`, `source-validated`, `inventory`, and `experimental`.
   - Do not market a computed rule as authority-validated unless the evidence says so.

5. Add a "claims matrix" document.
   - For each public claim, define the exact data source that permits it.

Exit criteria:

- release dossier contains no null quality-gate fields
- every linked artifact exists
- public claims are narrower but defensible

## Phase 2: Reliability hardening

Target: 2 to 4 weeks

Objectives:

- make the app dependable under normal use
- reduce hidden correctness failures

Tasks:

1. Fix date/time correctness at the frontend edge.
   - Replace UTC-based `todayIso()` with a timezone-aware local date strategy.
   - Prefer explicit Nepal-time handling where product intent is Nepal-centric.

2. Introduce typed API contracts.
   - Generate or hand-maintain shared schemas for frontend, backend, and SDK.
   - Contract tests should run against the real app.

3. Reduce broad exception swallowing.
   - Replace generic `except Exception` branches with typed errors.
   - Log structured failure reasons.
   - Fail loudly for correctness-sensitive paths.

4. Add runtime observability.
   - request/error counters
   - route latency
   - artifact freshness
   - last successful benchmark run

5. Harden sensitive input flows.
   - Treat birth data and location data as sensitive.
   - Add clear privacy posture for personal routes.

6. Add golden-data regression suites.
   - sunrise boundary cases
   - timezone edge cases
   - region-specific observance cases
   - historical festival edge cases

Exit criteria:

- no known core UX blockers
- typed contracts across user-critical APIs
- materially better failure visibility

## Phase 3: Codebase maintainability and platform maturity

Target: 3 to 6 weeks

Objectives:

- make future iteration safe and fast
- support commercial use cases cleanly

Tasks:

1. Break up oversized modules.
   - Split route files by feature.
   - Split rule/catalog logic by domain or source family.
   - Separate pure computation from transport/serialization.

2. Expand SDK coverage.
   - Add typed methods for personal panchanga, muhurta, kundali, and temporal compass.
   - Add examples for institutional/API customers.

3. Create formal API product tiers.
   - public
   - developer
   - institution
   - internal/admin

4. Add change logs and migration notes for API versions.

5. Tighten dependency management.
   - pin deploy dependencies
   - upgrade vulnerable environment packages
   - document the supported runtime baseline

Exit criteria:

- smaller modules
- stronger SDK story
- clearer external API product surface

## Phase 4: Commercial readiness

Target: 2 to 6 weeks after technical hardening

Objectives:

- stop being "interesting software"
- become "a useful thing people can adopt"

Tasks:

1. Build three polished monetizable surfaces.
   - public widget embed
   - institution calendar feed
   - developer API quickstart

2. Publish a trust page.
   - methodology
   - known limits
   - source policy
   - release evidence links
   - uptime and incident notes

3. Add low-touch adoption tooling.
   - copy-paste widget embed
   - ICS subscription links
   - one-page API getting-started guide

4. Run 3 to 5 pilot users or institutions.
   - one school/media org
   - one temple/community org
   - one developer/integration partner

5. Collect structured feedback before broad launch.

Exit criteria:

- real external users use the product
- at least one paid or committed pilot path exists

## Phase 5: Accuracy moat

Target: ongoing

Objectives:

- become meaningfully more trusted over time
- earn authority instead of claiming it

Tasks:

1. Build a larger benchmark corpus.
   - region-specific observances
   - doctrinal variants
   - historical exception cases
   - expert-reviewed samples

2. Maintain provenance at the rule level.
   - source
   - version
   - validation status
   - reviewer
   - last checked date

3. Create explicit profile-based outputs.
   - do not pretend one answer fits all traditions

4. Invite external reviewers or volunteer advisors.
   - scholars
   - practitioners
   - domain experts

5. Publish comparisons carefully.
   - be transparent where Parva disagrees with other calendars
   - explain why

Exit criteria:

- accuracy leadership becomes evidence-backed instead of aspirational

## Recommended Launch Sequence

Do not go straight to "national launch."

Recommended sequence:

1. Internal hardening.
2. Public beta with narrow claims.
3. Pilot institutions and developers.
4. Trust page and evidence page.
5. Soft commercial rollout.
6. Wider user growth only after reliability is proven.

## What To Say Publicly Right Now

Safe claims:

- Nepal-focused calendar and festival engine
- explainable outputs
- provenance-aware architecture
- public beta / early access
- transparent about known limits

Unsafe claims right now:

- zero issues
- world-best accuracy
- definitive religious authority
- production-grade at any scale with no caveats

## Final Verdict

Project Parva has real potential.

Its strengths are not superficial:

- the idea is differentiated
- the backend architecture is strong
- the docs are excellent
- the project clearly aims for truth and rigor

Its problems are also real:

- core flows are broken in a live browser
- the release-evidence chain is incomplete
- repo hygiene is damaged by unrelated leftover workspace files
- the strongest marketing claims currently run ahead of the proof

If the team narrows focus, fixes the blocker class of issues first, and chooses a trust-first infrastructure wedge instead of trying to become a zero-budget consumer super-app, this project can become genuinely important and commercially useful.

If the team keeps the current ambition level but tries to launch with overclaims, it risks becoming "impressive but not trusted."

The best path is:

- fewer claims
- more proof
- tighter product scope
- stronger integration tests
- cleaner repository
- deliberate commercialization around APIs, embeds, and institutions

That path will not guarantee "sure success," but it is the highest-probability path to building something durable, respected, and capable of making real money while keeping core public value free.

## External Sources Used

- [DataReportal: Digital 2026 Nepal](https://datareportal.com/reports/digital-2026-nepal)
- [Hamro Patro official site](https://www.hamropatro.com/)
- [Hamro Patro Google Play listing](https://play.google.com/store/apps/details?id=com.hamropatro&hl=en_US&gl=US)
- [Drik Panchang official site](https://www.drikpanchang.com/)
- [AstroSage official site](https://www.astrosage.com/)
- [AstroSage Google Play listing](https://play.google.com/store/apps/details?id=com.ojassoft.astrosage&hl=en_US&gl=US)
- [MyPanchang official site](https://www.mypanchang.com/)
- [Prokerala API](https://api.prokerala.com/)
- [AstrologyAPI](https://www.astrologyapi.com/)
- [Render docs: Free web services](https://render.com/docs/free#free-web-services)

## Most Important Local Files Reviewed

- `README.md`
- `docs/PROJECT_BIBLE.md`
- `docs/AS_BUILT.md`
- `docs/KNOWN_LIMITS.md`
- `docs/ENGINE_ARCHITECTURE.md`
- `docs/ACCURACY_METHOD.md`
- `docs/DEPLOYMENT.md`
- `backend/app/main.py`
- `backend/app/bootstrap/app_factory.py`
- `backend/app/bootstrap/router_registry.py`
- `backend/app/bootstrap/middleware.py`
- `backend/app/bootstrap/settings.py`
- `backend/app/festivals/routes.py`
- `backend/app/festivals/repository.py`
- `backend/app/calendar/routes.py`
- `backend/app/engine/core_engine.py`
- `backend/app/engine/plugins/registry.py`
- `backend/app/engine/plugins/validation.py`
- `backend/app/rules/catalog_v4.py`
- `backend/app/rules/execution.py`
- `backend/app/api/temporal_compass_routes.py`
- `backend/app/api/personal_routes.py`
- `backend/app/api/muhurta_heatmap_routes.py`
- `backend/app/api/kundali_routes.py`
- `frontend/src/App.jsx`
- `frontend/src/services/api.js`
- `frontend/src/context/TemporalContext.jsx`
- `frontend/src/context/temporalContextState.js`
- `frontend/src/pages/TemporalCompassPage.jsx`
- `frontend/src/pages/FestivalExplorerPage.jsx`
- `frontend/src/pages/FestivalDetailPage.jsx`
- `frontend/src/pages/PersonalPanchangaPage.jsx`
- `frontend/src/pages/MuhurtaPage.jsx`
- `frontend/src/pages/KundaliPage.jsx`
- `sdk/python/parva_sdk/client.py`
- `scripts/generate_accuracy_report.py`
- `scripts/generate_authority_dashboard.py`
- `scripts/release/generate_month9_dossier.py`
