# Contributing to Project Parva

Thanks for contributing.

## Rule/Data Changes Require Evidence
If your change touches festival rules, calculations, or official date overrides, include:
- Source references (MoHA / Panchang / primary references)
- Accuracy impact summary
- A signed review trail (`Reviewed-by`, `Signed-off-by`)

## Workflow
1. Open a Rule Change RFC issue (`.github/ISSUE_TEMPLATE/rule-change.yml`).
2. Link evidence and expected behavior changes.
3. Submit PR using `.github/PULL_REQUEST_TEMPLATE.md`.
4. Run test suite and attach result summary.

## Required Checks
- `python3 -m pytest -q`
- Plugin validation if plugin/rule changes:
  - `PYTHONPATH=backend python3 backend/tools/validate_plugins.py`
- For governance docs or rule RFC records:
  - `python3 scripts/governance/verify_approval.py <path-to-rfc-or-pr-md>`
