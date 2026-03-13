# Project Parva

Project Parva is an ephemeris-backed Nepali temporal engine and festival
platform. The launch-safe public contract is the stable `v3` read-only
profile under `/v3/api/*`, with `/api/*` kept as a compatibility alias.
The supported runtime target for this build is Python 3.11.

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
py -3.11 -m pip install -e .[test,dev]
set PYTHONPATH=backend
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Tested target:

```bash
py -3.11 --version
```

### Frontend

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

Frontend: `http://localhost:5173`
API: `http://localhost:8000/v3/api`

## Release packaging

Use the release packager instead of zipping the working directory. It excludes
virtualenvs, caches, `node_modules`, generated reports, and other local-only
artifacts.

```bash
py -3.11 scripts/release/package_source_archive.py
```

## Validation

```bash
py -3.11 -m pip install -e .[test,dev]
set PYTHONPATH=backend
py -3.11 scripts/check_path_leaks.py
py -3.11 -m pytest -q
npm --prefix frontend run lint
npm --prefix frontend test -- --run
py -3.11 scripts/release/check_contract_freeze.py
py -3.11 scripts/spec/run_conformance_tests.py
py -3.11 scripts/generate_accuracy_report.py
py -3.11 scripts/generate_authority_dashboard.py
py -3.11 scripts/release/generate_month9_dossier.py
```

## Generated artifacts

Files under `reports/` are generated artifacts, not required committed files.
The policy is documented in `docs/GENERATED_ARTIFACTS.md`.

## Documentation

- `docs/API_REFERENCE_V3.md`
- `docs/PROJECT_BIBLE.md`
- `docs/ROUTE_ACCESS.md`
- `docs/DEPLOYMENT.md`
- `docs/GENERATED_ARTIFACTS.md`
- `docs/EVALUATOR_GUIDE.md`
- `docs/ENGINE_ARCHITECTURE.md`
- `docs/ACCURACY_METHOD.md`
- `docs/KNOWN_LIMITS.md`
- `docs/spec/PARVA_TEMPORAL_SPEC_V1.md`
- `docs/public_beta/month9_release_dossier.md`

## License

This repository is released under the MIT License. See `LICENSE`.
