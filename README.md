# Project Parva

**Nepali temporal infrastructure for Bikram Sambat, fiscal logic, panchanga computation, festivals, developer APIs, and future BS month-length risk analysis.**

Every serious Nepali software system eventually becomes a calendar system.

A date in Nepal can decide a fiscal year, a loan schedule, an interest period, a payroll cycle, a festival feed, a contract boundary, an audit export, or a public-facing statement line. Project Parva treats those dates as infrastructure rather than display text.

Parva brings together deterministic BS/AD conversion, fiscal-year rules, panchanga and tithi computation, festival data, public APIs, source-aware validation, and a research-grade future BS risk layer for systems that need evidence before they trust a calendar assumption.

---

## Live API

- API documentation: <https://api.prabinghimire1.com.np/docs>
- OpenAPI schema: <https://api.prabinghimire1.com.np/openapi.json>
- Future-BS capability summary: <https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities>

---

## What Parva Is Built To Do

Project Parva is designed for Nepali products where calendar logic affects real operations.

It supports:

| Area | Purpose |
| --- | --- |
| BS/AD conversion | Convert between Bikram Sambat and Gregorian dates with validation and structured responses. |
| Fiscal-year logic | Resolve Nepali fiscal years, fiscal boundaries, BS month ranges, and reporting periods. |
| Panchanga computation | Provide tithi, nakshatra, yoga, karana, vaara, lunar phase, and related calendar signals. |
| Sankranti and solar logic | Support solar-ingress aware calendar computation and future BS research. |
| Festivals and observances | Serve structured festival, observance, rule, location, and feed data. |
| Muhurta and timing | Provide auspicious-window and timing-related API surfaces. |
| Kundali foundations | Expose horoscope and chart computation surfaces for astrology-facing products. |
| Developer APIs | Offer public API routes, OpenAPI schema, examples, and integration-ready responses. |
| Future BS risk analysis | Evaluate future BS month-length assumptions, source strength, model disagreement, and operational risk. |
| Provenance and validation | Track source labels, reproducibility, model runs, benchmark limits, and claim boundaries. |

---

## Why This Project Exists

Most calendar libraries answer a narrow question:

> What is the converted date?

Parva answers a broader engineering question:

> Can this date logic be trusted inside a real Nepali product?

That difference matters.

A payroll system needs valid month boundaries.  
A loan system needs safe day counts.  
A reporting system needs the correct fiscal year.  
A festival product needs rule-aware observance data.  
A financial platform needs a way to detect calendar assumptions that become fragile before official publication catches up.

Parva is built around that reality.

---

## Main API Surfaces

| Surface | Status | Role |
| --- | --- | --- |
| `/v3/api/*` | Stable public API | BS/AD conversion, calendar helpers, panchanga, festivals, feeds, widgets, billing, and developer access. |
| `/v4/api/future-bs/*` | Research and evaluation layer | Future BS month-length risk analysis, validation, backtesting, source-aware comparison, and operational impact checks. |
| `/api/*` | Compatibility layer | Older route aliases for existing integrations. |
| Frontend | Reference interface | Public-facing pages, demos, and developer discovery surfaces. |

---

## Future BS Month-Length Risk Layer

Future BS month lengths create a special problem.

Many systems can store a table. Far fewer systems can explain where that table becomes fragile.

Parva’s Future BS layer studies month-start behavior, solar-civil patterns, source strength, boundary-sensitive months, and disagreement between computational and legacy assumptions. The goal is risk detection, audit support, and controlled validation for future-dated systems.

A simplified flow looks like this:

```text
BS year
  -> predicted month starts
  -> derived month lengths
  -> source and model evidence
  -> confidence and risk labels
  -> disagreement report
  -> operational impact
```

This layer is designed for teams that already maintain internal future BS month-length sheets and need an independent computational reference.

It can support:

- BS year month-length evaluation
- source-aware confidence reporting
- model disagreement detection
- boundary-sensitive month flagging
- external sheet comparison
- holdout, rolling, and replay backtests
- year-total consistency checks
- reproducible model-run artifacts
- loan, interest, contract, and schedule impact analysis
- blinded audit workflows where aggregate risk is shared before corrected values

Official Nepali publications remain the final authority for official dates. Parva’s future layer is an engineering and audit system for pre-publication risk, internal validation, and model-risk review.

---

## Current Research Result

The strongest current Future BS result is a recent official-window validation.

Across the current Tier 1 official-verified validation window available to Parva, covering **2078-2083 BS**, the reference-calibrated solar-civil computational path matched **72 of 72 official month lengths**.

On the same window, a legacy/static baseline matched **68 of 72**.

The legacy/static misses were concentrated around boundary-sensitive months:

- 2082 Ashadh
- 2082 Shrawan
- 2083 Bhadra
- 2083 Ashwin

This result supports the central thesis behind Parva’s Future BS layer: static or cycle-style assumptions can look stable for long periods and still fail around month-start boundary cases.

This benchmark is a limited official-window result. It is useful evidence for audit design, model-risk testing, and future-BS validation workflows. Broader public accuracy claims require a larger official and printed-source validation set.

---

## Source Policy

Parva treats source quality as part of the data model.

Calendar data from different origins carries different authority. A government notice, a printed panchanga, a newspaper masthead, a public calendar site, a software lookup table, and a third-party app table belong in different evidence layers.

The Future BS research layer uses source policies such as:

| Policy | Use |
| --- | --- |
| `official_strict` | Official-verified and strongly reviewed printed evidence for official-grade validation. |
| `medium_high_training` | Higher-trust sources used for calibration and development, reported separately. |
| `all_witness_experimental` | Broad witness evidence for weak-signal discovery, anomaly detection, and active learning. |
| `market_shadow_experimental` | Market-table comparison, especially for public or third-party calendar behavior. |

This separation keeps technical research, public behavior, and official claim-readiness from being mixed into one misleading number.

---

## Public Claim Boundary

Parva is built to be useful before it becomes flashy.

The current public position is:

- published/current BS/AD conversion APIs can be used for normal integration
- fiscal-year and calendar validation APIs can support business workflows
- panchanga, festival, feed, and timing surfaces can support calendar products
- Future BS outputs belong in validation, audit, and risk-review workflows
- GREEN/YELLOW/RED risk labeling is the preferred direction for future month-length claims
- official-grade future accuracy claims require stronger official and printed validation coverage

The most important target for Future BS research is selective reliability:

```text
High confidence only when the evidence supports high confidence.
```

The long-term goal is **99%+ accuracy on GREEN predictions with zero wrong-GREEN cases**, rather than a broad top-line number across every source and every month.

---

## Quick API Examples

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

Future-BS capabilities:

```bash
curl https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Future-BS month explanation:

```bash
curl "https://api.prabinghimire1.com.np/v4/api/future-bs/month-lengths/explain?year=2083&month=6"
```

Backtest summary:

```bash
curl "https://api.prabinghimire1.com.np/v4/api/future-bs/backtest?mode=holdout&train_start=2070&train_end=2077&test_start=2078&test_end=2083"
```

---

## Repository Structure

```text
backend/
  app/
    calendar/
    future_bs/
    festivals/
    panchanga/
    muhurta/
    kundali/
    feeds/
    reliability/

frontend/
  src/

data/
  festivals/
  future_bs/
  ephemeris/

docs/
  future_bs/
  enterprise/
  API_REFERENCE_V3.md
  API_QUICKSTART.md

scripts/
  future_bs/
  precompute/
  validation/

tests/
  unit/
  integration/
```

The repository includes backend services, frontend pages, data artifacts, validation scripts, future-BS research tooling, documentation, and test coverage.

---

## Local Development

Backend requires Python 3.11.  
Frontend requires Node 20.x.

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

Frontend setup:

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

---

## Validation

Focused Future BS tests:

```bash
PYTHONPATH=backend pytest tests/integration/test_future_bs_routes.py tests/unit/future_bs -q
```

Full backend test suite:

```bash
PYTHONPATH=backend pytest -q
```

Repository verification:

```bash
make verify
make preflight-production
```

Future BS claim-boundary checks:

```bash
python scripts/audit_verified_corpus.py

python scripts/backtest_future_bs_model.py \
  --validation-mode source_strict_official_only \
  --train-start 2000 \
  --train-end 2077 \
  --test-start 2078 \
  --test-end 2083
```

---

## Key Documentation

- [Future BS Methodology](docs/future_bs/METHODOLOGY.md)
- [Future BS Limitations](docs/future_bs/LIMITATIONS.md)
- [Future BS API](docs/future_bs/API.md)
- [Confidence Model](docs/future_bs/CONFIDENCE_MODEL.md)
- [Loan Impact](docs/future_bs/LOAN_IMPACT.md)
- [Validation Report Template](docs/future_bs/VALIDATION_REPORT_TEMPLATE.md)
- [Enterprise Validation](docs/enterprise/README_VALIDATION.md)
- [API Quickstart](docs/API_QUICKSTART.md)
- [API Reference V3](docs/API_REFERENCE_V3.md)
- [Stability](docs/STABILITY.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)
- [Data Sources and Licenses](docs/DATA_SOURCES_AND_LICENSES.md)
- [Cloud Run Deployment](docs/DEPLOY_CLOUD_RUN.md)

---

## Commercial and Enterprise Use

Parva is most useful when a team needs an independent calendar layer for:

- BS/AD conversion validation
- fiscal-year reporting checks
- date-boundary regression tests
- future BS month-length risk review
- external sheet comparison
- loan and interest schedule impact analysis
- private deployment or internal validation workflows

For production use in regulated, financial, legal, or contract-sensitive contexts, teams should pair Parva with their own official-source review and internal approval process.

---

## License

Project Parva is licensed under **AGPL-3.0-or-later**. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This repository uses Swiss Ephemeris through `pyswisseph`. Hosted services based on this repository should publish the corresponding source for the deployed build and set `PARVA_SOURCE_URL` accordingly.
