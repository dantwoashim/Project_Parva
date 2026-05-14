# Phase 02 Red-Check Sprint Report

Generated artifact for Phase 02 verification evidence.

## Status

Phase 02 public verification gate is green as of commit `88c8633` plus this report update.

## Scope Audited

- `parva_codex_phase_files/AGENTS.md`
- `parva_codex_phase_files/phase_02_red-check_sprint.md`
- Root `AGENTS.md`
- README and required docs: `README.md`, `docs/README.md`, `docs/VERSIONING.md`, `docs/DEVELOPMENT.md`, `docs/KNOWN_LIMITATIONS.md`
- Deployment and project config: `render.yaml`, `pyproject.toml`, `Makefile`, `.github/workflows/`
- Route profile/bootstrap: `backend/app/bootstrap/app_factory.py`, `backend/app/bootstrap/router_registry.py`, `backend/app/bootstrap/settings.py`, `backend/app/main.py`
- Phase 02 gate scripts: `scripts/release/verify_public.py`, `scripts/release/check_repo_hygiene.py`, `scripts/check_path_leaks.py`, `scripts/check_docs_links.py`, `scripts/release/check_public_openapi_drift.py`, `scripts/release/check_public_safety_gate.py`

## Before Matrix

| Gate | Command | Result | Evidence |
| --- | --- | --- | --- |
| Public gate | `python --version; python scripts/release/verify_public.py` | Fail | Shell `python` was 3.10.10, but `verify_public.py` found Python 3.11.4 and failed at repository hygiene because tracked `reports/phase_01_baseline/*` files were rejected as generated reports. |
| Trust verify | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/parva_trust_verify.py` | Pass | `trust verification passed`; 11 public trust artifact hashes matched. |
| Docs links | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/check_docs_links.py` | Fail | `docs\strategy\PROJECT_PARVA_10_10_SOTA_MASTER_PLAN.md:817: missing path docs/internal_archive`. |
| Schema validation | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe tools/validate_schemas.py` | Pass | `validated 30 schemas`. |
| Route inventory | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/release/check_route_inventory.py` | Pass | `route_count: 448`, `canonical_v3_route_count: 217`, `legacy_route_count: 217`. |
| Documented routes | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/release/check_documented_routes.py` | Pass | `Documented route inventory verified (217 canonical v3 routes).` |
| OpenAPI drift | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/release/check_public_openapi_drift.py` | Pass | `Static public OpenAPI mirror is current.` |
| Public pytest lane | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | Pass | `780 passed, 8 skipped in 138.08s`. |
| Route/profile/frontend contract | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe -m pytest tests/contract/test_frontend_routes_vs_backend_profile.py -q` | Pass | `1 passed`. |
| Layer 5 trust contract | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe -m pytest tests/contract/test_layer5_trust_contract.py -q` | Pass | `12 passed`. |
| Python SDK tests | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe -m pytest packages/parva-python/tests -q` | Pass | `14 passed`. |
| JavaScript SDK tests | `npm --prefix packages/parva-js test` | Pass | `13` Node test cases passed after package build. |
| Frontend lint/test/build | `npm --prefix frontend run lint; npm --prefix frontend test -- --run; npm --prefix frontend run build` | Pass | `25` test files and `112` tests passed; Vite build completed. |
| Verification scripts | `scripts/parva_timegraph_verify.py`, `scripts/parva_rulelang_verify.py`, `scripts/parva_impact_verify.py`, `scripts/parva_agent_verify.py`, `scripts/parva_agent_benchmark.py` with Python 3.11 | Pass | TimeGraph, RuleLang, Impact, Agent verify, and benchmark all reported `ok` or `pass`. |
| Protocol scripts | `scripts/parva_protocol_verify.py`; `scripts/parva_conformance.py --target local --level parva_core`; `scripts/parva_conformance.py --target local --level parva_full` with Python 3.11 | Pass | Protocol verify passed; core conformance `9/9`; full conformance `24/24`. |
| Backend smoke and lint | `scripts/release/check_backend_smoke.py`; `scripts/release/check_sdk_install.py`; `python -m ruff check backend tests scripts sdk packages/parva-python` with Python 3.11 | Pass | Backend smoke passed, SDK imports passed, Ruff reported `All checks passed!`. |
| Offline bundle | `scripts/parva_offline_bundle.py --output dist/parva-offline-bundle`; `scripts/parva_offline_verify.py dist/parva-offline-bundle` with Python 3.11 | Pass | Bundle wrote `19` contents; verifier checked `19` with no issues. |

## Changes Made

- `scripts/release/check_repo_hygiene.py`: allowed tracked phase governance report directories for Phase 01 and Phase 02 while continuing to reject unrelated tracked generated reports.
- `scripts/check_path_leaks.py`: changed scanning to the Git public candidate set from `git ls-files --cached --others --exclude-standard`, with explicit UTF-8 decoding, so ignored local artifacts do not break public verification.
- `docs/internal_archive/README.md`: added public-safe placeholder for an intentionally empty archive directory referenced by the strategy plan.
- Public docs and strategy docs: replaced Windows-launcher-only `py -3.11` examples with `python3.11`, `PARVA_PYTHON=/path/to/python3.11 python ...`, or `make verify-public PYTHON=/path/to/python3.11`.
- `docs/strategy/PROJECT_PARVA_10_10_SOTA_MASTER_PLAN.md`: removed prohibited public phrases that triggered the public safety gate.

## After Matrix

| Gate | Command | Result | Evidence |
| --- | --- | --- | --- |
| Repository hygiene | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/release/check_repo_hygiene.py` | Pass | `Repository hygiene check passed.` |
| Docs links | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/check_docs_links.py` | Pass | `Documentation links verified.` |
| Path leaks | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/check_path_leaks.py` | Pass | `No local path leaks detected.` |
| Public safety | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/release/check_public_safety_gate.py` | Pass | Public OpenAPI boundary, public demo boundary, future conversion policy, schema validation, and public text safety all passed. |
| Ruff on changed scripts | `C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe -m ruff check scripts/check_path_leaks.py scripts/release/check_repo_hygiene.py` | Pass | `All checks passed!` |
| Cross-platform hardcoding scan | `rg -n 'py -3.11|\["py", "-3.11"|\[''py'', ''-3.11''' tests scripts backend README.md docs/API_QUICKSTART.md docs/API_REFERENCE_V3.md docs/DEVELOPMENT.md docs/future_bs/MONTH_START_INVERSION_WORKBENCH.md docs/strategy/PROJECT_PARVA_10_10_SOTA_MASTER_PLAN.md` | Pass | No matches, exit code `1` from ripgrep no-match behavior. |
| Full public gate | `PARVA_PYTHON=C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe python scripts/release/verify_public.py` | Pass | All public gate subcommands passed, ending with `Public reproducibility gate passed.` |

## Acceptance Checklist

1. `python scripts/parva_trust_verify.py` passes: yes, run with Python 3.11, `trust verification passed`.
2. `python scripts/check_docs_links.py` passes: yes, `Documentation links verified.`
3. Public pytest lane passes without private/wide/research data: yes, `780 passed, 8 skipped`.
4. Remaining `py -3.11` hardcoding removed from cross-platform tests/scripts: yes, no matches in `tests`, `scripts`, or `backend`; active public docs were also cleaned.
5. `verify_public.py` or `make verify-public PYTHON=...` supported and documented: yes, `PARVA_PYTHON=... python scripts/release/verify_public.py` passed and docs mention both `PARVA_PYTHON` and `make verify-public PYTHON=...`.
6. Route inventory checks pass: yes, route inventory and documented routes both passed.
7. Route/profile/frontend contract passes: yes, `test_frontend_routes_vs_backend_profile.py` passed.
8. OpenAPI drift check exists and passes: yes, `scripts/release/check_public_openapi_drift.py` exists and passed.
9. SDK tests pass: yes, Python SDK `14 passed`; JS SDK `13` test cases passed.
10. Frontend lint/build/test pass or blocker isolated: yes, lint passed, `112` Vitest tests passed, Vite build passed.
11. CI public verification workflow exists: yes, `.github/workflows/verify-public.yml` exists and runs on `push` and `pull_request`.
12. Scheduled trust drift workflow exists: yes, `.github/workflows/trust-drift.yml` exists with daily cron and `workflow_dispatch`, running trust, schema, and protocol verification.
13. `reports/phase_02_red_check/` records the before/after matrix: yes, this report.

## Remaining Blockers

None for Phase 02 acceptance.

## Later-Phase Backlog

- `scripts/check_path_leaks.py` now intentionally scans public Git candidates. If future phases want local ignored artifacts scanned too, add a separate private/developer-only hygiene command rather than making the public lane depend on ignored scratch files.
- Historical ignored files under `docs/internal_audit/` still contain old Windows launcher examples. They are ignored and not part of the public candidate set. If those reports become tracked again, normalize them first.

## Risk Notes

- Reduced risk: public verification no longer fails because required phase reports exist.
- Reduced risk: public path leak scanning no longer depends on ignored local phase prompt files or generated repo snapshots.
- Reduced risk: active public docs no longer recommend the Windows-only `py -3.11` launcher as the public verification path.
- Introduced risk: `check_path_leaks.py` now relies on Git being available for its strict public candidate set. It falls back to filesystem traversal if Git fails.
