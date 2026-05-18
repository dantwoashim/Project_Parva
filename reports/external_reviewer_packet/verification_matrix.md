# Verification Matrix

The detailed command matrix is maintained in `reports/release_readiness/final_verification_matrix.json` and summarized in `reports/next_roadmap_execution/verification_matrix.md`.

## Final Gate

`py -3.11 scripts/release/verify_public.py` passed with 32 subchecks:

- environment
- repository hygiene
- secret scan
- path leak scan
- public safety gate
- documentation links
- canonical runtime registry
- maturity lanes
- Render public blueprint
- temporal trust verification
- TimeGraph verification
- RuleLang verification
- impact simulator verification
- agentic temporal verification
- agent benchmark
- protocol verification
- external temporal rules
- benchmark schema
- public claims
- protocol conformance core
- protocol conformance full
- documented route inventory
- public OpenAPI drift
- backend smoke
- Python SDK import smoke
- backend lint
- backend public tests
- Python package SDK tests
- frontend lint
- frontend tests
- frontend build
- JavaScript SDK tests

## Additional New Work Checks

- Final verification matrix: 61 passed, 1 blocked, 0 failed.
- agent-tool tests: 8 passed.
- MCP tests: 8 passed.
- Benchmark runners: Parva 89.47 percent, static baseline 20.53 percent.
- JPL kernel hash verifier and solar ingress differential generator passed.
- Sample digital Panchanga release verifier: passed.

## Local Blocker

`py -3.11 -m build packages/parva-python` is blocked locally because the Python `build` module is absent and `pip install build` timed out against PyPI. The Python SDK wheel build still passed through `py -3.11 -m pip wheel packages/parva-python --no-deps --no-build-isolation -w <temp>`.
