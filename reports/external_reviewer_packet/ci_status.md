# CI Status

Public CI is configured in `.github/workflows/public-verification.yml` for
pushes to `main`, pull requests to `main`, and manual dispatch.

The workflow uses Python 3.11 and Node 20. It runs environment, backend public,
governance, SDK/AI/MCP, frontend, benchmark, and release-gate jobs.

Last checked: 2026-05-16T05:00Z.

Checked commit: `db4ec3288e8fbec9ee63633e6ac019307c0004cd`.

GitHub Actions evidence:

- Public verification: passed, <https://github.com/dantwoashim/Project_Parva/actions/runs/25953295356>
- CI: passed, <https://github.com/dantwoashim/Project_Parva/actions/runs/25953295366>

The public verification run passed all visible jobs:

- environment
- backend-public
- governance
- sdk-ai-mcp
- frontend
- benchmark
- release-gate

The CI run passed both visible jobs:

- backend-quality
- frontend-quality

GitHub emitted Node 20 action deprecation warnings for third-party action
runtime internals. The project runtime under test remains pinned to Node 20 for
application and package commands.
