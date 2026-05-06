# Future BS API

Base URL:

```text
https://api.prabinghimire1.com.np
```

## Capabilities

```http
GET /v4/api/future-bs/capabilities
```

Returns engine status, corpus metadata, model registry, precomputed store status, and explicit non-claims.

## Month Lengths

```http
GET /v4/api/future-bs/month-lengths/{bs_year}
GET /v4/api/future-bs/month-lengths/range?start=2084&end=2200
```

Returns 12 month lengths, per-month probability, confidence, model agreement, source status, publication status, and risk flags.

## Explain

```http
GET /v4/api/future-bs/month-lengths/explain?year=2112&month=8
```

Returns month-level reasoning, model outputs, confidence interpretation, and review recommendation.

## Compare External Sheet

```http
POST /v4/api/future-bs/month-lengths/compare
```

Payload:

```json
{
  "source_name": "infodev_excel",
  "years": [
    {
      "bs_year": 2085,
      "months": [31, 32, 31, 32, 31, 31, 30, 30, 29, 30, 30, 30]
    }
  ]
}
```

## Import CSV/XLSX

```http
POST /v4/api/future-bs/month-lengths/import-excel
```

Payload uses base64 content:

```json
{
  "source_name": "infodev_excel",
  "file_format": "csv",
  "content_base64": "..."
}
```

## Backtest

```http
GET /v4/api/future-bs/backtest?mode=holdout&train_start=2040&train_end=2075&test_start=2076&test_end=2083
GET /v4/api/future-bs/backtest?mode=full&test_start=2076&test_end=2083
GET /v4/api/future-bs/backtest?mode=rolling&train_start=2040&test_start=2076&test_end=2083
GET /v4/api/future-bs/backtest/residuals?train_start=2040&train_end=2075&test_start=2076&test_end=2083
```

## Boundary Risk

```http
GET /v4/api/future-bs/boundary-risk?year=2112&month=8
```

Returns low/medium/high/critical/unknown civil assignment risk.

## Export

```http
GET /v4/api/future-bs/export.csv?start=2084&end=2200
GET /v4/api/future-bs/export.xlsx?start=2084&end=2200
```

Aliases under `/month-lengths/export.csv` and `/month-lengths/export.xlsx` are also available.

## Loan Impact

```http
POST /v4/api/future-bs/loan-impact/simulate
```

Supports `actual_365`, `actual_360`, `actual_actual`, `30_360`, `monthly_flat`, and `product_specific`.

## Model Runs

```http
GET /v4/api/future-bs/model-runs
GET /v4/api/future-bs/model-runs/{run_id}
```

Returns immutable run metadata so prediction outputs can be reproduced.
