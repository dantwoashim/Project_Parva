# Verification Matrix

Generated: see `reports/release_readiness/final_verification_matrix.json`

Final matrix status: 61 passed, 1 blocked, 0 failed.

| Command | Status | Evidence |
| --- | --- | --- |
| `git status --short` | pass | Showed only roadmap worktree changes before final staging. |
| `python --version` | pass with environment caveat | Ambient shell Python is 3.10.10. Repo verification used Python 3.11.4 through `py -3.11` and release scripts. |
| `py -3.11 --version` | pass | Python 3.11.4. |
| `node --version` | pass with environment caveat | Ambient shell Node is v25.2.1. Repo verification resolved managed Node v20.20.2. |
| `npm --version` | pass | npm 11.10.0. |
| `py -3.11 scripts/verify_environment.py` | pass | Python 3.11.4, managed Node v20.20.2, npm available, frontend lockfile present. |
| `py -3.11 scripts/release/regenerate_public_release_hashes.py --check` | pass | Public release hashes current. |
| `py -3.11 scripts/parva_trust_verify.py` | pass | 22 release checks, 3 signature checks, 11 public sources, 1 trust log entry. |
| `py -3.11 scripts/check_docs_links.py` | pass | Documentation links verified. |
| `py -3.11 scripts/check_path_leaks.py` | pass | No local path leaks detected. |
| `py -3.11 scripts/check_future_bs_public_leakage.py` | pass | Future-BS public leakage check passed. |
| `PYTHONPATH=backend:. py -3.11 scripts/release/check_public_openapi_drift.py` | pass | Static public OpenAPI mirror current. |
| `py -3.11 -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | pass | 874 passed, 8 skipped. |
| `py -3.11 -m pytest tests/unit/bootstrap -q` | pass | 36 passed. |
| `py -3.11 -m pytest tests/security -q` | pass | 7 passed. |
| `py -3.11 -m pytest tests/performance -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | pass | 7 passed. |
| `py -3.11 scripts/perf/route_latency_smoke.py --profile public_reference --output reports/phase_08_performance_sre/latency_baseline.json` | pass | Latency baseline JSON regenerated. |
| `py -3.11 scripts/check_canonical_runtime.py` | pass | Canonical runtime registry passed. |
| `py -3.11 scripts/check_maturity_lanes.py` | pass | Maturity lanes passed with public/private route profile boundaries. |
| `py -3.11 tools/validate_schemas.py` | pass | 31 schemas validated. |
| `py -3.11 scripts/release/check_route_inventory.py` | pass | 448 route entries, 217 canonical v3 routes, 217 legacy routes. |
| `py -3.11 scripts/release/check_documented_routes.py` | pass | 217 canonical v3 routes documented. |
| `py -3.11 scripts/release/check_backend_smoke.py` | pass | Backend smoke passed. |
| `py -3.11 scripts/parva_timegraph_verify.py` | pass | 7416 facts, 27755 relationships, 1 conflict recorded. |
| `py -3.11 scripts/parva_rulelang_verify.py` | pass | 5 rules verified. |
| `py -3.11 scripts/parva_impact_verify.py` | pass | 2 fixture impacts verified. |
| `py -3.11 scripts/parva_agent_verify.py` | pass | 14 tools and 2 schedule items verified. |
| `py -3.11 scripts/parva_protocol_verify.py` | pass | 20 conformance tests verified. |
| `py -3.11 scripts/release/check_public_safety_gate.py` | pass | Public safety gate passed. |
| `py -3.11 scripts/release/check_render_blueprint.py` | pass | Render blueprint passed. |
| `py -3.11 scripts/release/check_repo_hygiene.py` | pass | Repository hygiene passed. |
| `py -3.11 -m ruff check backend tests scripts sdk packages/parva-python packages/parva-ai-tools packages/parva-mcp-server` | pass | All checks passed. |
| `py -3.11 -m pytest packages/parva-python/tests -q` | pass | 18 passed. |
| `py -3.11 -m build packages/parva-python` | blocked | Local Python 3.11 environment lacks the `build` module; repeated `pip install build` attempts timed out against PyPI. |
| `py -3.11 -m pip wheel packages/parva-python --no-deps --no-build-isolation -w <temp>` | pass | Python SDK wheel built successfully through setuptools/wheel already present in the local toolchain. |
| `npm --prefix packages/parva-js test` under managed Node 20/npm lane | pass | 16 JavaScript SDK tests passed. |
| `npm pack --dry-run` under managed Node 20/npm lane in `packages/parva-js` | pass | JavaScript SDK package dry-run passed. |
| `npm --prefix frontend run lint` under managed Node 20/npm lane | pass | ESLint passed. |
| `npm --prefix frontend test -- --run` under managed Node 20/npm lane | pass | 27 files, 120 tests passed. |
| `npm --prefix frontend run build` under managed Node 20/npm lane | pass | Vite production build passed. |
| `py -3.11 -m pytest packages/parva-ai-tools/tests -q` | pass | 8 passed. |
| `py -3.11 -m pytest packages/parva-mcp-server/tests -q` | pass | 8 passed. |
| `py -3.11 public-benchmark/runners/run_against_static_baseline.py` | pass | 38 tasks, 20.53 percent score. |
| `py -3.11 public-benchmark/runners/run_against_parva.py` | pass | 38 tasks, 38 passed, 89.47 percent score. |
| `py -3.11 scripts/ephemeris/verify_kernel_hashes.py` | pass | Configured present kernels verified; optional absent kernel skipped. |
| `py -3.11 scripts/ephemeris/generate_solar_ingress_differential.py` | pass | Solar ingress differential report generated with status `computed` when configured kernels were present. |
| `py -3.11 samples/digital-panchanga-release/2083-bs/verification/verify_release.py` | pass | Sample digital Panchanga release checksums verified. |
| `py -3.11 scripts/release/verify_public.py` | pass | Public reproducibility gate passed with 32 subchecks. |
