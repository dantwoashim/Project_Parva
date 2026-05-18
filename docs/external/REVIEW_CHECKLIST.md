# External Review Checklist

This checklist prepares a non-maintainer review. It does not claim that an external review has happened.

1. Run `python scripts/release/reviewer_dry_run.py --quick --deterministic`.
2. Verify `examples/external/proofpacks/civil-conversion.proofpack.json`.
3. Verify `examples/external/proofpacks/panchanga-summary.proofpack.json`.
4. Verify `examples/external/timepacks/payroll-date-risk.timepack.json`.
5. Inspect generated artifact `reports/source_coverage/coverage_matrix.md` and generated artifact `reports/proof_contract/route_proof_matrix.md`.
6. Confirm Panchanga output remains computed, method-backed, location-sensitive, and not official ritual authority.
7. Confirm payroll/date-risk output remains decision support, not legal, tax, payroll, banking, or government authority.
8. Record any challenge with the artifact id, disputed field, evidence, and proposed correction.
