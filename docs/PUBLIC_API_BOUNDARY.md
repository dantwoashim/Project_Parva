---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Public API Boundary

Status: Phase 04 public/private route boundary.

The public Project Parva deployment exposes stable calendar, fiscal-year, festival, panchanga, and public methodology surfaces for technical evaluation. The lightweight Render demo may expose a narrower route set than a private or full public profile.

The public deployment is intentionally narrower than a private deployment. Sensitive future-BS workflows remain disabled unless an operator explicitly enables experimental routes and private schema visibility.

## Public By Default

| Surface | Purpose |
| --- | --- |
| `/health/*` | Service health and readiness checks |
| `/v3/api/calendar/*` | BS/AD conversion, today, validation, calendar utilities, and enabled panchanga helpers |
| `/v3/api/enterprise/*` | Nepali fiscal-year and business date validation logic |
| `/v3/api/compliance/*` | Compliance-preview profile decisions in full/private profiles, excluded from the lightweight public demo |
| `/v3/api/trust/*` | Public-safe source registry, release manifest, release diff, trust log, and evidence packet metadata |
| `/v3/api/timegraph/*` | Public-safe temporal fact graph, relationship, trace, and conflict metadata |
| `/v3/api/rules/*` | Public-safe RuleLang registry, validation, bounded execution, tests, and explanation traces |
| `/v3/api/impact/*` | Bounded temporal impact simulation in full or private profiles, excluded from the lightweight public demo |
| `/v3/api/agent/*` | Agent-safe deterministic temporal tools in full or private profiles, excluded from the lightweight public demo |
| `/v3/api/protocol/*` | Protocol draft metadata and alpha conformance in full or private profiles, excluded from the lightweight public demo |
| `/v3/api/festivals/*` | Festival and observance APIs |
| `/v4/api/future-bs/capabilities` | Public summary of the future-BS research layer |
| `/v5/api/calendar-model-risk/capabilities` | Public summary of model-risk methodology when the full public profile is enabled |

## Private By Default

These surfaces are not part of the public deployment by default:

- direct future BS month-length prediction
- full future range prediction
- CSV or XLSX future exports
- model runs
- backtests
- residual analysis
- detailed explain endpoints that reveal future outputs
- boundary-risk endpoints that reveal future outputs
- loan or schedule-impact simulation using future vectors
- external sheet import or comparison workflows
- corrected-value outputs
- private model internals
- private TimeGraph facts, private archive paths, and unpublished source contents
- private RuleLang rules and private source-backed rule registries
- unverified future BS-to-AD conversion through public calendar routes unless an operator explicitly accepts that exposure

## Required Public Settings

Public deployments should keep:

```text
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_ROUTE_PROFILE=public_demo
PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION=false
```

With this policy, `/v3/api/calendar/bs-to-gregorian` serves verified public calendar ranges but blocks exact public output for unverified future BS years. A private deployment may set `PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION=true` only if the operator intentionally accepts that exact future conversion outputs are public for that deployment.

Future outputs are treated as:

```text
computed_prediction_not_official
```

The public service is not an official government calendar publication and is not legal, tax, regulatory, or banking-contract final authority.
