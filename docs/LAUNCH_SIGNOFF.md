# Launch Signoff Matrix

This document records the role-based signoff required before a Parva release
candidate is treated as launch-ready.

## Evidence

- `scripts/release/run_release_candidate_gates.py --frontend-clean-install --require-signed-provenance`
- `reports/release/browser_smoke.json`
- `reports/release/golden_journeys.json`
- `reports/release/frontend_bundle_budget.json`
- `reports/security_audit.json`
- `docs/public_beta/release_candidate_dossier.md`

## Sources

- `docs/RELEASE_CANDIDATE_RUNBOOK.md`
- `docs/CLOSED_BETA_OPERATIONS.md`
- `docs/RELIABILITY.md`
- `docs/INSTITUTIONAL_LAUNCH_CHECKLIST.md`

Reviewed-by: Engineering / automated_release_candidate_gates
Reviewed-by: QA / golden_journeys_suite
Reviewed-by: Design / stitch parity review
Reviewed-by: Product / launch-critical surface review
Signed-off-by: Release preparation / release_coordinator

## Acceptance Notes

- Engineering confirms the candidate passes the repository, contract, provenance,
  and packaging gates.
- QA confirms the browser smoke suite and launch-critical golden journeys pass
  against the built application.
- Design confirms the launch-critical shell and key consumer routes match the
  current editorial product direction.
- Product confirms only the launch-critical routes are treated as primary entry
  points and that support/beta surfaces remain correctly de-emphasized.
