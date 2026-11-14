# Focused runtime and preserved research

The focused package starts from repository commit `ca38c5f184d0b25eff2e36683624a16cfcc9f383`. Existing root backend, frontend, published SDKs, source archive and research artifacts are retained. Their deployed behavior is not changed by adding this directory.

The new runtime has one installable Python package and one web interface. Conversion and holiday decisions need no third-party runtime packages. Astronomy and HTTP are optional installation extras. No research pipeline executes inside a request.

## Compatibility boundary

This is a separate candidate, not an in-place replacement for `/v3/api` or the published `parva-python` and `@project-parva/parva-js` SDKs. Use a separate virtual environment and deployment. Existing consumers need an explicit migration before the old routes can be retired.

In particular, the legacy payroll-safety decision should not be used as evidence of calendar completeness. The focused API instead returns `working: null` and `status: "unknown"` when holiday evidence is incomplete. Source labels and fingerprints identify inputs; they do not prove that those inputs are correct.

The focused `/v1/sources` response groups `sources`, `release` and `data_sha256` separately. CSV reviews return `source: "per-row"`; each row identifies its own source and coverage. The frontend implements these contracts directly.

## Research preservation

The root `backend/app/research/`, `docs/future_bs/`, `data/`, `tests/fixtures/` and forecast-related scripts remain the historical record. Frozen corpora, forecasts, metrics and archived PDFs are not rewritten to fit runtime corrections. The local prospective-forecasting manuscript is preserved alongside the existing future-BS documentation.

Calendar corrections live only under `parva-next/src/parva/data/`, with a correction ledger and source-page references. They do not silently modify research fixtures or historical benchmark outputs. Retrospective fit and prospective validation remain different claims.

## Deliberate limits

This change adds no payment system, user accounts, database, generic workflow engine or replacement SDK family. Existing consumers and actual adoption should determine subsequent work. Complete holiday coverage requires ongoing source maintenance; code cleanup cannot substitute for that evidence.
