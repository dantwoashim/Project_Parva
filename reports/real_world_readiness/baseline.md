# Real-World Readiness Baseline

Generated: 2026-05-17
Commit at baseline: `7ac1c7583c1405923b208d236fa37acfdba9d940`

## Environment

- `python --version`: Python 3.10.10, not the project runtime.
- `py -3.11 --version`: Python 3.11.4, used for verification.
- `node --version`: v25.2.1, not the project runtime.
- `npm --version`: 11.10.0, not the project runtime.
- Node 20/npm 10 commands use `npx -y -p node@20 -p npm@10`.

## Baseline Verification

- `py -3.11 scripts/release/check_public_claims.py`: passed.
- `py -3.11 scripts/check_docs_links.py`: passed.
- `py -3.11 scripts/check_path_leaks.py`: passed.
- `py -3.11 public-benchmark/validate_benchmark.py`: passed, 38 tasks.
- `py -3.11 public-benchmark/runners/compare_results.py`: passed, Parva 89.47%, static baseline 20.53%.
- `py -3.11 -m pytest packages/parva-agent-tools/tests packages/parva-mcp-server/tests -q`: passed, 18 tests before MCP stdio work.

## MCP Baseline

Before this sprint, `packages/parva-mcp-server` supported `--manifest` and `--check` only. It did not support `--stdio`; the desktop MCP client example launched `--manifest`, which prints JSON and exits. That was not a live MCP server.

## Product Baseline

- Free tier already had `FREE_MONTHLY_LIMIT = 10_000` and `FREE_DAILY_LIMIT = 1_000`.
- `frontend/src/redesign/ParvaExperience.jsx` was 18 lines, with the previous component split already present.
- Benchmark v0 had 38 public-safe tasks.
- Reviewer/CI reports pointed to commit `7ac1c75` before new changes.

## Known Baseline Blockers

- MCP live stdio server was missing and was the primary real-world blocker.
- Enterprise BS month metadata still used static lookup through `days_in_bs_month()` instead of solar-civil sankranti computation.
