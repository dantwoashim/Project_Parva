# Project Parva

Project Parva is an ephemeris-backed Nepali temporal engine and festival
platform. The launch-safe public contract is the stable `v3` read-only
profile under `/v3/api/*`, with `/api/*` kept as a compatibility alias.
The supported runtime target for this build is Python 3.11.
The supported frontend runtime target is Node 20.
If your global `node` is newer, `scripts/verify_environment.py` and the release-candidate gate runner can fall back to a managed `node@20` runtime resolved through `npx`.

## Launch profile

Public stable profile:

- BS and AD conversion
- calendar and panchanga endpoints
- festival explorer APIs
- stateless personal compute endpoints
- feeds
- frontend app and docs

Disabled by default:

- webhook subscription management and dispatch (not shipped in this build)
- experimental version tracks (`/v2`, `/v4`, `/v5`)
- admin and provenance mutation routes

See `docs/AS_BUILT.md`, `docs/ROUTE_ACCESS.md`, and `SECURITY.md` for the
current shipped contract.

## Quick start

### Backend

```bash
py -3.11 scripts/verify_environment.py
py -3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Tested target:

```bash
py -3.11 --version
```

### Frontend

```bash
npm --version
npm --prefix frontend install
npm --prefix frontend run dev
```

Frontend: `http://localhost:5173`
API: `http://localhost:8000/v3/api`

### Python SDK

```bash
py -3.11 -m pip install -e sdk/python
```

```python
from parva_sdk import ParvaClient

client = ParvaClient("http://localhost:8000/v3/api")

today = client.today()
personal = client.personal_panchanga(
    "2026-10-21",
    latitude=27.7172,
    longitude=85.3240,
)
kundali = client.kundali(
    "2026-02-15T06:30:00+05:45",
    latitude=27.7172,
    longitude=85.3240,
)
```

See `sdk/python/README.md` for the current SDK surface.

### API and embeds

- API quickstart: `docs/API_QUICKSTART.md`
- Hosted API onboarding: `docs/HOSTED_API_ONBOARDING.md`
- Institutional embed guide: `docs/EMBED_GUIDE.md`
- Partner access: `docs/PARTNER_ACCESS.md`
- Render zero-budget runbook: `docs/RENDER_ZERO_BUDGET_RUNBOOK.md`
- Usage tiers: `docs/USAGE_TIERS.md`
- Institutional launch checklist: `docs/INSTITUTIONAL_LAUNCH_CHECKLIST.md`

## Release packaging

Use the release packager instead of zipping the working directory. It excludes
virtualenvs, caches, `node_modules`, generated reports, and other local-only
artifacts.

```bash
py -3.11 scripts/release/package_source_archive.py
```

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

## Generated artifacts

Files under `reports/` are generated artifacts, not required committed files.
The policy is documented in `docs/GENERATED_ARTIFACTS.md`.

## Supported runtime matrix

- Python `3.11.x`
- Node `20.x`
- Release archives must be produced from a clean checkout via
  `py -3.11 scripts/release/package_source_archive.py`

## Open-source commercial use

Project Parva now follows the zero-budget AGPL path required by its Swiss
Ephemeris dependency stack. You can still charge for hosting, support,
integration, customization, and white-label operations, but network users must
be able to access the corresponding source for the deployed service.

For hosted deployments:

- keep the project and your deployment changes under AGPL-compatible terms
- publish a public source repository or source archive for the exact deployed build
- set `PARVA_SOURCE_URL` to that public source location
- keep `/source` reachable in production

## Documentation

- `docs/API_REFERENCE_V3.md`
- `docs/API_QUICKSTART.md`
- `docs/HOSTED_API_ONBOARDING.md`
- `docs/PROJECT_BIBLE.md`
- `docs/ROUTE_ACCESS.md`
- `docs/DEPLOYMENT.md`
- `docs/EMBED_GUIDE.md`
- `docs/PARTNER_ACCESS.md`
- `docs/RENDER_ZERO_BUDGET_RUNBOOK.md`
- `docs/USAGE_TIERS.md`
- `docs/INSTITUTIONAL_LAUNCH_CHECKLIST.md`
- `docs/GENERATED_ARTIFACTS.md`
- `docs/EVALUATOR_GUIDE.md`
- `docs/ENGINE_ARCHITECTURE.md`
- `docs/ACCURACY_METHOD.md`
- `docs/KNOWN_LIMITS.md`
- `docs/spec/PARVA_TEMPORAL_SPEC_V1.md`
- `docs/public_beta/month9_release_dossier.md`

## License

This repository's first-party code is released under the GNU Affero General
Public License v3.0 or later. See `LICENSE`.

This is the zero-dollar commercial path for deployments that rely on Swiss
Ephemeris / `pyswisseph`: you may sell services around the software, but
deployed network users must be able to obtain the corresponding source code for
the running service. Review `docs/DEPLOYMENT.md`, `docs/KNOWN_LIMITS.md`, and
`THIRD_PARTY_NOTICES.md` before launch.
