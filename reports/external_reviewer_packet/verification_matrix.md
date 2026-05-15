# Verification Matrix

The detailed command matrix is maintained in `reports/next_roadmap_execution/verification_matrix.md`.

## Final Gate

`py -3.11 scripts/release/verify_public.py` passed with 29 subchecks:

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

- AI-tool and MCP tests: 11 passed.
- Benchmark runners: Parva 86.58 percent, static baseline 20.53 percent.
- JPL kernel hash verifier: passed with configured present kernels verified and optional absent kernel skipped.
- Sample digital Panchanga release verifier: passed.
