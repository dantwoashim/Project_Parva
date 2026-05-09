# Project Parva

Project Parva is an open-source Nepali temporal infrastructure project for Bikram Sambat conversion, fiscal-year logic, panchanga-related computation, festival intelligence, and source-aware calendar validation.

It also includes an experimental future-BS risk research layer for evaluating month-length assumptions before they affect financial, contractual, reporting, or operational systems.

## Technical Thesis

Nepali calendar logic is not just a formatting problem. In real systems, BS dates affect fiscal reports, contract schedules, renewal dates, interest periods, compliance exports, and audit trails.

Parva treats calendar behavior as infrastructure. Every computed result should be explainable, source-aware, reproducible, and honest about its confidence.

## Live API

- API documentation and demo deployment are being migrated.

## What Parva Provides

| Area | Purpose |
| --- | --- |
| Calendar conversion | BS/AD conversion, validation, today endpoints, and month metadata |
| Enterprise date logic | Fiscal-year boundaries, date-range helpers, and business validation |
| Panchanga and lunar logic | Tithi, nakshatra, yoga, karana, lunar phase, and paksha surfaces |
| Festival intelligence | Festival catalog, observance rules, calendar feeds, and explanations |
| Developer API | FastAPI endpoints, OpenAPI docs, examples, and integration-ready responses |
| Future BS risk research | Experimental month-length risk analysis, confidence labels, and validation methodology |
| Provenance and reliability | Source labels, claim boundaries, and reproducible artifacts |

## Current Research Result

In the current Tier 1 official-verified validation window available to Parva, covering 2078-2083 BS, a reference-calibrated solar-civil computational path matched all 72 official month lengths in that window.

A legacy/static baseline matched 68 out of 72 on the same window, with misses concentrated around boundary-sensitive months.

This is a limited validation result. It supports the research direction, but it is not a claim of official authority or broad future-calendar certainty.

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
| Third-party reference | App/site references used for comparison, not authority |
| Needs review | Ambiguous, conflicting, or incomplete evidence |

Only strong official or reviewed printed evidence can support official-grade claims.

## Claim Boundary

Parva is not an official government calendar publication.

Future outputs from the research layer are treated as:

```text
computed_prediction_not_official
```

They are intended for validation, audit, comparison, and risk detection. Official publication, legal interpretation, tax treatment, banking-contract finalization, and production financial decisions require the relevant authority or institution's own approval.

## API Examples

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

The public API intentionally exposes capability and claim-boundary information for the Future BS research layer. Direct future prediction values, export routes, model-run details, residuals, and operational audit tools belong behind private access controls.

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

The `.env.example` file is kept as a local-development map. It contains blank placeholders and example defaults, not production secrets.

## Validation

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
- [Stability policy](docs/STABILITY.md)
- [Known limitations](docs/KNOWN_LIMITATIONS.md)
- [Data sources and licenses](docs/DATA_SOURCES_AND_LICENSES.md)
- [Future BS methodology](docs/future_bs/METHODOLOGY.md)
- [Future BS limitations](docs/future_bs/LIMITATIONS.md)
- [Future BS claims policy](docs/future_bs/CLAIMS_POLICY.md)

## What Parva Is Not

- Not an official government calendar publication.
- Not legal, tax, or banking-contract final authority.
- Not a replacement for an institution's production calendar approval process.
- Not a claim that all historical rows in the corpus have equal source strength.
- Not a blanket claim of future BS month-length certainty.

## License

Project Parva is licensed under AGPL-3.0-or-later. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This repository uses Swiss Ephemeris through `pyswisseph`. If you run a hosted service based on this repo, publish the corresponding source for the exact deployed build and set `PARVA_SOURCE_URL` accordingly.
