# Public API Boundary

The public Project Parva deployment exposes stable calendar, fiscal-year, festival, panchanga, and public methodology surfaces for technical evaluation. The lightweight Render demo may expose a narrower route set than a private or full public profile.

The public deployment is intentionally narrower than a private deployment. Sensitive future-BS workflows remain disabled unless an operator explicitly enables experimental routes and private schema visibility.

## Public By Default

| Surface | Purpose |
| --- | --- |
| `/health/*` | Service health and readiness checks |
| `/v3/api/calendar/*` | BS/AD conversion, today, validation, calendar utilities, and enabled panchanga helpers |
| `/v3/api/enterprise/*` | Nepali fiscal-year and business date validation logic |
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

## Required Public Settings

Public deployments should keep:

```text
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_ROUTE_PROFILE=public_demo
```

Future outputs are treated as:

```text
computed_prediction_not_official
```

The public service is not an official government calendar publication and is not legal, tax, regulatory, or banking-contract final authority.
