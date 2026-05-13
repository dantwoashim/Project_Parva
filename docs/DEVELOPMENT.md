# Development

Project Parva is a trust-sensitive calendar infrastructure project. Public development must be reproducible without private source archives, private future-BS artifacts, or local caches.

## Runtime Requirements

- Python 3.11.x
- Node 20.x
- npm 10.x or newer

On Windows, prefer the Python launcher:

```powershell
py -3.11 scripts/verify_environment.py
```

On macOS or Linux:

```bash
python3.11 scripts/verify_environment.py
```

The repository can resolve Node 20 through the local Node binary or the managed `npx node@20` fallback used by the verification scripts.

## Setup

Install backend and Python test dependencies:

```bash
python3.11 -m pip install -e .[test,dev]
```

Install the legacy Python SDK smoke package:

```bash
python3.11 -m pip install -e sdk/python
```

Install the alpha Python SDK package:

```bash
python3.11 -m pip install -e packages/parva-python
```

Install frontend dependencies:

```bash
npm --prefix frontend ci
```

Install JavaScript SDK dependencies:

```bash
npm --prefix packages/parva-js ci
```

If GNU Make is available, `make install` runs the same public setup path.

## Public Verification

The public gate is:

```bash
python3.11 scripts/release/verify_public.py
```

Windows equivalent:

```powershell
py -3.11 scripts/release/verify_public.py
```

Windows wrapper when GNU Make is unavailable:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/release/verify-public.ps1
```

With GNU Make:

```bash
make verify-public
```

The public gate runs:

- environment checks
- repository hygiene
- secret scan
- local path leak scan
- documentation link check
- Render public-demo blueprint check
- documented route inventory check
- backend smoke check
- Python SDK import smoke
- backend lint
- public backend test suite
- alpha Python SDK tests
- frontend lint
- frontend tests
- frontend build
- JavaScript SDK tests

Private source tests are disabled in this public gate.

## Public And Private Data Tiers

| Tier | Public verification behavior |
| --- | --- |
| Public fixtures | Checked in and required for public tests |
| Public generated data | Checked in only when intentionally part of the public artifact |
| Private source archives | Optional, not required for public tests |
| Private research artifacts | Optional, not required for public tests |
| Local caches | Ignored by git and never required for public verification |

Private source archive tests require explicit opt-in:

```bash
PARVA_ENABLE_PRIVATE_SOURCE_TESTS=1 PARVA_SOURCE_ARCHIVE_DIR=data/source_archive python3.11 -m pytest tests/unit/calendar/test_bs_official_range_exhaustive.py
```

If the private archive is enabled but missing, the test fails with the exact missing file path. If it is not enabled, public CI skips that private witness comparison with a clear reason.

Wide corpus or private future-BS research gates should use explicit variables such as:

```text
PARVA_ENABLE_WIDE_CORPUS_TESTS=1
```

Do not add private source archives, full future prediction vectors, or generated research artifacts to public verification.

## Focused Commands

Backend:

```bash
python3.11 -m ruff check backend tests scripts sdk packages/parva-python
python3.11 -m pytest -q
```

Frontend:

```bash
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

SDKs:

```bash
python3.11 scripts/release/check_sdk_install.py
python3.11 -m pytest packages/parva-python/tests -q
npm --prefix packages/parva-js test
```

Docs and release hygiene:

```bash
python3.11 scripts/check_docs_links.py
python3.11 scripts/check_path_leaks.py
python3.11 scripts/security/scan_repo_secrets.py
python3.11 scripts/release/check_repo_hygiene.py
python3.11 scripts/release/measure_public_api_performance.py
```

Layer 2 public API contract:

```bash
python3.11 -m pytest tests/contract/test_layer2_public_api_contract.py -q
python3.11 -m pytest packages/parva-python/tests -q
npm --prefix packages/parva-js test
```

## Route Profiles

The public demo profile is intentionally narrower than a full private deployment.

Recommended public demo environment:

```text
PARVA_ENV=public
PARVA_ROUTE_PROFILE=developer_preview
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_RATE_LIMIT_BACKEND=memory
PARVA_REQUIRE_PRECOMPUTED=false
PARVA_PREWARM_HOTSET=true
```

Production is stricter. If `PARVA_ENV=production`, the backend requires a source URL and Redis-backed rate limiting.

## Frontend API Base

The frontend must use the central API helpers from `frontend/src/services/apiBase.js`.

- Use `apiUrl(path)` for fetch-style endpoint construction.
- Use `apiHref(path)` for links, downloads, and feed URLs.
- Do not hardcode relative `/v3/api/...` anchors in public UI components.

The public Cloudflare Pages environment should set:

```text
VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api
```

## Common Failures

### Python Version Mismatch

If `scripts/verify_environment.py` reports a Python mismatch, use Python 3.11 explicitly:

```bash
python3.11 scripts/release/verify_public.py
```

or on Windows:

```powershell
py -3.11 scripts/release/verify_public.py
```

### Missing Private Source Archive

Public tests should not fail because `data/source_archive/` is missing. Only private opt-in tests should require it.

### Frontend Uses The Wrong API Host

Set:

```text
VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api
```

and ensure backend links in the UI use `apiHref`.

### Render Startup Fails In Production Profile

The public demo should use `PARVA_ENV=public`. The strict `production` profile requires `PARVA_SOURCE_URL`, `PARVA_RATE_LIMIT_BACKEND=redis`, and `PARVA_REDIS_URL`.

## Claim Boundary

Future-BS research outputs remain:

```text
computed_prediction_not_official
```

Public development must not introduce official future-calendar claims, full future vectors, private model runs, or private calibration artifacts.
