# Release Candidate Runbook

Use this runbook from a clean checkout when preparing a Parva release candidate.

## Preconditions

- Python `3.11.x`
- Node `20.x`
- A clean git worktree
- Release environment variables present when required:
  - `PARVA_PROVENANCE_ATTESTATION_KEY`
  - `PARVA_PROVENANCE_ATTESTATION_KEY_ID`
  - any production API keys needed for smoke verification

When a workstation is on a newer global Node release, the gate runner may resolve a managed `node@20` runtime through `npx` so the validation sequence still runs on the pinned major version.

## Release Gate Command

Preferred release-candidate command:

```bash
py -3.11 scripts/release/run_release_candidate_gates.py --frontend-clean-install --require-signed-provenance
```

This gate sequence verifies:

- supported local toolchain
- repository hygiene
- Render blueprint alignment
- SDK install surface
- versioned contract freeze
- provenance completeness and attestation verification
- backend tests
- frontend clean install, lint, tests, and production build
- frontend bundle budget
- public-beta artifact generation
- dependency security audit
- browser smoke coverage
- launch-critical golden browser journeys
- role-based launch signoff metadata
- clean source archive packaging

## Manual Review Checklist

After the automated gates pass, confirm:

1. `docs/public_beta/month9_release_dossier.md` reflects the current artifact run and `docs/public_beta/release_candidate_dossier.md` reflects the final RC gate run.
2. degraded-state API metadata is present where defaults/fallbacks are applied.
3. provenance snapshots show the expected `manifest_version`, `canonical_engine_id`, and attestation mode.
4. the frontend still communicates degraded or unavailable states without hidden fallback dates.
5. `reports/release/golden_journeys.json` shows all launch-critical journeys passing.
6. `reports/release/frontend_bundle_budget.json` stays within the published budget thresholds.
7. `reports/security_audit.json` contains no failing checks.
8. the archive in `dist/*-source.zip` opens cleanly and excludes build/runtime residue.

## Candidate Packaging

The release candidate should publish:

- clean source archive from `scripts/release/package_source_archive.py`
- generated authority/public-beta artifacts
- updated public-beta dossier and release-candidate technical dossier
- golden-journey, bundle-budget, and security audit reports
- launch signoff matrix
- operator runbooks
- rollback notes

## Final Sign-Off

Before tagging or announcing a candidate, record:

- git SHA
- runtime versions used for the gate run
- provenance attestation mode and key id
- release dossier paths
- launch signoff document path
- any accepted degraded modes or known limits
