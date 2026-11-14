# Parva

The Nepali calendar, with its sources.

Parva converts Bikram Sambat and Gregorian dates, exposes recorded holidays, and reviews date files before import. An optional astronomy module calculates festival estimates and panchanga. The web interface and HTTP API use the same Python package.

## Scope

| Capability | Evidence and limits |
| --- | --- |
| BS / AD conversion | Community month table for BS 2000–2095. Matches all 72 months in the preserved BS 2078–2083 reference fixture. Years from 2084 are provisional. |
| Holiday records | Archived annual MoHA notices for BS 2078–2083. Coverage is partial in every year. |
| Source review | BS 2083 records and BS 2082 Dashain/Tihar spans checked against PDF page images. Older rows retain their earlier review state. |
| Working-day review | `true`, `false`, or `null` (unknown). Incomplete evidence never establishes a working day. A Saturday weekend is an explicit policy default. |
| Festival calculations | Astronomical estimates, compared with historical records where available. Historical agreement is not a forecast guarantee. |
| Calendar subscription | Source-reviewed closures only. Observances and unreviewed rows are excluded. |

This is an independent reference, not a government publication or payroll authorization. Undated holidays, later amendments, local decisions and employer rules require separate review. In the current release, ordinary weekdays without a reviewed closure return **unknown**.

## Run locally

Use Python 3.11+ and Node 22.12+ in a fresh environment. The older `parva-python` SDK also uses the `parva` import name; do not install both in one environment.

```sh
cd parva-next
python -m venv .venv
# Activate .venv using your shell's activation command.
python -m pip install -e '.[dev]'
cd web
npm ci
npm run build
cd ..
uvicorn parva.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. API documentation is at `/docs`. For frontend development, run `npm run dev` in `web/`; Vite proxies `/v1` to the API on port 8000.

The base package has no runtime dependencies. Install `.[astro]` for astronomy, `.[api]` for HTTP, or `.[mcp]` for the optional stdio adapter. The web build is separate from the Python wheel. Set `PARVA_WEB_DIST` when serving a build from another location.

```sh
parva convert 2026-04-14
parva convert 2083-01-01 --bs
parva holidays 2083 --scope national
parva check dates.csv --column date --bs
```

CSV review requires UTF-8, a header and explicit calendar selection: Gregorian by default, BS with `--bs` / `?bs=true`. Limits are 1 MiB and 10,000 rows. Scope values are validated; comma-separated scopes form a union with national holidays. `all` is for listing, not a working-day policy.

## Structure

```text
src/parva/
  bs.py, fiscal.py       conversion and fiscal boundaries
  holidays.py           source records and three-state decisions
  review.py, ical.py     CSV review and calendar export
  astro.py, lunar.py,
  festivals.py          optional astronomical calculations
  api.py, cli.py, mcp.py adapters
  data/                 versioned records, source hashes, correction ledger
web/src/                React pages, shared request helper and stylesheet
tests/                  regression tests and preserved reference fixtures
tools/                  data verification and quarantined legacy extraction
docs/                   data review and migration notes
```

There is no database, job queue, plugin framework or separate service layer. Data corrections are explicit JSON changes with source references. HTTP responses use `{data, source, version}`; CSV results carry provenance per row.

## Verify

```sh
python -m ruff check src tests tools
python -m ruff format --check src tests tools
python -m mypy
python -m pytest
python tools/verify_data.py --archive-root ../data/source_archive/moha
python -m build
cd web
npm ci
npm run build
npm audit --omit=dev
```

The data check verifies six archived PDF hashes, row conversions, source metadata, reviewed holiday endpoints, the 72-month reference fixture and every date in the conversion table. These checks establish consistency; they do not turn partial records into a complete holiday calendar. Source-review details are in [the data notes](docs/DATA.md).

`tools/import_legacy.py --output-dir <new-directory>` extracts candidates for review. It cannot overwrite the runtime source tree and rejects incomplete holiday spans. Do not promote OCR output without checking its source page.

## Research and migration

The original research, archived sources and frozen forecast artifacts remain outside this runtime. [Migration notes](docs/MIGRATION.md) identify the boundary. This package does not replace the published legacy API or SDK contracts in place.

Licensed under [AGPL-3.0-or-later](LICENSE), consistent with the repository. Optional dependencies retain their own licenses.
