---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-04
owner: research-team
---

# Future BS Public API

Project Parva publishes a curated, read-only Future BS research snapshot. Every response carries `computed_prediction_not_official`, requires human review, and yields to a later authoritative calendar publication.

## Public Endpoints

```http
GET /v4/api/future-bs/capabilities
GET /v4/api/future-bs/methodology
GET /v4/api/future-bs/forecast/{bs_year}
```

The tracked snapshot currently covers `2084-2200 BS`.

```bash
curl "https://api.prabinghimire1.com.np/v4/api/future-bs/forecast/2084"
```

The year response includes:

- twelve predicted month lengths and the year total
- 80% and 95% model prediction sets for each month
- model probabilities and agreement counts
- Nepal civil-boundary distance in minutes
- GREEN, YELLOW, or RED review labels and risk flags
- selected model and calibration versions
- validation scope, source metadata, warnings, and claim boundary

The methodology endpoint publishes the selected pipeline, civil cutoff rules, sequence constraints, risk policy, and validation interpretation.

## Validation Meaning

The selected method matches all `72/72` month cases in the official `2078-2083 BS` calibration window. This result is a calibrated replay. Independent broad accuracy remains below the project's evidence threshold of 528 verified month cases. The API exposes both facts in the `validation` object.

## Controlled Research Routes

The following workflows remain available only in controlled research profiles:

- bulk and range forecasts
- CSV and XLSX exports
- source-sheet imports and comparisons
- backtests, residuals, and model-run registries
- raw explanation and boundary-risk payloads
- financial and schedule-impact simulations
- private source material and calibration artifacts

These routes require a research profile, experimental and research flags, and operator authentication. Public OpenAPI contains only the three curated routes above.

## Source Artifacts

- Forecast snapshot: `data/future_bs/public/forecast_snapshot_v6_2084_2200.json`
- Selected methodology: `data/future_bs/public/selected_model_v6.json`
- Snapshot promotion builder: `scripts/future_bs/build_public_forecast_snapshot.py` (requires the controlled source run artifacts)
