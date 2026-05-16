# Distribution Readiness Baseline

Baseline captured at the start of this sprint before implementation changes.

## Environment

- Repo status: clean except an untracked nested checkout artifact, removed after
  path verification.
- Python: `py -3.11 --version` returned `Python 3.11.4`; ambient `python`
  returned `Python 3.10.10`.
- Node: ambient `node --version` returned `v25.2.1`; Node 20 is available via
  `npx -p node@20`.
- npm: ambient `npm --version` returned `11.10.0`; npm 10 is available via
  `npx -p npm@10`.

## Public Checks

- `python scripts/release/check_public_claims.py`: pass.
- `python scripts/check_docs_links.py`: pass.
- `python scripts/check_path_leaks.py`: pass.
- `python public-benchmark/validate_benchmark.py`: pass, 38 tasks.
- `python public-benchmark/runners/compare_results.py`: pass, Parva 89.47%
  versus static baseline 20.53%.
- `python -m pytest packages/parva-ai-tools/tests packages/parva-mcp-server/tests -q`:
  pass, 16 tests.

## Initial Findings

- Free tier was hostile for public-beta adoption: `monthly_limit=0` and
  `FREE_DAILY_LIMIT=100`.
- `frontend/src/redesign/ParvaExperience.jsx` was 3,454 lines.
- Public benchmark results existed but were mostly repo-local artifacts.
- Package metadata existed but versions and repository metadata were not
  coherent across packages.
- MCP adapter existed but registry submission metadata was missing.
- `.gitattributes` excluded all `reports/` paths from source archives while
  README linked the external reviewer packet.
- Duplicate runtime paths were already registered as deprecated or
  compatibility-only; removal targets and distribution report were missing.
