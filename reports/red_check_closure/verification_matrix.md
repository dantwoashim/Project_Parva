# Verification Matrix

All commands below were run with Python 3.11.4 first on PATH unless noted. The
full public gate also required Node 20.20.2 first on PATH.

| Command | Result | Evidence summary |
| --- | --- | --- |
| `python scripts/release/regenerate_public_release_hashes.py --check` | PASS | `manifest_ok=true`, `signature_ok=true`. |
| `python scripts/release/regenerate_public_release_hashes.py --write` | PASS | Deterministic write path returned `ok=true`. |
| `python scripts/parva_trust_verify.py` | PASS | Trust verification passed; public source registry hash matched. |
| `python scripts/check_docs_links.py` | PASS | Documentation links verified. |
| `python scripts/check_future_bs_public_leakage.py` | PASS | Required Phase 07 report exists; public profiles/OpenAPI exclude exact private Future-BS routes. |
| `PYTHONPATH=backend:. python scripts/release/generate_public_demo_openapi.py` | PASS | Wrote public OpenAPI mirror with 387 paths. |
| `PYTHONPATH=backend:. python scripts/release/check_public_openapi_drift.py` | PASS | Static public OpenAPI mirror is current. |
| `python -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | PASS | 846 passed, 8 skipped. |
| `python -m pytest tests/future_bs tests/accuracy tests/artifacts tests/performance -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | PASS | 56 passed. |
| `python -m pytest tests/unit/bootstrap -q` | PASS | 35 passed. |
| `python -m pytest tests/security -q` | PASS | 7 passed. |
| `python -m pytest tests/performance -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20` | PASS | 7 passed. |
| `python scripts/perf/route_latency_smoke.py --profile public_reference --output reports/phase_08_performance_sre/latency_baseline.json` | PASS | Wrote latency baseline: 6 routes, 0 failures, 0 warnings. |
| `python scripts/check_canonical_runtime.py` | PASS | Canonical runtime registry check passed. |
| `python scripts/check_maturity_lanes.py` | PASS | `ok=true`; route/profile/OpenAPI maturity data clean. |
| `python scripts/check_path_leaks.py` | PASS | No local path leaks detected. |
| `python tools/validate_schemas.py` | PASS | 30 schemas validated. |
| `python scripts/release/check_route_inventory.py` | PASS | `ok=true`; 448 routes, 217 canonical v3 routes. |
| `python scripts/release/check_documented_routes.py` | PASS | 217 canonical v3 routes documented. |
| `python scripts/release/check_backend_smoke.py` | PASS | Backend smoke checks passed. |
| `python scripts/parva_timegraph_verify.py` | PASS | 7416 facts, 27755 relationships, 1 conflict. |
| `python scripts/parva_rulelang_verify.py` | PASS | 5 public rules verified. |
| `python scripts/parva_impact_verify.py` | PASS | 2 fixture impacts verified. |
| `python scripts/parva_agent_verify.py` | PASS | 14 tools and 2 schedule items verified. |
| `python scripts/parva_protocol_verify.py` | PASS | 20 conformance tests verified. |
| `python scripts/release/check_public_safety_gate.py` | PASS | Public safety gate passed. |
| `python scripts/release/check_render_blueprint.py` | PASS | Render blueprint check passed. |
| `python scripts/release/check_repo_hygiene.py` | PASS | Repository hygiene check passed. |
| `python scripts/release/verify_public.py` | PASS | Full public reproducibility gate passed with Python 3.11.4 and Node 20.20.2 first on PATH. |

