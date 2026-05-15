# CI Status

Public CI is configured in `.github/workflows/public-verification.yml` for
pushes to `main`, pull requests to `main`, and manual dispatch.

The workflow uses Python 3.11 and Node 20. It runs environment, backend public,
governance, SDK/AI/MCP, frontend, benchmark, and release-gate jobs.

GitHub Actions status must be checked on GitHub after push; local syntax and
equivalent command checks are recorded in the release readiness matrix.
