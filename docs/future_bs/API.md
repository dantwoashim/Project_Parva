# Future BS API

The future-BS surface is a research and validation layer. It returns computed risk signals, not official future publication.

Base URL:

```text
https://api.prabinghimire1.com.np
```

## Capabilities

```http
GET /v4/api/future-bs/capabilities
```

Returns engine status, corpus metadata, model registry, precomputed-store status, and explicit non-claims.

## Month-Length Research Payload

```http
GET /v4/api/future-bs/month-lengths/{bs_year}
```

Returns month-length assumptions, probability, confidence, source status, publication status, and risk flags for review.

Do not treat this as an official calendar publication. Future payloads are labeled:

```text
computed_prediction_not_official
```

## Explain

```http
GET /v4/api/future-bs/month-lengths/explain?year=2085&month=6
```

Returns month-level reasoning, confidence interpretation, and review recommendation.

## Compare External Sheet

```http
POST /v4/api/future-bs/month-lengths/compare
```

Payload shape:

```json
{
  "source_name": "external_reference_sheet",
  "years": [
    {
      "bs_year": 2085,
      "months": [31, 32, 31, 32, 31, 31, 30, 30, 29, 30, 30, 30]
    }
  ]
}
```

The example values are placeholders for request-shape demonstration. A disagreement means review is recommended, not that the external sheet is automatically wrong.

## Import CSV/XLSX

```http
POST /v4/api/future-bs/month-lengths/import-excel
```

Payload uses base64 content:

```json
{
  "source_name": "external_reference_sheet",
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

Backtests are model-quality signals, not official certification.

## Boundary Risk

```http
GET /v4/api/future-bs/boundary-risk?year=2085&month=6
```

Returns low, medium, high, critical, or unknown civil-assignment risk.

## Loan Or Schedule Impact

```http
POST /v4/api/future-bs/loan-impact/simulate
```

Supports `actual_365`, `actual_360`, `actual_actual`, `30_360`, `monthly_flat`, and `product_specific`.

This estimates how differences between BS month-length assumptions may affect date-sensitive schedules. It is not legal, tax, banking-contract, or official calendar authority.

## Model Runs

```http
GET /v4/api/future-bs/model-runs
GET /v4/api/future-bs/model-runs/{run_id}
```

Returns public run metadata where available. Full future prediction vectors and internal calibration artifacts are not public documentation artifacts.
