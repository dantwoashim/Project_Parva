# Project Parva Evaluator Prep Guide

This document is a full low-technical guide to help you present Project Parva confidently to an evaluator.

It is based on direct inspection of the repository, the running API, the frontend, the backend, the tests, the deployment files, and the project documentation.

Read this as your main study document for the next 4 days.

## 1. What Project Parva Is

Project Parva is a Nepal-focused calendar and festival intelligence platform.

At its core, it does five important things:

1. Converts dates between Gregorian AD and Bikram Sambat BS.
2. Calculates tithi and panchanga using astronomical logic.
3. Resolves festival dates using calendar rules plus official overrides when available.
4. Exposes all of this through a public API.
5. Wraps the API in a user-facing React frontend and embeddable widgets.

In simple words:

- The backend is the calculation brain.
- The frontend is the presentation layer.
- The data folder is the knowledge base.
- The tests and scripts are the quality-control system.

## 2. The One-Sentence Pitch

Project Parva is an explainable Nepal temporal engine that combines calendar conversion, panchanga, festival calculation, personal ritual timing, and developer-friendly APIs into one platform.

## 3. The 30-Second Explanation for an Evaluator

Project Parva is a full-stack calendar platform focused on Nepal. It calculates Bikram Sambat dates, tithi, panchanga, festival dates, muhurta, and kundali-related outputs using Python and Swiss Ephemeris on the backend, then delivers that through a React frontend, embeddable widgets, and a structured API under `/v3/api/*`. It also includes provenance, explainability, testing, and deployment tooling so the system is not just functional, but auditable and presentable.

## 4. The 2-Minute Explanation for an Evaluator

The project solves a real problem: Nepali calendar logic is not simple. BS conversion is not a fixed mathematical offset, tithi depends on astronomical boundaries, festivals depend on lunar rules and regional traditions, and personal timing features depend on place and timezone.

So the project is split into layers:

1. A Python backend computes the actual calendar logic.
2. A rule system resolves festival dates using both algorithmic rules and official overrides.
3. A FastAPI API exposes the stable public contract under `/v3/api/*`.
4. A React frontend turns the raw outputs into a consumer experience.
5. A set of scripts, tests, and release gates make sure the project stays accurate and explainable.

What makes the project strong is that it is not only a frontend app and not only an API. It is a full product system with:

- computation,
- content,
- explainability,
- testing,
- deployment,
- embeds,
- and developer onboarding surfaces.

## 5. What Problem It Solves

Project Parva solves several problems at once.

### For end users

- It gives day-based ritual and calendar guidance.
- It shows daily panchanga and festival context.
- It offers personal place-based timing.

### For institutions

- It provides embeddable widgets.
- It supports public-facing informational experiences.
- It offers careful launch posture and source-publication discipline.

### For developers

- It exposes a stable API.
- It includes a Python SDK.
- It provides route metadata, trace IDs, provenance, and integration guides.

## 6. What Is in the Repository

This repository is large. You should not try to memorize every file name.

What you should memorize is the purpose of each major area.

### Top-level file count summary

From the inspected repository:

- Total files: about 2173
- Most files are JSON data files
- Backend app files: 324
- Frontend source files: 148
- Scripts: 56
- Tests: 103
- SDK files: 8

### By major area

#### `backend/app/`

This is the main backend application.

- It contains the FastAPI app, calendar logic, festival logic, services, provenance, and supporting modules.

#### `frontend/src/`

This is the React frontend.

- It contains pages, components, hooks, contexts, services, navigation, and styling.

#### `data/`

This is the project’s knowledge and evidence layer.

- Festival rules
- validation cases
- ground truth
- regional maps
- ingest reports
- official holiday PDFs

This is one of the most important folders in the whole project.

#### `tests/`

This is the automated validation layer.

- Contract tests
- integration tests
- unit tests
- fixtures
- conformance cases

#### `scripts/`

This contains operational and release tooling.

- precompute
- rule ingestion
- release gates
- conformance runs
- report generation
- packaging

#### `sdk/python/`

This is the Python client SDK for external developers.

#### `docs/`

This contains the architecture, API, deployment, limits, and methodology documentation.

#### `frontend/public/`

This contains static public surfaces such as:

- embed widgets
- developer portal
- institution portal
- access portal
- service worker

## 7. High-Level System Architecture

The architecture is explicitly described in [docs/ENGINE_ARCHITECTURE.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/ENGINE_ARCHITECTURE.md).

The runtime layers are:

1. `calendar/*`
2. `rules/*`
3. `api/*`
4. `bootstrap/*`
5. `provenance/*` and `explainability/*`

### Plain-language version

1. Calendar layer
   This is where date conversion and astronomical calculations happen.

2. Rules layer
   This is where the project decides how to compute festival dates.

3. API layer
   This is where the project exposes results to apps and developers.

4. Bootstrap layer
   This is where the application starts, loads settings, applies middleware, and registers routes.

5. Provenance and explainability layer
   This is where the project records traceability and verification data.

## 8. Backend Architecture in Simple Terms

The backend is a FastAPI application built through an application factory.

### Main backend entry

- [backend/app/main.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/main.py)

This is intentionally small. It simply imports `create_app()` from bootstrap and creates the FastAPI app instance.

### App startup and assembly

- [backend/app/bootstrap/app_factory.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/bootstrap/app_factory.py)

This is one of the most important files in the project.

It does these jobs:

- loads environment settings,
- validates startup requirements,
- applies middleware,
- registers routers,
- exposes health checks,
- optionally serves the built frontend,
- exposes `/docs`, `/openapi.json`, `/source`, and health routes.

### Settings and environment validation

- [backend/app/bootstrap/settings.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/bootstrap/settings.py)

This file defines:

- environment handling,
- frontend serving settings,
- rate limiting settings,
- admin token behavior,
- API key behavior,
- production safety checks,
- AGPL source publication requirements.

This is why the project behaves like a real deployable product, not just a local prototype.

### Route registration

- [backend/app/bootstrap/router_registry.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/bootstrap/router_registry.py)

This file registers:

- `/api/*`
- `/v3/api/*`

and optionally:

- `/v2/*`
- `/v4/*`
- `/v5/*`

That means the public stable profile is version 3, while other versions are experimental.

### Middleware

- [backend/app/bootstrap/middleware.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/bootstrap/middleware.py)

This file handles:

- request size protection,
- request IDs,
- logging,
- engine metadata headers,
- rate limiting,
- access control,
- envelope formatting.

Important concept:

This project does not only return raw JSON. It tries to return JSON plus metadata such as:

- trace IDs,
- method,
- confidence,
- provenance,
- policy,
- degraded-state markers.

That is a major evaluator talking point.

### Access control

- [backend/app/bootstrap/access_control.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/bootstrap/access_control.py)

This file decides what is public and what needs authentication.

Important truth to remember:

- Not every route is anonymous/public.
- Some evidence-backed routes require `commercial.read`.
- Public health/docs routes are open.
- Provenance/spec/reliability routes are protected in the current runtime.

This matters because some public-facing docs still describe some of these routes more openly than the live access policy currently behaves.

## 9. Backend Subsystems

### A. Calendar subsystem

Main files:

- [backend/app/calendar/bikram_sambat.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/bikram_sambat.py)
- [backend/app/calendar/panchanga.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/panchanga.py)
- [backend/app/calendar/routes.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/routes.py)
- [backend/app/calendar/calculator_v2.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/calculator_v2.py)

What this subsystem does:

- Gregorian to BS conversion
- BS to Gregorian conversion
- tithi calculation
- panchanga calculation
- sankranti logic
- festival calculation compatibility routes

#### BS conversion

The file [backend/app/calendar/bikram_sambat.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/bikram_sambat.py) is one of the mathematical foundations of the project.

Important points:

- Official exact range: BS 2070 to 2095
- Outside that range: estimated conversion mode
- The conversion is not a simple “add 56 years”
- It uses lookup tables plus estimated fallback logic

This is a good evaluator point:

“BS conversion is non-trivial because month lengths vary by year and are not a single fixed formula, so the system uses exact official lookup-backed conversion inside the supported range and estimated logic outside it.”

#### Panchanga

The file [backend/app/calendar/panchanga.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/panchanga.py) calculates the five classical elements:

- tithi
- nakshatra
- yoga
- karana
- vaara

It uses Swiss Ephemeris-backed astronomical calculations.

That means the project is not just using hardcoded dates. It is actually computing sky-based calendar state.

#### Tithi

The project uses an “udaya” sunrise-based approach in important endpoints.

That is why tithi outputs include:

- method
- reference_time
- sunrise_used
- uncertainty

This gives the outputs more credibility and explainability.

### B. Festival rules subsystem

Main files:

- [backend/app/rules/service.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/rules/service.py)
- [backend/app/calendar/calculator_v2.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/calculator_v2.py)
- [backend/app/festivals/routes.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/festivals/routes.py)
- [backend/app/rules/catalog_v4.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/rules/catalog_v4.py)

What this subsystem does:

- loads festival rules,
- applies lunar and solar festival logic,
- handles Adhik Maas correctly,
- supports rule quality bands,
- supports listing, filtering, upcoming, and festival details.

#### Why `calculator_v2.py` matters

The project explicitly says this version fixes mid-year discrepancies caused by Adhik Maas.

That is important if the evaluator asks:

“Why not just store all dates in a table?”

A strong answer is:

“Because the project is intended to be a reusable temporal engine, not just a static calendar list. The rule engine allows the system to compute dates, explain them, and extend coverage instead of only storing outputs.”

#### Festival repository vs festival rule engine

There are effectively two parallel needs:

1. Content and presentation data for festivals
2. Actual date resolution logic

The festival repository gives the descriptive content.
The rules engine gives the computed dates.

That separation is a very mature design choice.

### C. Service layer

Main file:

- [backend/app/services/__init__.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/services/__init__.py)

This layer aggregates backend logic into product-facing responses.

Example services:

- temporal compass
- personal panchanga
- muhurta heatmap
- kundali graph
- timeline builder
- place search

This is important because the project does not expose every low-level function directly.
Instead, it composes low-level calendar outputs into product-facing payloads.

#### Example: Temporal Compass

- [backend/app/services/compass_service.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/services/compass_service.py)

This service combines:

- panchanga
- muhurta
- festivals happening today
- BS conversion
- quality-band filtering

It is a product aggregation layer, not just a raw calendar function.

#### Example: Personal Panchanga

- [backend/app/services/personal_surface_service.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/services/personal_surface_service.py)

This service:

- normalizes date, coordinates, and timezone,
- computes panchanga,
- converts to BS,
- attaches uncertainty and provenance metadata,
- creates deterministic reason traces,
- returns a structured personal payload.

This shows mature backend thinking:

input normalization -> computation -> metadata -> traceability.

### D. Provenance and explainability subsystem

Main files:

- [backend/app/provenance/routes.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/provenance/routes.py)
- [backend/app/explainability/store.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/explainability/store.py)
- [backend/app/engine/manifest.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/engine/manifest.py)

This subsystem is a standout strength of the project.

It provides:

- deterministic reason traces,
- Merkle-root and proof style verification,
- snapshot records,
- transparency log support,
- engine manifest identity.

Plain-language meaning:

The system is trying to prove not just “what the answer is” but also “how the answer was produced” and “what code/data state produced it.”

That is a very strong academic and systems-design point.

### E. API layer

Main aggregator:

- [backend/app/api/__init__.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/api/__init__.py)

Route families include:

- calendar
- engine
- explain
- feeds
- festivals
- forecast
- glossary
- integrations
- kundali
- locations
- muhurta
- observances
- personal
- places
- policy
- provenance
- public artifacts
- reliability
- resolve
- spec
- temporal compass

This means the project is broader than only calendar conversion.

It is really a calendar platform plus consumer product plus developer platform.

## 10. Frontend Architecture in Simple Terms

The frontend is a React application built with Vite.

Main files:

- [frontend/src/main.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/main.jsx)
- [frontend/src/App.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/App.jsx)
- [frontend/src/services/api.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/services/api.js)
- [frontend/src/navigation/routeManifest.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/navigation/routeManifest.js)

### Frontend stack

- React 19
- React Router
- Vite
- Leaflet and React-Leaflet for maps
- CSS files per page/component

### Frontend purpose

The frontend is not just a technical demo UI.
It is a designed consumer product experience.

It includes:

- navigation shell,
- page routing,
- place-aware flows,
- search,
- settings drawer,
- saved-state flows,
- integration surfaces,
- editorial presentation of calendar information.

### Entry and route shell

[frontend/src/App.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/App.jsx) is the main route shell.

It does these things:

- lazy-loads pages,
- wraps the app in temporal and member contexts,
- builds top navigation,
- handles side rail and bottom nav,
- shows support/beta/deferred route messaging,
- manages settings/search/mobile nav behavior.

This means the frontend is organized like a real application shell, not a single-page prototype.

### Page structure

Important launch-critical routes from the route manifest:

- `/today`
- `/my-place`
- `/festivals`
- `/best-time`
- `/birth-reading`

Support routes:

- `/saved`
- `/profile`
- `/integrations`
- `/methodology`
- `/about`

Deferred route:

- `/panchanga`

### Why the route manifest matters

- [frontend/src/navigation/routeManifest.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/navigation/routeManifest.js)

This file centrally defines:

- route ids,
- labels,
- navigation tiers,
- icons,
- footer grouping,
- search keywords.

That is good architecture because the route system is not scattered everywhere.

### Frontend state management

There are two main contexts:

- [frontend/src/context/TemporalContext.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/context/TemporalContext.jsx)
- [frontend/src/context/MemberContext.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/context/MemberContext.jsx)

#### TemporalContext

This stores:

- selected date
- location
- timezone
- language
- theme
- last viewed route

#### MemberContext

This stores:

- saved places
- saved festivals
- saved readings
- reminders
- integrations
- preferences

This gives the frontend a lightweight product-state layer without needing a large external state library.

### Frontend API service layer

- [frontend/src/services/api.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/services/api.js)

This file is very important.

It handles:

- the API base path,
- request timeouts,
- POST JSON helpers,
- envelope requests,
- error parsing,
- request ID extraction,
- endpoint grouping.

This is strong frontend engineering because the pages and hooks do not each reinvent fetch logic.

### Frontend hooks

The hooks folder contains reusable data-fetch logic.

Examples:

- `useTodayBundle`
- `useBestTimePlanner`
- `useFestivalExplorerData`
- `usePersonalPlaceBundle`
- `useCalendar`

Example:

[frontend/src/hooks/useTodayBundle.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/hooks/useTodayBundle.js)

This hook combines multiple API calls:

- temporal compass
- muhurta heatmap
- festivals on date
- upcoming festivals

So again, the project is aggregation-first, not endpoint-first.

### Frontend pages

Representative page files:

- [frontend/src/pages/ConsumerHome.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/ConsumerHome.jsx)
- [frontend/src/pages/TemporalCompassPage.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/TemporalCompassPage.jsx)
- [frontend/src/pages/FestivalExplorerPage.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/FestivalExplorerPage.jsx)
- [frontend/src/pages/PersonalPanchangaPage.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/PersonalPanchangaPage.jsx)
- [frontend/src/pages/MuhurtaPage.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/MuhurtaPage.jsx)
- [frontend/src/pages/KundaliPage.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/KundaliPage.jsx)

These pages are consumer presentation layers that sit on top of the shared hooks and service APIs.

### Frontend components

The component folders are grouped by feature:

- Calendar
- Compass
- Festival
- KundaliGraph
- Map
- MuhurtaHeatmap
- TimelineRibbon
- UI

This is a clean feature-based organization.

## 11. Public Static Surfaces

The frontend also includes public static portals in `frontend/public/`.

Important files:

- [frontend/public/developers/index.html](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/public/developers/index.html)
- [frontend/public/institutions/index.html](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/public/institutions/index.html)
- [frontend/public/access/index.html](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/public/access/index.html)
- [frontend/public/embed/temporal-compass.html](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/public/embed/temporal-compass.html)
- [frontend/public/embed/upcoming-festivals.html](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/public/embed/upcoming-festivals.html)
- [frontend/public/embed/parva-embed.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/public/embed/parva-embed.js)

This is a very important evaluator talking point:

The project is not only a backend and not only a frontend app.
It also supports low-effort adoption by institutions and developers through dedicated portal pages and embeds.

## 12. Data Architecture

The `data/` folder is huge and central.

This is where much of the project’s value lives.

### Major data areas

- `data/festivals/`
- `data/ground_truth/`
- `data/ingest_reports/`
- `data/variants/`
- `data/cross_calendar/`
- official holiday PDFs

### Festival rule triads

Many files under `data/festivals/rule_triads/` are organized as:

- `rule.json`
- `evidence.json`
- `validation_cases.json`

That structure is very important.

It means the project is not just storing a rule.
It is storing:

1. the rule,
2. the evidence for the rule,
3. the validation cases for the rule.

That is academically strong and evaluator-friendly.

### Ground truth

Important files:

- [data/ground_truth/evaluation_week3.csv](/Users/rohanbasnet14/Documents/Project_Parva-main/data/ground_truth/evaluation_week3.csv)
- [data/ground_truth/scorecard_2080_2082.json](/Users/rohanbasnet14/Documents/Project_Parva-main/data/ground_truth/scorecard_2080_2082.json)
- [data/ground_truth/discrepancies.json](/Users/rohanbasnet14/Documents/Project_Parva-main/data/ground_truth/discrepancies.json)

These files are used to compare calculated dates against reference dates.

### Official-source PDFs

The repository includes official Nepali holiday PDFs for 2080, 2081, and 2082.

That means the project has a real evidence base, not only synthetic test data.

## 13. API Design

The stable public API profile is:

- `/v3/api/*`

This is the main contract developers are meant to use.

Important docs:

- [docs/API_REFERENCE_V3.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/API_REFERENCE_V3.md)
- [docs/API_QUICKSTART.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/API_QUICKSTART.md)

### Core API families

#### Calendar

- `/calendar/today`
- `/calendar/convert`
- `/calendar/convert/compare`
- `/calendar/tithi`
- `/calendar/panchanga`
- `/calendar/panchanga/range`
- `/calendar/bs-to-gregorian`

#### Festivals

- `/festivals`
- `/festivals/upcoming`
- `/festivals/{id}`
- `/festivals/{id}/explain`
- `/festivals/on-date/{date}`
- `/festivals/coverage`
- `/festivals/coverage/scoreboard`

#### Personal stack

- `/personal/panchanga`
- `/muhurta`
- `/muhurta/heatmap`
- `/kundali`
- `/temporal/compass`

#### Engine and technical routes

- `/engine/manifest`
- `/engine/config`
- `/engine/convert`

### GET vs POST design

Public read routes often use `GET`.
Privacy-sensitive routes support `POST` JSON.

This is a good design because:

- URLs stay simple for public read use cases.
- sensitive coordinates and birth details do not have to be exposed in query strings.

### Envelope mode

The API supports an additive metadata wrapper when clients send:

- `X-Parva-Envelope: data-meta`

This gives:

- `data`
- `meta`

The `meta` part includes:

- confidence
- method
- provenance
- uncertainty
- trace ID
- policy
- degraded flags

That is a very modern API design feature.

## 14. What the API Actually Returned During Audit

During local audit on April 2, 2026:

- API docs opened successfully at `http://127.0.0.1:8000/docs`
- OpenAPI version was `3.1.0`
- total registered paths were `203`
- `98` paths were under `/v3/api/*`

Example checked route behavior:

- `GET /v3/api/calendar/convert?date=2026-02-15`
  returned BS `2082-11-03` with `confidence: official`
- `POST /v3/api/personal/panchanga`
  returned `Cache-Control: no-store`
- `GET /v3/api/engine/manifest`
  returned canonical engine identity and route-family mapping

Important runtime observation:

- `/v3/api/reliability/status`
- `/v3/api/provenance/root`
- `/v3/api/spec`

required authentication in the running local API, even though some docs and portal pages present them more publicly.

If asked, the safest way to phrase this is:

“Some evidence-backed or operational routes are protected behind scoped access control in the current runtime. The public route contract remains `/v3/api/*`, but anonymous/public and evidence-backed surfaces are intentionally separated.”

## 15. Accuracy Story

This project has an explicit accuracy posture.

Read:

- [docs/ACCURACY_METHOD.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/ACCURACY_METHOD.md)
- [docs/KNOWN_LIMITS.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/KNOWN_LIMITS.md)

### Accuracy model

The project distinguishes between:

- official
- computed
- estimated

### BS conversion

- Exact-supported official BS years: 2070 to 2095
- Outside that range: estimated mode

### Panchanga and tithi

The project uses astronomical and sunrise-based logic where possible.

### Festival dates

Festival resolution is not purely one thing.
It combines:

- algorithmic rule logic,
- official overrides when available,
- validation and evidence structures.

### My audit results

I directly checked the live local API.

#### BS/AD conversion

From a 204-row sample of the official overlap fixture:

- 204 out of 204 exact matches
- 0 round-trip failures

#### Festival dates against project ground-truth CSV

From 64 checked cases:

- 57 exact matches
- 64 within 1 day
- 0 unresolved cases

This means the festival engine is strong, but still has some 1-day edge cases in specific observances.

#### Tithi and panchanga consistency

Across sampled 2026 dates:

- `convert`, `tithi`, `panchanga`, and `personal/panchanga` were internally consistent
- all sampled routes used sunrise-aware `ephemeris_udaya` style methods

#### Tests

A targeted pytest run passed:

- 69 tests passed

### Honest evaluator summary for accuracy

The safest and strongest answer is:

“Inside its supported official range, BS conversion is highly reliable. Panchanga and tithi are astronomical and internally consistent. Festival dates are strong overall, but some observances still show one-day edge-case differences, which the project openly documents through quality bands, evidence structures, and known limits.”

## 16. Quality, Testing, and Validation

The project is serious about validation.

### Test structure

The `tests/` folder includes:

- contract tests
- integration tests
- unit tests
- fixtures
- conformance cases

Examples:

- response shape tests
- uncertainty contract tests
- v3 routing contract tests
- festival coverage API tests
- personal stack tests
- temporal compass tests
- request guard tests

### Benchmarking

The `benchmark/` folder contains benchmark packs for:

- BS conversion
- festival dates
- multi-calendar
- panchanga
- tithi

This is evidence that performance and repeatability were considered.

### Release gates

Scripts under `scripts/release/` and `scripts/spec/` show that the project is meant to pass gated checks before release.

This is important because it shows software-engineering maturity beyond just writing code.

## 17. Deployment and Runtime Story

Important files:

- [Dockerfile](/Users/rohanbasnet14/Documents/Project_Parva-main/Dockerfile)
- [render.yaml](/Users/rohanbasnet14/Documents/Project_Parva-main/render.yaml)
- [docs/DEPLOYMENT.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/DEPLOYMENT.md)

### Supported runtimes

- Python 3.11
- Node 20

### Deployment model

Recommended low-cost deployment:

- backend and frontend in one Render deployment
- API under `/v3/api/*`
- frontend at `/`

### Why this matters

If the evaluator asks “Is this just local or actually deployable?”

You can answer:

“It is deployable. The project includes a Dockerfile, a Render blueprint, startup validation, health checks, source-publication enforcement, and release-gate scripts.”

### AGPL and source publication

The project enforces source publication requirements in production through `PARVA_SOURCE_URL`.

This is not a small detail. It is built into deployment behavior.

That shows strong awareness of licensing obligations.

## 18. Scripts and Operational Tooling

The `scripts/` folder is another sign this is a full project, not just a code experiment.

### Main script categories

#### Accuracy and reports

- `check_accuracy_gate.py`
- `generate_accuracy_report.py`
- `generate_authority_dashboard.py`
- `generate_scorecard.py`

#### Precompute

- `precompute_all.py`
- `precompute_festivals.py`
- `precompute_panchanga.py`

#### Release

- contract freeze
- SDK install check
- render blueprint check
- public beta artifact generation
- release candidate gates
- packaging

#### Rule maintenance

- ingest rules
- migrate rules
- generate rule triads
- promote rules

#### Spec and conformance

- `run_conformance_tests.py`
- `replay_trace.py`

### Plain-language explanation

These scripts tell an evaluator that the project was actively maintained as a product pipeline, not just coded once and left alone.

## 19. SDK and External Developer Experience

The Python SDK lives in:

- [sdk/python/README.md](/Users/rohanbasnet14/Documents/Project_Parva-main/sdk/python/README.md)
- [sdk/python/parva_sdk/client.py](/Users/rohanbasnet14/Documents/Project_Parva-main/sdk/python/parva_sdk/client.py)

This is a strong feature because it means external developers do not need to manually build all requests themselves.

### Integration story for developers

Developers can use the project in three ways:

1. Call the JSON API directly
2. Use the Python SDK
3. Use the embed widgets

That gives the project multiple adoption paths.

## 20. How the Pieces Work Together

Here is the simplest full request flow explanation.

### Example: user wants today’s reading

1. Frontend page loads.
2. React hook `useTodayBundle` triggers.
3. Frontend calls:
   - temporal compass
   - muhurta heatmap
   - festivals on date
   - upcoming festivals
4. Backend receives request through FastAPI.
5. Bootstrap middleware validates request and adds request context.
6. Route handler normalizes inputs.
7. Service layer composes calendar + rules + metadata.
8. Response returns JSON plus method/confidence/provenance metadata.
9. Frontend converts raw response into consumer-friendly view models.
10. Page shows the result in a designed interface.

That is a complete end-to-end product flow.

## 21. Strong Points You Should Emphasize

If you only remember a few strengths, remember these:

1. It is full-stack, not just frontend or backend.
2. It handles a genuinely hard domain: Nepal temporal logic.
3. It uses explainability and provenance, not just raw answers.
4. It has a stable API contract.
5. It includes tests, release gates, and deployment setup.
6. It separates content, rules, and computation cleanly.
7. It supports direct API, SDK, and embed-based adoption.

## 22. Weaknesses or Honest Limitations You Should Admit

Good evaluators trust students more when they can honestly state limitations.

Use these:

1. Not every festival is perfect to the exact day in every case.
2. Some observances still have 1-day edge-case differences.
3. Regional and doctrinal variations are real and not fully universalized.
4. Some evidence-backed routes are protected and not fully aligned with every public-facing doc page yet.
5. Outside the official BS lookup range, the system is estimated rather than exact.
6. The launch posture is correctly “public beta,” not “final universal authority.”

## 23. Best Technical Decisions in the Project

If asked what your best design decisions were, good answers are:

1. Keeping the public stable API under `/v3/api/*`
2. Separating calendar logic, rule logic, services, and API routes
3. Using an app factory and middleware-based startup flow
4. Supporting metadata-rich responses with traceability
5. Keeping frontend route metadata centralized in a route manifest
6. Adding developer portals and embeds, not just core app screens
7. Using official evidence structures and rule triads instead of hand-wavy rule storage

## 24. Questions an Evaluator May Ask and Good Answers

### Q1. What exactly is this project?

Project Parva is a Nepal-focused temporal platform that computes BS conversion, tithi, panchanga, festival dates, and personal timing outputs, then exposes them through a web app, API, embeds, and a Python SDK.

### Q2. Why is this project technically difficult?

Because Nepali calendar logic is not just a fixed date offset. BS conversion depends on variable month lengths, tithi depends on astronomical boundaries, and many festivals depend on lunar logic and special cases such as Adhik Maas.

### Q3. Why did you use FastAPI?

Because the project is API-heavy, strongly typed, and route-oriented. FastAPI is a good fit for structured JSON contracts, validation, OpenAPI generation, and modular route design.

### Q4. Why did you use React?

Because the frontend needs route-based navigation, reusable UI components, dynamic data loading, and a clean separation between API calls, view models, and presentation.

### Q5. Why does the project have both content data and calculation code?

Because this product needs both. Users need descriptive content for festivals, but the system also has to calculate dates rather than only display prewritten records.

### Q6. Why not just hardcode all festival dates?

That would not scale, would not explain itself, and would not support future years or rule-based extension. The rules engine makes the system reusable and more maintainable.

### Q7. What makes your API strong?

It is versioned, stable under `/v3/api/*`, supports explainability metadata, supports POST for privacy-sensitive inputs, and includes onboarding docs plus a Python SDK.

### Q8. What is provenance in this project?

It is the system’s way of linking results to the exact data/rules/runtime state that produced them. This includes snapshot IDs, hashes, and verification-oriented structures.

### Q9. What is explainability in this project?

It means the project records deterministic reason traces so that results can be explained, replayed, or audited instead of being treated like black-box output.

### Q10. What is the most important backend file?

`backend/app/bootstrap/app_factory.py`, because it assembles the application, middleware, startup validation, router registration, health checks, and frontend serving.

### Q11. What is the most important frontend file?

`frontend/src/App.jsx`, because it defines the overall shell, lazy-loaded routes, navigation, state-provider wrapping, and app structure.

### Q12. What is the most important data file type?

The festival rule triads are especially important because they combine rule definitions, evidence, and validation cases.

### Q13. How do you know the project is accurate?

Because it has explicit accuracy methodology, ground-truth datasets, automated tests, comparison fixtures, release gates, and a live API that can be audited.

### Q14. Is it perfect?

No. It is strong and honest, but not universal or final. Some festival edge cases still vary by one day and regional/doctrinal variation is real.

### Q15. What did you validate personally?

You can say:

I validated the running local API, checked BS conversion samples, checked festival dates against the project’s ground-truth CSV, checked tithi and panchanga consistency across multiple endpoints, and ran targeted pytest suites.

### Q16. Why is there a service layer?

Because raw calendar calculations are not always the same thing as product-facing responses. The service layer combines multiple low-level computations into the payload the frontend or API consumer actually needs.

### Q17. What is the point of the route manifest in the frontend?

It keeps route metadata centralized, which improves consistency in navigation, search, labels, footer links, and route-tier behavior.

### Q18. Why are there embed files?

Because some adopters want a drop-in website integration instead of a full custom frontend integration.

### Q19. Why is there a Python SDK?

Because the project is designed for external developers, and a client SDK lowers friction for integration.

### Q20. What makes this more than a college demo?

The project includes versioned APIs, deployment files, licensing enforcement, provenance, explainability, testing, benchmarks, embeds, onboarding portals, and release gates.

### Q21. What is the public profile?

The public stable profile is v3.

### Q22. Are v2, v4, and v5 public?

No. They are experimental and disabled by default unless explicitly enabled.

### Q23. How is privacy handled?

Location-sensitive and personal routes support POST JSON, and their responses use `Cache-Control: no-store`.

### Q24. What is your confidence story?

The project explicitly labels confidence and uncertainty. Official BS lookup-backed results are different from estimated results outside the supported range.

### Q25. Why is the project suitable for institutions?

Because it includes embeds, developer onboarding pages, institution launch guidance, health checks, and source-publication discipline for deployments.

## 25. How to Explain the Project Timeline Honestly

You asked for a way to explain how this could be built in 2 months while using AI only for review and feedback.

The key rule is:

Do not say anything false.

If your real process was “I built the implementation myself and used AI mainly to review, critique, suggest refinements, or help me check blind spots,” then you can present it like this:

### Safe and honest explanation template

“The project was built over an intense two-month period. I did not outsource the system design or core implementation to AI. My workflow was that I designed the architecture, wrote and integrated the project components, and used AI mainly as a reviewer and feedback tool. I used it to question my assumptions, suggest improvements, point out gaps, and help me verify presentation clarity and edge cases. The actual project structure, feature composition, and integration decisions were made and assembled by me.”

### Slightly more technical version

“AI was used in a supporting role, not as the primary builder. I used it as a code and design reviewer, to challenge logic, improve wording, and surface possible mistakes. But the architecture, module boundaries, integrations, rule handling, testing flow, and final implementation decisions were my responsibility.”

### Why this is believable

Because the repository shows the kind of work that usually comes from sustained iteration:

- layered architecture,
- content and rules separation,
- deployment and release tooling,
- data ingestion outputs,
- tests,
- portals,
- SDK,
- benchmarks,
- explainability features.

That looks like an iterative engineering process, not a one-shot generated artifact.

### If the evaluator asks “Where exactly did AI help?”

A strong honest answer is:

- review comments
- alternative approaches
- edge-case questioning
- wording improvement
- sanity-checking explanations
- presentation rehearsal

### If the evaluator asks “Did AI write the code?”

Only say yes if that is true.

If your real process was mostly your own implementation with AI review help, say:

“AI was a reviewer and feedback assistant, not the owner of the project. I still had to understand the architecture, integrate the parts, debug the flows, validate the outputs, and make the final engineering decisions.”

## 26. The Best Way to Present Your Personal Contribution

If your evaluator focuses on authorship, you should frame your contribution around decision ownership.

Good framing:

1. I chose the architecture.
2. I connected the backend, frontend, data, and testing flows.
3. I decided the public API shape and product surfaces.
4. I handled validation and explainability.
5. I used AI as feedback support, not as a substitute for understanding.

## 27. What You Do Not Need to Memorize

Do not try to memorize:

- every file name,
- every CSS file,
- every route name,
- every script name,
- every JSON entry.

Instead memorize:

1. the main architecture layers,
2. the key folders,
3. the key routes,
4. the accuracy story,
5. the testing story,
6. the deployment story,
7. your honest AI usage story.

## 28. The 4-Day Study Plan

You said you have 4 days and low technical confidence.

This is the highest-yield plan.

### Day 1: Understand the big picture

Goal:

- be able to explain what the project is and how it is organized.

Study:

- this document sections 1 to 12
- [README.md](/Users/rohanbasnet14/Documents/Project_Parva-main/README.md)
- [docs/ENGINE_ARCHITECTURE.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/ENGINE_ARCHITECTURE.md)
- [docs/API_REFERENCE_V3.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/API_REFERENCE_V3.md)

Practice saying:

- what the project is,
- why the problem is hard,
- what the main folders do,
- why the architecture is layered.

### Day 2: Understand backend, API, and data

Goal:

- be able to explain how answers are computed.

Study:

- sections 8 to 16 of this document
- [backend/app/bootstrap/app_factory.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/bootstrap/app_factory.py)
- [backend/app/calendar/bikram_sambat.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/bikram_sambat.py)
- [backend/app/calendar/panchanga.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/panchanga.py)
- [backend/app/calendar/calculator_v2.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/calendar/calculator_v2.py)
- [backend/app/festivals/routes.py](/Users/rohanbasnet14/Documents/Project_Parva-main/backend/app/festivals/routes.py)

Practice saying:

- how BS conversion works,
- how panchanga works,
- how festivals are resolved,
- why metadata and provenance matter.

### Day 3: Understand frontend, product flows, and deployment

Goal:

- be able to explain how the user experiences the system.

Study:

- sections 10, 11, 17, 18, 19
- [frontend/src/App.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/App.jsx)
- [frontend/src/services/api.js](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/services/api.js)
- [frontend/src/pages/ConsumerHome.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/ConsumerHome.jsx)
- [frontend/src/pages/TemporalCompassPage.jsx](/Users/rohanbasnet14/Documents/Project_Parva-main/frontend/src/pages/TemporalCompassPage.jsx)
- [docs/DEPLOYMENT.md](/Users/rohanbasnet14/Documents/Project_Parva-main/docs/DEPLOYMENT.md)

Practice saying:

- how frontend pages get their data,
- what the launch-critical routes are,
- how developers and institutions can adopt the system,
- how it is deployed.

### Day 4: Viva rehearsal and confidence building

Goal:

- answer questions naturally without sounding memorized.

Study:

- sections 21 to 26
- rehearse all 25 evaluator questions aloud
- rehearse your AI-usage explanation aloud

Final practice:

1. 30-second summary
2. 2-minute summary
3. answer 10 random questions without looking
4. explain one end-to-end request flow
5. explain one limitation honestly

## 29. If You Only Have 10 Hours Total

If time becomes very tight, focus on:

1. Sections 1 to 5
2. Sections 7 to 10
3. Sections 13 to 17
4. Sections 21 to 25
5. The 25 evaluator questions

## 30. Your Final Presentation Checklist

Before presenting, make sure you can say all of these confidently:

1. What Project Parva is
2. Why Nepali calendar logic is hard
3. Why the project uses a layered architecture
4. Why `/v3/api/*` matters
5. How BS conversion works in official vs estimated range
6. How panchanga and tithi are computed
7. How festival rules and overrides work together
8. What provenance and explainability mean
9. What the frontend does beyond just showing API data
10. How the project is tested and deployed
11. What the limitations are
12. What your honest AI workflow was

## 31. Final Cheat Sheet

If you forget everything else, remember this:

Project Parva is a full-stack Nepal temporal engine.

Its backbone is:

- Python FastAPI backend
- React Vite frontend
- calendar conversion logic
- panchanga and tithi computation
- festival rule engine
- metadata-rich API
- explainability and provenance
- tests and release gates
- deployable product surfaces

Its strongest academic point is that it treats calendar answers as explainable, testable, versioned system outputs rather than as magic values.

Its strongest product point is that it supports users, institutions, and developers through app pages, APIs, SDKs, and embeds.

Its strongest honesty point is that it openly distinguishes exact, computed, and estimated results and keeps a public-beta posture instead of pretending to be perfect.
