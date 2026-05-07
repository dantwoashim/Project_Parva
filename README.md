# Project Parva

Project Parva is a Nepali calendar computation API with a dedicated future-BS month-length risk engine for financial-system evaluation.

The strongest product surface in this repository is now:

```text
BS year -> 12 month lengths -> confidence -> mismatch report -> loan impact
```

Parva does **not** claim to be the official future Nepali calendar. It provides a computational validation layer: source-labeled historical corpus, solar-ingress calibrated prediction, external Excel comparison, confidence/risk flags, immutable prediction runs, exports, and loan/interest impact analysis.

## Live API

- API docs: [https://api.prabinghimire1.com.np/docs](https://api.prabinghimire1.com.np/docs)
- OpenAPI JSON: [https://api.prabinghimire1.com.np/openapi.json](https://api.prabinghimire1.com.np/openapi.json)
- Future-BS capabilities: [https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities](https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities)

## Main Surfaces

| Surface | Status | Purpose |
| --- | --- | --- |
| `/v4/api/future-bs/*` | Evaluation-ready | Future BS month-length prediction, Excel comparison, backtesting, exports, and loan-risk simulation. |
| `/v3/api/*` | Stable public API | BS/AD conversion, panchanga, festivals, muhurta, kundali, feeds, widgets, billing, and developer API access. |
| `/api/*` | Legacy compatibility | Older route alias for existing integrations. |
| Frontend | Reference beta | Public interface and developer pages, not the primary enterprise contract surface. |

## Future-BS Risk Engine

The future-BS engine is designed for companies that already have internal BS month-length sheets and need a second computational reference.

It can:

- predict BS month lengths through the configured future range
- return probability and confidence for each month
- flag model disagreement and near-boundary civil-date risk
- compare Parva predictions against external Excel/CSV sheets
- export CSV/XLSX prediction files
- run holdout, full-replay, and rolling backtests
- simulate loan and interest impact when month lengths differ
- preserve immutable model-run metadata for reproducibility

Important limits:

- Future outputs are `not_official_publication`.
- Cloud Run builds download and verify NASA NAIF `de440.bsp`, then expose it through `PARVA_JPL_DE440_KERNEL`. Swiss/Moshier remains the fallback path if the kernel is not present.
- Source labels matter. Third-party or legacy static rows are not represented as official ground truth.

## Future-BS API Examples

Base URL:

```text
https://api.prabinghimire1.com.np
```

Capabilities:

```bash
curl https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Predict one BS year:

```bash
curl https://api.prabinghimire1.com.np/v4/api/future-bs/month-lengths/2112
```

Explain one month:

```bash
curl "https://api.prabinghimire1.com.np/v4/api/future-bs/month-lengths/explain?year=2112&month=8"
```

Compare an external sheet:

```bash
curl -X POST https://api.prabinghimire1.com.np/v4/api/future-bs/month-lengths/compare \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "infodev_excel",
    "years": [
      {
        "bs_year": 2085,
        "months": [31, 32, 31, 32, 31, 31, 30, 30, 29, 30, 30, 30]
      }
    ]
  }'
```

Backtest:

```bash
curl "https://api.prabinghimire1.com.np/v4/api/future-bs/backtest?mode=holdout&train_start=2040&train_end=2075&test_start=2076&test_end=2083"
```

Export:

```bash
curl -L "https://api.prabinghimire1.com.np/v4/api/future-bs/export.csv?start=2084&end=2200" \
  -o parva_future_bs_2084_2200.csv
```

Loan impact:

```bash
curl -X POST https://api.prabinghimire1.com.np/v4/api/future-bs/loan-impact/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "loan_start_bs": "2085-05-01",
    "term_months": 240,
    "principal": 1000000,
    "annual_rate": 12,
    "day_count_method": "actual_365",
    "external_years": [
      {
        "bs_year": 2085,
        "months": [31, 32, 31, 32, 31, 31, 30, 30, 29, 30, 30, 30]
      }
    ]
  }'
```

## Corpus and Data Policy

Future-BS calibration data lives in:

- `data/future_bs/corpus/verified_month_lengths.csv`
- `data/future_bs/corpus/source_registry.json`
- `data/future_bs/corpus/verification_notes.md`

Every row has a source label:

- `official_verified`
- `approved_patro`
- `physical_patro_verified`
- `internal_reference`
- `third_party_reference`
- `needs_review`

The current corpus is intentionally conservative. Rows that come from legacy static lookup or third-party references are labeled as review material, not official financial-contract authority.

Precomputed prediction artifacts live in:

- `data/future_bs/predictions/`
- `data/future_bs/model_runs/`

Regenerate them with:

```bash
PYTHONPATH=backend python scripts/precompute_future_bs_predictions.py \
  --start 2084 \
  --end 2200 \
  --model parva_solar_civil_accuracy_v4
```

Local JPL setup:

```bash
python scripts/download_jpl_kernel.py --output data/ephemeris/jpl/de440.bsp
export PARVA_JPL_DE440_KERNEL="$PWD/data/ephemeris/jpl/de440.bsp"
python scripts/precompute_solar_ingress_events.py \
  --start 1843 \
  --end 2144 \
  --ephemeris jpl_de440 \
  --output data/future_bs/astronomy/solar_ingress_events_1900_2200.json \
  --parquet-output data/future_bs/astronomy/solar_ingress_events_1900_2200.parquet
```

Accuracy claim boundary:

```bash
python scripts/audit_verified_corpus.py
python scripts/backtest_future_bs_model.py \
  --validation-mode source_strict_official_only \
  --train-start 2000 \
  --train-end 2077 \
  --test-start 2078 \
  --test-end 2083
```

Parva tracks month-level `overall_top1_accuracy`, `green_zone_accuracy`,
`green_zone_coverage`, and `boundary_case_accuracy`. A 99%+ claim is blocked
until the source-strict official/printed benchmark has enough verified month
cases and the green-zone thresholds pass.

## General Calendar API

Use `/v3/api/*` for public integrations.

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

Paid API access is manual-first until company/merchant registration is ready for automated Khalti/eSewa checkout. Supported request paths include manual QR/contact options for Nepal and Payoneer invoice flow for international customers.

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

## Validation

Focused future-BS tests:

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

## Key Docs

- [docs/future_bs/METHODOLOGY.md](docs/future_bs/METHODOLOGY.md)
- [docs/future_bs/LIMITATIONS.md](docs/future_bs/LIMITATIONS.md)
- [docs/future_bs/API.md](docs/future_bs/API.md)
- [docs/future_bs/CONFIDENCE_MODEL.md](docs/future_bs/CONFIDENCE_MODEL.md)
- [docs/future_bs/LOAN_IMPACT.md](docs/future_bs/LOAN_IMPACT.md)
- [docs/future_bs/VALIDATION_REPORT_TEMPLATE.md](docs/future_bs/VALIDATION_REPORT_TEMPLATE.md)
- [docs/enterprise/INFODEVELOPERS_MEETING_PACK.md](docs/enterprise/INFODEVELOPERS_MEETING_PACK.md)
- [docs/enterprise/README_VALIDATION.md](docs/enterprise/README_VALIDATION.md)
- [docs/API_QUICKSTART.md](docs/API_QUICKSTART.md)
- [docs/API_REFERENCE_V3.md](docs/API_REFERENCE_V3.md)
- [docs/STABILITY.md](docs/STABILITY.md)
- [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)
- [docs/DATA_SOURCES_AND_LICENSES.md](docs/DATA_SOURCES_AND_LICENSES.md)
- [docs/DEPLOY_CLOUD_RUN.md](docs/DEPLOY_CLOUD_RUN.md)

## What Parva Is Not

- Not an official government calendar publication.
- Not legal, tax, or banking-contract final authority.
- Not a replacement for a client’s internal production calendar without validation.
- Not a claim that all historical rows in the corpus have equal source strength.

## License

Project Parva is licensed under AGPL-3.0-or-later. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This repository uses Swiss Ephemeris through `pyswisseph`. If you run a hosted service based on this repo, publish the corresponding source for the exact deployed build and set `PARVA_SOURCE_URL` accordingly.
