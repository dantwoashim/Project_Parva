# Generated Artifacts

Project Parva uses a generated-artifact policy for public-beta release evidence.

## Canonical policy

- Files under `reports/` are generated in CI and release workflows.
- Generated artifacts are not required to be committed to git.
- Public copies that need to live in the repository are published under
  `docs/public_beta/`.

## Expected generated outputs

- `reports/conformance_report.json`
- `reports/rule_ingestion_summary.json`
- `reports/authority_dashboard.json`
- `reports/accuracy/annual_accuracy_2082.json`
- `reports/release/month9_dossier.json`
- `reports/security_audit.json`

## How they are produced

- Conformance: `python scripts/spec/run_conformance_tests.py`
- Public-beta artifact pack: `python scripts/release/generate_public_beta_artifacts.py`
- Security audit: `python scripts/security/run_audit.py`

Any documentation that mentions a `reports/...` path should label it as a
generated artifact unless the file is committed in the repository.

The current Parva public-beta build path uses `backend/` and `frontend/` only.
The old root `viral-sync` workspace residue has been removed, and
`scripts/release/check_repo_hygiene.py` now protects that boundary in CI.
