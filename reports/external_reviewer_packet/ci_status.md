# CI Status

Public CI is configured in `.github/workflows/public-verification.yml` for
pushes to `main`, pull requests to `main`, and manual dispatch.

The workflow uses Python 3.11 and Node 20. It runs environment, backend public,
governance, SDK/Agent/MCP, frontend, benchmark, and release-gate jobs.

Last checked after this distribution sprint: 2026-05-16T10:45Z.

Checked commit:
`f9504dfb5b972889f33d8f16d06e17f4180446ac`.

GitHub Actions evidence:

- Public verification: passed, <https://github.com/dantwoashim/Project_Parva/actions/runs/25959896441>
- CI: passed, <https://github.com/dantwoashim/Project_Parva/actions/runs/25959896434>

The public verification run passed all visible jobs:

- environment
- backend-public
- governance
- sdk-agent-mcp
- frontend
- benchmark
- release-gate

The CI run passed both visible jobs:

- backend-quality
- frontend-quality

GitHub emitted Node 20 action deprecation warnings for third-party action
runtime internals. The project runtime under test remains pinned to Node 20 for
application and package commands.

The final pushed sprint verified the benchmark page, package-readiness checker,
MCP registry metadata checker, archive hygiene checker, and frontend component
split in public CI.
