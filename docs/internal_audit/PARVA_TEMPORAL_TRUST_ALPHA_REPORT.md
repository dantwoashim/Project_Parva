# Parva Temporal Trust Alpha Report

Date: 2026-05-12

## What Was Built

Project Parva now presents as a source-aware Nepali temporal infrastructure alpha with:

- public-safe BS/AD conversion and calendar APIs
- formal temporal schemas
- conformance fixtures and runner
- release manifest verification
- source registry and calculation trace documentation
- public-safe JavaScript and Python SDK alpha surfaces
- public-safe CLI alpha
- future-BS risk discipline with `computed_prediction_not_official`
- blinded audit protocol documentation
- temporal trust alpha artifacts, signature shape, SBOM shape, and transparency log verification

This final pass tightened integration issues rather than adding a new product surface.

## Architecture Summary

The release story is now consistent:

1. Public users get stable calendar, fiscal, festival, panchanga, source-policy, and capability metadata surfaces.
2. Private or experimental future-BS prediction, export, backtest, model-run, corrected-value, client comparison, and schedule-impact workflows stay gated.
3. Public SDKs call only stable public calendar endpoints and the public future-BS capabilities summary.
4. Release manifests, source registries, calculation traces, and trust artifacts provide reproducible public proof without exposing private future vectors.
5. Future-BS research remains clearly labeled as `computed_prediction_not_official`.

## Files Created

- `docs/internal_audit/ALPHA_RELEASE_CHECKLIST.md`
- `docs/internal_audit/PARVA_TEMPORAL_TRUST_ALPHA_REPORT.md`

## Files Modified

- `frontend/src/services/apiBase.js`
- `cloudbuild.cloudrun.yaml`
- `docs/API_QUICKSTART.md`
- `docs/DEPLOYMENT.md`
- `scripts/future_bs/optimize_regime_aware_accuracy_loop.py`
- `scripts/future_bs/optimize_solar_civil_rules_loop.py`
- `tests/accuracy/test_disagreement_increases_risk.py`
- `tests/public_safety/test_public_release_safety.py`
- `tests/unit/trust/test_temporal_trust_tools.py`

## Files Removed

- `docs/archive/DEPLOY_CLOUD_RUN.md`

The archived Cloud Run guide was stale for the current public Render deployment and contained old public deployment host guidance. The backend Cloud Run Docker path remains available as an optional deployment asset, but it no longer advertises the old image path.

## Commands Run

| Command | Result |
|---|---:|
| `npm --prefix frontend run build` | Pass |
| `python tools/validate_schemas.py` | Pass, 16 schemas validated |
| `python tools/conformance_runner/run.py` | Pass, 27 of 27 cases |
| `python tools/release/verify_release.py data/public/releases/parva-bs-public-demo.manifest.json` | Pass |
| `python tools/trust/verify_log.py` | Pass |
| `$env:PYTHONPATH='backend'; python -m pytest -q` | Pass, 672 passed, 7 skipped |
| `npm --prefix packages/parva-js install` | Pass |
| `npm --prefix packages/parva-js test` | Pass, 3 tests |
| `python -m pip install -e packages/parva-python` | Pass |
| `python -m pytest -q packages/parva-python/tests` | Pass, 4 tests |
| `python tools/parva-cli/parva_cli.py --help` | Pass |
| `npm --prefix frontend run lint` | Pass |
| `npm --prefix frontend run test` | Pass, 109 tests |
| `$env:PYTHONPATH='backend'; python -m pytest -q tests/accuracy/test_disagreement_increases_risk.py` | Pass, 1 test |
| `$env:PYTHONPATH='backend'; python -m pytest -q` after final audit fix | Pass, 672 passed, 7 skipped |

## Public Safety Checks

Public route check:

- `PARVA_ENABLE_EXPERIMENTAL_API=false`
- `PARVA_SHOW_PRIVATE_SCHEMA=false`
- public OpenAPI returned no private future-BS prediction, export, backtest, model-run, loan-impact, external audit, or corrected-value routes
- `/v4/api/future-bs/capabilities` returned metadata only
- `/v5/api/calendar-model-risk/capabilities` returned metadata only

Repo searches:

- no old Cloud Run URL markers remain in tracked repo search scope
- no stale `VITE_API_BASE_URL` remains
- no client-specific names remain in public docs, frontend, examples, or test literals
- no prohibited broad-claim phrases remain
- no em dash remains in tracked README, AGENTS, docs, or frontend source
- exact public-facing future-shadow range labels were de-identified in internal script/report labels where doing so did not remove internal capability

Classified safe matches:

- Public docs mention corrected values only as negative boundary language, such as "does not expose corrected future values".
- Internal ignored-artifact paths still reference future prediction file names required by private tooling. Generated artifacts remain ignored and untracked.

## What Is Not Claimed

Project Parva does not claim:

- official government calendar publication authority
- legal, tax, regulatory, or banking-contract final authority
- guaranteed future dates
- broad future-calendar certainty
- broad 99 percent future accuracy
- replacement of official Nepali calendar publication

Official publication overrides computed output.

## Remaining Risks

- Private future-BS tooling remains powerful and must stay gated in public deployments.
- Platform environment variables on Cloudflare Pages and Render still need to match `docs/DEPLOYMENT.md`.
- Generated private future-BS artifacts are ignored, but a future force-add could still leak them. Public-safety tests and release grep checks should stay in CI.
- Frontend tests passed with non-fatal Node test-environment warnings. No functional failure was observed.

## Next 7-Day Roadmap

1. Verify Render production environment values against `docs/DEPLOYMENT.md`.
2. Verify Cloudflare Pages uses `VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api`.
3. Generate a static public OpenAPI mirror from the public route profile.
4. Add SDK conformance adapters that consume the existing JSON conformance cases.
5. Add a CI check that fails on stale deployment URL markers and public route leakage.
6. Add release signing with a real key backend when operationally ready.
7. Keep future-BS private artifacts out of public tracking and rerun public-safety grep before every release.

## Final Status

The alpha release hardening pass is complete. Required commands passed, public route boundary is verified, SDK and CLI alpha surfaces are usable, docs are coherent, stale deployment guidance was removed, and release checklist artifacts exist.
