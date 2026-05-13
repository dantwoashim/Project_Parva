# Alpha Release Checklist

Date: 2026-05-12

Scope: final integration hardening for Parva Temporal Trust Infrastructure Alpha.

## Release Checklist

| Check | Status | Evidence |
|---|---:|---|
| Public API stable | Pass | Public OpenAPI smoke check found no private future-BS prediction, export, backtest, model-run, loan-impact, or corrected-value routes when experimental routes were disabled. |
| Frontend stable | Pass | `npm --prefix frontend run build`, `npm --prefix frontend run lint`, and `npm --prefix frontend run test` passed. Frontend tests covered public shell, today, my-place, festivals, best-time, and visual baselines. |
| No old Cloud Run public references | Pass | Repo grep for old Cloud Run URL markers returned no matches after removing the stale archive deployment doc and replacing the stale Cloud Build image default. |
| No sensitive future leaks in public docs/examples | Pass | Public examples grep returned no private future route calls, full future vectors, future exports, client names, or broad accuracy claims. |
| Private routes gated | Pass | Public OpenAPI check confirmed private future-BS routes are hidden with `PARVA_ENABLE_EXPERIMENTAL_API=false` and `PARVA_SHOW_PRIVATE_SCHEMA=false`. |
| Public capabilities safe | Pass | `/v4/api/future-bs/capabilities` and `/v5/api/calendar-model-risk/capabilities` returned metadata only with `publication_status: computed_prediction_not_official`. |
| Spec exists | Pass | `docs/spec/PARVA_TEMPORAL_SPEC_V0_1.md` exists and is non-empty. |
| Schemas parse | Pass | `python tools/validate_schemas.py` validated 16 schemas. |
| Conformance runner works | Pass | `python tools/conformance_runner/run.py` passed 27 of 27 cases. |
| SDK alpha exists | Pass | JS SDK and Python SDK directories exist with public-safe calendar and capabilities methods. |
| JS SDK install/build/test path works | Pass | `npm --prefix packages/parva-js install` and `npm --prefix packages/parva-js test` passed. |
| Python SDK install/test path works | Pass | `python -m pip install -e packages/parva-python` and `python -m pytest -q packages/parva-python/tests` passed. |
| CLI alpha exists | Pass | `python tools/parva-cli/parva_cli.py --help` returned public-safe commands. |
| Release manifest exists | Pass | `data/public/releases/parva-bs-public-demo.manifest.json` verified successfully. |
| Source registry exists | Pass | Release verifier checked `data/public/releases/parva-bs-public-demo.sources.json`. |
| Trace format exists | Pass | Release verifier checked `schemas/calculation-trace.schema.json`. |
| Future-risk alpha exists | Pass | `schemas/future-risk.schema.json`, public capabilities routes, and future-BS claim-boundary docs exist. |
| Blinded audit aggregate mode exists | Pass | `docs/future_bs/BLINDED_AUDIT_PROTOCOL.md`, `schemas/blinded-audit-report.schema.json`, and `tools/future_bs_audit` are present. |
| Trust alpha exists | Pass | `docs/TRUST_INFRASTRUCTURE_ALPHA.md`, `docs/TEMPORAL_SBOM.md`, `docs/TRANSPARENCY_LOG.md`, and `tools/trust/verify_log.py` are present and verified. |
| Docs coherent | Pass | Required docs exist, deployment doc was completed, SDK quickstart import was corrected, and public/private boundaries are consistent. |
| Build passed | Pass | Frontend build passed. |
| Backend tests passed | Pass | `$env:PYTHONPATH='backend'; python -m pytest -q` passed 672 tests with 7 skipped. |
| Remaining blockers listed | Pass | See remaining risks below. |

## Public Safety Search Results

Searches performed:

- repo-wide grep for stale backend-host markers, deprecated frontend API env names, client/prospect names, and prohibited public-claim phrases
- `git grep -n -I -E "2084-2099|2084-2200|2200.*export|export.*2200|corrected future values|private future values|full future vectors" -- frontend docs README.md examples schemas tests tools backend scripts data .`
- tracked public docs and frontend source were searched for em dash characters

Results:

- Old Cloud Run markers, stale `VITE_API_BASE_URL`, client names, and prohibited public claims: no matches.
- Em dash in tracked public docs and frontend source: no matches.
- Future-risk boundary phrases remain in public docs as negative boundary language, for example "does not expose corrected future values". Classified as safe.
- Internal future-BS tooling still contains ignored-artifact paths and internal future-shadow labels. Classified as internal execution capability, not public docs/examples or public API output.

## Remaining Risks

- Private future-BS tooling remains in the repository for internal runs. It is safe only while route gating, schema hiding, and artifact ignore rules remain enforced.
- Generated private artifacts under ignored paths must not be force-added.
- Render and Cloudflare settings still need to match `docs/DEPLOYMENT.md` in the platform dashboards.
- Frontend tests passed with non-fatal Node warnings from the test environment. No test failed.

## Final Status

Alpha release checklist passes for repository state, public-safety posture, route boundary, SDK usability, schema validation, conformance, release manifest verification, transparency log verification, frontend build/lint/tests, and backend tests.
