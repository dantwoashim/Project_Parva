# Phase 3 SDK and CLI Alpha Audit

## Phase Goal

Phase 3 adds public-safe SDK and CLI alpha surfaces so Project Parva can be used without relying only on the hosted API.

The phase created:

- a JavaScript and TypeScript SDK alpha
- a Python SDK alpha
- a Python CLI alpha
- public SDK usage documentation
- SDK smoke tests

The new SDK surfaces use stable public calendar endpoints and the public future-BS capabilities summary only.

## Packages Created

### JavaScript and TypeScript

Created under `packages/parva-js/`:

- `package.json`
- `package-lock.json`
- `tsconfig.json`
- `src/index.ts`
- `packages/parva-js/tests/client.test.mjs`
- `README.md`

Exports:

- `ParvaClient`
- `bsToAd`
- `adToBs`
- `getToday`
- `validateBsDate`
- `getFutureBsCapabilities`

### Python

Created under `packages/parva-python/`:

- `pyproject.toml`
- `parva/__init__.py`
- `parva/client.py`
- `packages/parva-python/tests/test_client.py`
- `README.md`

Exports:

- `ParvaClient`
- `bs_to_ad`
- `ad_to_bs`
- `get_today`
- `validate_bs_date`
- `get_future_bs_capabilities`

### CLI

Created under `tools/parva-cli/`:

- `parva_cli.py`
- `README.md`

Supported commands:

- `parva today`
- `parva convert ad 2026-04-14`
- `parva convert bs 2083-01-01`
- `parva validate bs 2083-01-32`
- `parva capabilities future-bs`

Repository command form:

```bash
python tools/parva-cli/parva_cli.py --help
```

## Documentation Added

- `docs/SDK_USAGE.md` was added with JS, Python, and CLI usage.

No private future-BS implementation files were changed.

## Endpoint Review

The SDKs call only these public-safe surfaces:

- `GET /calendar/today`
- `GET /calendar/convert`
- `POST /calendar/bs-to-gregorian`
- `GET https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities`

The SDKs do not call private future-BS month-length prediction, export, model-run, backtest, residual, external comparison, corrected-value, or schedule-impact endpoints.

## Quality Checks Performed

- Verified JS package install succeeds.
- Verified JS tests pass.
- Verified JS TypeScript build passes.
- Verified Python package installs in editable mode.
- Verified Python SDK tests pass.
- Verified CLI help runs.
- Verified conformance runner still passes.
- Verified frontend build still passes.
- Re-read the phase specification after implementation.
- Checked new SDK and CLI docs for public-safety wording.
- Checked new SDK and CLI files for em dash characters.
- Checked new SDK and CLI files for prohibited client names and unsafe future-value examples.

## Commands Run

| Command | Result |
|---|---|
| `npm --prefix packages/parva-js install` | Passed |
| `npm --prefix packages/parva-js test` | Passed, 3 JS tests |
| `npm --prefix packages/parva-js run build` | Passed |
| `python -m pip install -e packages/parva-python` | Passed |
| `python -m pytest packages/parva-python -q` | Passed, 4 Python tests |
| `pytest packages/parva-python` | Passed, 4 Python tests |
| `python tools/parva-cli/parva_cli.py --help` | Passed |
| `python tools/conformance_runner/run.py` | Passed, 27 of 27 cases |
| `npm --prefix frontend run build` | Passed |

## Repo-Wide Searches

The required searches were run for:

- stale deployment URL patterns
- prohibited client-name and overclaim patterns
- private future-BS route usage in the SDK and CLI packages
- em dash characters in new or edited Phase 3 files

Classifications:

- Existing archived Cloud Run deployment notes and the legacy Cloud Build blueprint still contain stale deployment references. They were not introduced by Phase 3.
- Existing public-safety tests contain prohibited phrases as guardrail input strings. They were not introduced by Phase 3.
- Local phase prompt files contain instruction text and are untracked. They were not staged.
- New SDK and CLI files do not introduce client-specific names, private future values, broad accuracy claims, or direct private future-BS route calls.

## Public Safety Status

Pass.

- No future month-length vectors were added.
- No corrected future values were added.
- No client-specific references were added.
- No private route examples were added.
- Future-BS examples call capabilities only.
- Future-BS claim boundary text preserves `computed_prediction_not_official`.

## Current Limitations

- The JS and Python SDKs are alpha packages. They wrap the public API and do not yet provide offline conversion mode.
- CLI packaging is intentionally simple. The working script form is `python tools/parva-cli/parva_cli.py`.
- Language-specific conformance adapters are documented but not implemented in this phase.
- CLI network commands were not exercised against the live API in the verification loop. The required CLI help smoke check passed, and SDK request behavior is covered by mocked tests.

## Next SDK Work

- Add conformance adapters for JS and Python that load the JSON cases under `conformance/`.
- Add published package metadata and release workflow.
- Add optional local/offline mode for stable published calendar data.
- Add examples for fiscal-year APIs once the public SDK contract is finalized.
