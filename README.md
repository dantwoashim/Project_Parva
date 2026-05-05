# Project Parva

Project Parva is a Nepal-focused temporal platform and public reference implementation. It exposes BS/AD conversion, panchanga, festival dates, muhurta windows, kundali endpoints, feeds, embeddable widgets, a Python SDK, and a reference frontend backed by a FastAPI service.

The core product posture is intentionally mixed but explicit:

- BS/AD conversion uses official overlap data inside the supported range, with bounded fallback behavior outside that range.
- Panchanga, tithi, muhurta, kundali, and other astronomical calculations use Swiss Ephemeris through `pyswisseph`.
- Festival outputs combine computation, curated source inventories, and public trust metadata rather than pretending every answer is equally authoritative.

Use `/v3/api/*` for new integrations. `/api/*` is a legacy compatibility alias. `/v2`, `/v4`, and `/v5` are experimental aliases disabled by default and are not independent long-term API contracts.

## Status

| Surface | Status | Notes |
| --- | --- | --- |
| `/v3/api/*` public API | Stable public contract | Canonical integration surface for new clients. |
| Python SDK | Stable public-beta | Built and validated from package artifacts. |
| Reference frontend | Beta | Actively maintained, but still a reference app rather than a finished consumer product. |
| Feeds and widgets | Beta | Publicly usable, but still evolving operationally and editorially. |
| `/api/*` | Legacy compatibility | Supported for existing clients only. |
| `/v2`, `/v4`, `/v5` | Experimental | Disabled by default and not version-isolated. |
| Labs / PoCs / ops helpers | Experimental or unsupported | Not part of the public compatibility guarantee. |

See [docs/STABILITY.md](docs/STABILITY.md), [docs/ROUTE_ACCESS.md](docs/ROUTE_ACCESS.md), and [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) before presenting Parva as authoritative.

The backend platform and the frontend should be understood separately:

- the canonical production commitment is the `/v3/api/*` platform
- the frontend is a public reference beta unless explicitly productized further

## Live links

- App: [https://project-parva-uzy1.onrender.com/](https://project-parva-uzy1.onrender.com/)
- API docs: [https://project-parva-uzy1.onrender.com/docs](https://project-parva-uzy1.onrender.com/docs)
- Developer portal: [https://project-parva-uzy1.onrender.com/developers/index.html](https://project-parva-uzy1.onrender.com/developers/index.html)
- Embed examples: [https://project-parva-uzy1.onrender.com/embed/index.html](https://project-parva-uzy1.onrender.com/embed/index.html)

## Recommended hosted split

For the next production migration, the repository is prepared for:

- Cloudflare Pages for the static frontend
- Google Cloud Run for the Python API
- Upstash Redis for distributed rate limiting and lightweight cache state

That split keeps the backend stateless, preserves the `/v3/api/*` contract, and avoids serving the Vite frontend from the Python container when a static host is available.

## What this repo includes

- FastAPI backend under `backend/`
- React/Vite reference frontend under `frontend/`
- Public docs under `docs/`
- Release, hygiene, and validation scripts under `scripts/`
- Python SDK under `sdk/python/`
- Data, source inventories, and public artifacts under `data/` and `backend/data/`
- Tests under `tests/` and `backend/tests/`

## What this repo does not promise

- It is not an official government calendar publication.
- It is not a universal doctrinal authority across all Nepali traditions or observance profiles.
- It does not ship a production account/sync platform today.
- It does not guarantee that every historical or regional festival entry is equally source-validated.
- It does not treat experimental aliases or lab surfaces as stable product commitments.

## Quick start

Backend requires Python 3.11. Frontend requires Node 20.x.

### Recommended

```bash
make install
make dev-backend
make dev-frontend
```

For product/design review with the built frontend and API on one origin:

```bash
make build-frontend
make dev-local
```

Then open `http://127.0.0.1:8000/today`. This mode sets `PARVA_SERVE_FRONTEND=true` so deep links and `/v3/api` calls work from the same FastAPI server.

If your default `npm` is not backed by Node 20, override the frontend command:

```bash
make NPM="npx -y -p node@20 -p npm@10 npm" install-frontend
make NPM="npx -y -p node@20 -p npm@10 npm" dev-frontend
```

### Manual backend setup

```bash
python3.11 scripts/verify_environment.py
python3.11 -m pip install -e .[test,dev]
python3.11 -m pip install -e sdk/python
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Manual frontend setup

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

Frontend runs at `http://localhost:5173`. The Vite dev server proxies `/v3/api` and `/api` to `http://127.0.0.1:8000` by default. Override with `PARVA_DEV_API_TARGET` when needed.

## Validate before opening a PR

```bash
make verify
make preflight-production
```

That runs environment checks, repo hygiene, secret scanning, route/doc parity, backend smoke, SDK install validation, Python tests/lint, frontend lint/test/build, and a production-style deployment preflight.

## API examples

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

Location-sensitive request:

```bash
curl -X POST https://project-parva-uzy1.onrender.com/v3/api/personal/panchanga \
  -H "Content-Type: application/json" \
  -H "X-Parva-Envelope: data-meta" \
  -d '{"date":"2026-10-21","lat":"27.7172","lon":"85.3240","tz":"Asia/Kathmandu"}'
```

Paid-key request:

```bash
curl "https://project-parva-uzy1.onrender.com/v3/api/calendar/today" \
  -H "X-API-Key: parva_live_your_key_here"
```

Request paid access manually:

```bash
curl -X POST https://project-parva-uzy1.onrender.com/v3/api/billing/checkout \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"Your Name","tier":"starter","provider":"manual_bank_qr"}'
```

Current paid activation is manual-first. Use `manual_bank_qr`, `manual_esewa_qr`, `manual_khalti_qr`, or `manual_contact` for Nepali customers and `payoneer` for international customers. Khalti/eSewa API checkout is intentionally not presented until merchant registration and company PAN requirements are ready.

Python SDK example:

```python
from parva_sdk import ParvaClient

client = ParvaClient("https://project-parva-uzy1.onrender.com/v3/api")
today = client.today()
print(today.data["gregorian"] if hasattr(today, "data") else today["gregorian"])
```

## Integration notes

- Use `/v3/api/*` for all new integrations.
- Treat `/api/*` as legacy compatibility only.
- Route access is summarized at `/v3/api/policy` and documented in [docs/ROUTE_ACCESS.md](docs/ROUTE_ACCESS.md).
- The free tier works without an API key up to the public quota. Paid API keys unlock higher monthly quotas after manual payment confirmation.
- Send `X-Parva-Envelope: data-meta` when you want stable `data` plus `meta` response envelopes.
- Preserve trust metadata such as `method`, `engine_path`, `support_tier`, `quality_band`, and `provenance` if you store or forward results.

## Key docs

- [docs/API_QUICKSTART.md](docs/API_QUICKSTART.md)
- [docs/API_REFERENCE_V3.md](docs/API_REFERENCE_V3.md)
- [docs/API_LIFECYCLE.md](docs/API_LIFECYCLE.md)
- [docs/STABILITY.md](docs/STABILITY.md)
- [docs/ROUTE_ACCESS.md](docs/ROUTE_ACCESS.md)
- [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)
- [docs/enterprise/README_VALIDATION.md](docs/enterprise/README_VALIDATION.md)
- [docs/enterprise/INFODEVELOPERS_MEETING_PACK.md](docs/enterprise/INFODEVELOPERS_MEETING_PACK.md)
- [docs/SUPPORT_MATRIX.md](docs/SUPPORT_MATRIX.md)
- [docs/SELF_HOSTING.md](docs/SELF_HOSTING.md)
- [docs/DEPLOY_CLOUDFLARE_PAGES.md](docs/DEPLOY_CLOUDFLARE_PAGES.md)
- [docs/DEPLOY_CLOUD_RUN.md](docs/DEPLOY_CLOUD_RUN.md)
- [docs/DEPLOY_UPSTASH.md](docs/DEPLOY_UPSTASH.md)
- [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md)
- [docs/DATA_SOURCES_AND_LICENSES.md](docs/DATA_SOURCES_AND_LICENSES.md)
- [docs/runbooks/redis-outage.md](docs/runbooks/redis-outage.md)
- [sdk/python/README.md](sdk/python/README.md)

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. Changes that affect dates, festival rules, or trust claims need evidence and a brief impact summary, not just code.

## License

Project Parva is licensed under AGPL-3.0-or-later. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This repository uses Swiss Ephemeris through `pyswisseph`. If you run a hosted service based on this repo, publish the corresponding source for the exact deployed build and set `PARVA_SOURCE_URL` accordingly.
