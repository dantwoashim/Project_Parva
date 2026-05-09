# Project Parva

Project Parva is open-source Nepali temporal infrastructure for Bikram Sambat conversion, fiscal-year logic, panchanga computation, festivals, and source-aware calendar validation.

It also includes a controlled future-BS risk research layer for evaluating month-length assumptions before they affect financial, contractual, reporting, or operational systems.

## Why This Exists

Nepali calendar logic is infrastructure, not decoration.

BS dates affect fiscal reports, payroll, contracts, transaction records, holidays, reporting periods, renewals, interest periods, compliance exports, and audit trails. Fragile calendar tables can quietly become operational risk when they are copied, extended, or updated without source policy.

Parva treats calendar behavior as something that should be explainable, source-aware, reproducible, and honest about confidence.

## What Parva Provides

| Area | Purpose |
| --- | --- |
| Calendar conversion | BS to AD, AD to BS, today endpoints, and month metadata |
| Fiscal-year logic | Nepali fiscal boundaries, fiscal labels, periods, and date-range helpers |
| Date validation | BS date validation and published-range checks |
| Panchanga and lunar computation | Tithi, nakshatra, yoga, karana, paksha, and related computation where enabled |
| Festival intelligence | Festival catalog, observance rules, calendar feeds, and explanations |
| Developer API | FastAPI endpoints, OpenAPI docs, examples, and integration-ready responses |
| Source policy | Source tiers, claim boundaries, and reliability metadata |
| Future BS risk research | Experimental month-length risk analysis, source-aware validation, and review labels |

## Live Surfaces

- Website: [https://prabinghimire1.com.np](https://prabinghimire1.com.np)
- API docs: [https://api.prabinghimire1.com.np/docs](https://api.prabinghimire1.com.np/docs)
- OpenAPI: [https://api.prabinghimire1.com.np/openapi.json](https://api.prabinghimire1.com.np/openapi.json)
- Source: [https://github.com/dantwoashim/Project_Parva](https://github.com/dantwoashim/Project_Parva)

The public API demo is optimized for evaluation. First requests may take a few seconds if the instance is waking up.

## Public API Boundary

The public deployment exposes stable calendar and documentation surfaces intended for technical evaluation. The lightweight Render demo may expose a narrower subset than a private or full public profile.

Public surfaces in the full public profile include:

| Surface | Purpose |
| --- | --- |
| `/v3/api/calendar/*` | BS/AD conversion, today, validation, calendar utilities, and enabled panchanga helpers |
| `/v3/api/enterprise/*` | Nepali fiscal-year and business date validation logic |
| `/v3/api/festivals/*` | Festival and observance APIs |
| `/v4/api/future-bs/capabilities` | Public summary of the future-BS research layer |

Private or experimental future-BS routes are not part of the public deployment by default. Future month-length prediction, exports, model runs, backtests, client comparison workflows, and schedule-impact simulations are intended for controlled evaluation or private deployment.

## Future BS Risk Research

Parva does not publish guaranteed future BS dates.

The research layer studies whether future BS month-length assumptions are stable, boundary-sensitive, source-conflicted, or review-worthy before they enter financial, contractual, reporting, or operational systems.

Future-BS outputs are labeled:

```text
computed_prediction_not_official
```

## Current Research Result

In the current Tier 1 official-verified validation window available to Parva, covering 2078-2083 BS, a reference-calibrated solar-civil computational path matched all 72 official month lengths in that window.

A legacy/static baseline matched 68 out of 72 on the same window, with misses concentrated around boundary-sensitive months.

This is a limited validation result. It is not a claim of official authority, guaranteed future accuracy, or broad future-calendar certainty.

## Source Policy

Parva does not treat every calendar row as equal.

Calendar evidence is classified by source strength:

| Tier | Meaning |
| --- | --- |
| Official verified | Government or official publication evidence |
| Printed verified | Identifiable printed calendar or panchanga evidence |
| Public witness | Public dated material that links AD and BS dates |
| Publisher reference | Public calendar or publisher material |
| Software/table reference | Open-source or static lookup references |
| Third-party reference | App or site references used for comparison, not authority |
| Needs review | Ambiguous, conflicting, or incomplete evidence |

Weak third-party rows and software-table rows can help with comparison, disagreement detection, and review targeting. They do not support official-grade claims.

## Developer Quickstart

Base URL:

```text
https://api.prabinghimire1.com.np
```

Today:

```bash
curl https://api.prabinghimire1.com.np/v3/api/calendar/today
```

AD to BS:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2026-04-14"
```

BS to AD:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/calendar/bs-to-gregorian \
  -H "Content-Type: application/json" \
  -d '{"year":2083,"month":1,"day":1}'
```

Future-BS research capabilities:

```bash
curl https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Public examples intentionally avoid direct future month-length prediction, future exports, backtests, model runs, schedule-impact simulation, and private comparison workflows.

## Deployment Model

Project Parva is designed to run in two modes:

| Mode | Purpose |
| --- | --- |
| Public demo | Lightweight API evaluation, documentation, stable calendar endpoints |
| Private deployment | Version-pinned deployment for organizations that need controlled calendar validation, internal audits, or sensitive future-BS risk workflows |

The public service is not the authority for legal, tax, regulatory, or banking-contract decisions. Production use should be validated against the organization's own requirements and source policy.

## Local Development

Backend requires Python 3.11. Frontend requires Node 20.x.

```bash
make install
make dev-backend
make dev-frontend
```

Manual backend setup:

```bash
python3.11 scripts/verify_environment.py
python3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Frontend:

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

The `.env.example` file is a public-safe configuration map. It contains blank placeholders and example defaults, not production secrets.

## Testing

Focused checks:

```bash
pytest tests/regression tests/unit tests/integration -q
```

Full test suite:

```bash
pytest -q
```

Repository verification:

```bash
make verify
```

## Public Documentation

- [API quickstart](docs/API_QUICKSTART.md)
- [API reference](docs/API_REFERENCE_V3.md)
- [Public API boundary](docs/PUBLIC_API_BOUNDARY.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Stability policy](docs/STABILITY.md)
- [Known limitations](docs/KNOWN_LIMITATIONS.md)
- [Data sources and licenses](docs/DATA_SOURCES_AND_LICENSES.md)
- [Future BS research](docs/future_bs/FUTURE_BS_RESEARCH.md)
- [Future BS risk labels](docs/future_bs/RISK_LABELS.md)
- [Future BS source policy](docs/future_bs/SOURCE_POLICY.md)
- [Future BS claim boundary](docs/future_bs/CLAIM_BOUNDARY.md)
- [Future BS reconciliation workflow](docs/future_bs/RECONCILIATION_WORKFLOW.md)
- [SDK roadmap](docs/SDK_ROADMAP.md)

## Claim Boundary

Parva is not an official government calendar publication.

It is not legal, tax, banking-contract, or regulatory final authority. Official publication, legal interpretation, tax treatment, banking-contract finalization, and production financial decisions require the relevant authority or institution's own approval.

## License

Project Parva is licensed under AGPL-3.0-or-later. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This repository uses Swiss Ephemeris through `pyswisseph`. If you run a hosted service based on this repo, publish the corresponding source for the exact deployed build and set `PARVA_SOURCE_URL` accordingly.
