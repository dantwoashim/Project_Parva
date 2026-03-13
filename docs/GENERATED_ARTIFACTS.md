# Generated Artifacts

Project Parva uses a generated-artifact policy for release evidence.

## Canonical policy

- Files under `reports/` are generated in CI and release workflows.
- Generated artifacts are not required to be committed to git.
- Public copies that need to live in the repository are published under
  `docs/public_beta/`.

## Expected generated outputs

- `reports/conformance_report.json`
- `reports/authority_dashboard.json`
- `reports/accuracy/annual_accuracy_2082.json`
- `reports/release/month9_dossier.json`
- `reports/security_audit.json`

## How they are produced

- Conformance: `python scripts/spec/run_conformance_tests.py`
- Accuracy: `python scripts/generate_accuracy_report.py`
- Authority dashboard: `python scripts/generate_authority_dashboard.py`
- Release dossier: `python scripts/release/generate_month9_dossier.py`
- Security audit: `python scripts/security/run_audit.py`

Any documentation that mentions a `reports/...` path should label it as a
generated artifact unless the file is committed in the repository.
