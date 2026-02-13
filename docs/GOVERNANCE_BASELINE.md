# Governance Baseline

Last updated: 2026-02-12

## Repository Integrity Policy
- Source control starts from the current repository baseline.
- No fabricated historical commits, release dates, or retroactive execution trails are permitted.
- Completion claims must reference:
  - implementation path(s),
  - test evidence,
  - and release note/document links.

## Version Canonicalization
- Canonical product version: `3.0.0`
- Runtime: `/Users/rohanbasnet14/Documents/Project Parva/backend/app/main.py`
- Python package: `/Users/rohanbasnet14/Documents/Project Parva/pyproject.toml`
- Frontend package: `/Users/rohanbasnet14/Documents/Project Parva/frontend/package.json`

## CI Baseline
- Workflow file: `/Users/rohanbasnet14/Documents/Project Parva/.github/workflows/ci.yml`
- Required checks:
  - backend tests
  - frontend build
  - contract freeze
  - conformance run

