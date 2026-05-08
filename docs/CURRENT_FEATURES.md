# Current Project Parva Feature Inventory

This inventory preserves the existing Parva platform boundary before additive Future BS and Calendar Model-Risk work.

## API Routes

- Calendar and conversion: `/api/calendar/*`, `/v3/api/calendar/*`, `/api/resolve`, `/api/engine/convert`.
- Enterprise calendar: `/api/enterprise/capabilities`, fiscal year, BS months, business days, bulk conversion, validation.
- Holidays and observances: festival routes, festival timelines, observance streams, forecast routes, iCal feeds, integration feeds.
- Panchanga and personal calendar surfaces: personal panchanga, proof capsules, muhurta, muhurta calendar, muhurta heatmap.
- Kundali and graph surfaces: kundali, lagna, kundali graph endpoints.
- Reliability and trust: provenance, public artifacts, reliability status, metrics, boundary suite, differential manifest, spec conformance.
- Billing and access: plans, checkout, API keys, usage, admin billing surfaces.
- Future BS: `/v4/api/future-bs/*` month-length research payloads, explainability, backtests, residuals, external comparison, loan impact, and model-run metadata.
- Calendar Model-Risk: `/v5/api/calendar-model-risk/*` prediction sets, committee posterior, perturbation robustness, external sheet audit, Calendar VaR, stress test, claim readiness, 2083 Ashwin replay.

## Backend Services

- `calendar_conversion_service`, `calendar_surface_service`, `enterprise_calendar_service`.
- `future_bs_service` for future month-length research payloads, comparison, residuals, and loan impact.
- Panchanga, muhurta, personal, trust, place search, timeline, feed, and kundali services.
- Billing, reliability, provenance, cache, source review, and storage modules.

## Calendar Engines and Data

- BS/AD conversion, known BS month lengths, BS year mapping, fiscal year logic.
- Panchanga/tithi, lunar calendar, sankranti, graha, muhurta, kundali, Nepal Sambat.
- Swiss Ephemeris-backed astronomy with optional JPL DE440/DE441 local kernels.
- Festival rules, source files, provenance files, overrides, and precomputed artifacts.

## Future BS and Model-Risk Assets

- Source-labeled corpus: `data/future_bs/corpus/verified_month_lengths.csv`.
- Source registry under `data/future_bs/corpus`.
- Generated model runs, prediction artifacts, calibration metadata, and residual reports are local artifacts and are not public source fixtures.
- Strict claim posture: future outputs are `computed_prediction_not_official`.

## Frontend

- React/Vite frontend with landing, consumer home, festival explorer/detail, methodology, panchanga, personal panchanga, muhurta, kundali, temporal compass, time lab, truth lab, profile, saved, and feed subscription pages.
- Frontend service clients and contract tests for API usage.
- Built static assets under `frontend/dist`.

## SDK

- Python SDK package under `sdk/python/parva_sdk` with client, models, and exceptions.
- Compatibility import package under `sdk/python/parva`.

## Scripts and Deployment

- Verification, golden journey, browser smoke, frontend accessibility, docs link, path leak, security, signing, and live smoke scripts.
- Future BS scripts for public validation, backtesting, comparison, residual reporting, and JPL kernel download.
- Docker, Cloud Run, Render, Cloud Build, release, governance, and precompute support files.

## Tests

- Unit tests for calendar, services, future BS, reliability, cache, billing, panchanga, muhurta, kundali, and routes.
- Integration tests for calendar, proof capsules, places, future BS, model-risk, and API surfaces.
- Accuracy tests for future BS holdout, green zone, performance, model regression, immutability, and year-total gates.
- Frontend tests under `frontend/src/test`.
