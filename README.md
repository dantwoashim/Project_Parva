# Project Parva

Project Parva is a Nepal-focused temporal platform. It provides BS/AD conversion, panchanga, festival dates, muhurta windows, kundali endpoints, feeds, and embeddable widgets through a public API and reference app.

The project mixes methods on purpose. BS/AD conversion in the supported official range uses overlap data from official calendars. Panchanga, tithi, muhurta, and other calendrical calculations use Swiss Ephemeris (`pyswisseph`) rather than static festival date tables.

Use `/v3/api/*` for new integrations. `/api/*` still exists as a deprecated compatibility alias on the current hosted deployment.

## Live links

- App: [https://project-parva-uzy1.onrender.com/](https://project-parva-uzy1.onrender.com/)
- API docs: [https://project-parva-uzy1.onrender.com/docs](https://project-parva-uzy1.onrender.com/docs)
- Developer portal: [https://project-parva-uzy1.onrender.com/developers/index.html](https://project-parva-uzy1.onrender.com/developers/index.html)
- Embed examples: [https://project-parva-uzy1.onrender.com/embed/index.html](https://project-parva-uzy1.onrender.com/embed/index.html)

## Who this is for

- Developers building Nepal-focused products
- Media, community, tourism, and institutional websites
- Dashboards and internal tools that need machine-readable Nepali calendar data
- Teams that want embeds without adopting the full app

## What it includes

- BS and AD date conversion
- Calendar, tithi, and panchanga endpoints
- Festival explorer, festival detail, and timeline endpoints
- Personal compute endpoints for location-aware panchanga, muhurta, and kundali
- iCal feeds
- Embed widgets
- Python SDK

Disabled by default:

- Experimental version tracks such as `/v2`, `/v4`, and `/v5`
- Admin and provenance mutation routes

These require `PARVA_ENABLE_EXPERIMENTAL_API=true`.

## Start in 60 seconds

Base URL:

```text
https://project-parva-uzy1.onrender.com/v3/api
```

Check connectivity:

```bash
curl https://project-parva-uzy1.onrender.com/v3/api/calendar/today
```

Convert Gregorian to BS:

```bash
curl "https://project-parva-uzy1.onrender.com/v3/api/calendar/convert?date=2026-10-21"
```

Get upcoming festivals:

```bash
curl "https://project-parva-uzy1.onrender.com/v3/api/festivals/upcoming?days=30&quality_band=computed"
```

For location-sensitive requests, use POST JSON:

```bash
curl -X POST https://project-parva-uzy1.onrender.com/v3/api/personal/panchanga \
  -H "Content-Type: application/json" \
  -H "X-Parva-Envelope: data-meta" \
  -d '{"date":"2026-10-21","lat":"27.7172","lon":"85.3240","tz":"Asia/Kathmandu"}'
```

JavaScript example:

```js
const response = await fetch(
  "https://project-parva-uzy1.onrender.com/v3/api/calendar/convert?date=2026-10-21"
);

const payload = await response.json();
console.log(payload.bikram_sambat.formatted);
```

Python SDK example:

```python
from parva_sdk import ParvaClient

client = ParvaClient("https://project-parva-uzy1.onrender.com/v3/api")

today = client.today()
personal = client.personal_panchanga(
    "2026-10-21",
    latitude=27.7172,
    longitude=85.3240,
    tz="Asia/Kathmandu",
)

print(today.data["gregorian"] if hasattr(today, "data") else today["gregorian"])
print(personal.data["tithi"]["name"])
```

## Integration notes

- Use `/v3/api/*` for all new clients.
- Treat `/api/*` as legacy compatibility only.
- Send `X-Parva-Envelope: data-meta` when you want a stable `data` plus `meta` response shape.
- Preserve `calculation_trace_id`, `method`, `method_profile`, `engine_path`, `support_tier`, `fallback_used`, `calibration_status`, `quality_band`, `assumption_set_id`, `provenance`, and `policy` if you store or forward results.
- Personal compute routes return `Cache-Control: no-store`.
- This is still a public beta. Keep known limitations visible if you present results as authoritative.

## Running locally

Backend requires Python 3.11. Frontend requires Node 20.

### Backend

```bash
py -3.11 scripts/verify_environment.py
py -3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Frontend

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

If your Node version is newer than 20.x:

```bash
npx -y -p node@20 -p npm@10 npm --prefix frontend install
npx -y -p node@20 -p npm@10 npm --prefix frontend run dev
```

Frontend runs at `http://localhost:5173`. The Vite dev server proxies `/v3/api` and `/api` to `http://127.0.0.1:8000` automatically. Override with `PARVA_DEV_API_TARGET` if you need to point elsewhere.

## Python SDK

Install:

```bash
py -3.11 -m pip install -e sdk/python
```

Import:

```python
from parva_sdk import ParvaClient
```

SDK details live in [sdk/python/README.md](sdk/python/README.md).

## Docs

- [docs/API_QUICKSTART.md](docs/API_QUICKSTART.md)
- [docs/API_REFERENCE_V3.md](docs/API_REFERENCE_V3.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [docs/EMBED_GUIDE.md](docs/EMBED_GUIDE.md)
- [docs/ENGINE_ARCHITECTURE.md](docs/ENGINE_ARCHITECTURE.md)
- [docs/SUPPORT_MATRIX.md](docs/SUPPORT_MATRIX.md)
- [docs/ACCURACY_METHOD.md](docs/ACCURACY_METHOD.md)
- [docs/KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md)

## Validation

```bash
py -3.11 scripts/verify_environment.py
py -3.11 -m pip install -e .[test,dev]
py -3.11 -m pip install -e sdk/python
py -3.11 scripts/release/check_repo_hygiene.py
py -3.11 scripts/release/check_render_blueprint.py
py -3.11 scripts/check_path_leaks.py
py -3.11 scripts/validate_festival_catalog.py
py -3.11 scripts/release/check_license_compliance.py
py -3.11 scripts/release/check_sdk_install.py
py -3.11 -m pytest -q
py -3.11 -m ruff check backend tests scripts sdk
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
py -3.11 scripts/release/check_contract_freeze.py
py -3.11 scripts/spec/run_conformance_tests.py
py -3.11 scripts/release/generate_public_beta_artifacts.py --target 300 --computed-target 300
py -3.11 scripts/run_browser_smoke.py
```

## Release packaging

Do not zip the working directory directly. Use the release packager so virtualenvs, caches, `node_modules`, and generated reports stay out of the archive.

Source archive:

```bash
py -3.11 scripts/release/package_source_archive.py
```

Lean submission bundle:

```bash
py -3.11 scripts/release/package_submission_bundle.py
```

Files under `reports/` are generated during validation runs and do not need manual editing.

## License

Project Parva is licensed under AGPL-3.0-or-later. See `LICENSE`.

This deployment path uses Swiss Ephemeris through `pyswisseph`. You can charge for hosting, support, or customization, but anyone using the software over a network must be able to get the corresponding source for what you shipped. Set `PARVA_SOURCE_URL` to a public repo or source archive for the exact deployed build and keep `/source` reachable.

Read [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md), [docs/KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md), and `THIRD_PARTY_NOTICES.md` before going public.
