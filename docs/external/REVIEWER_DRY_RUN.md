# Reviewer Dry Run

This dry run checks local/offline Project Parva proof artifacts from a clone. It
does not claim external validation, customer adoption, registry acceptance,
package publication, government authority, legal authority, tax authority,
payroll authority, banking authority, or official Panchanga authority.

## Run

```bash
py -3.11 scripts/release/reviewer_dry_run.py --quick --deterministic
```

For the full local-kernel package check:

```bash
py -3.11 scripts/release/reviewer_dry_run.py
```

Expected output:

```json
{
  "status": "pass",
  "json": "reports/external_reviewer_dry_run/review_report.json",
  "markdown": "reports/external_reviewer_dry_run/review_report.md"
}
```

The script verifies:

- civil proof pack replay
- Panchanga proof pack replay
- payroll/date-risk Timepack replay
- local-kernel verification
- public claim boundaries
- public route/profile surface security

The optional JPL lane is skipped unless a local kernel path is configured. A
fallback ephemeris result must not be described as JPL-backed.

## Clean-Clone Steps

1. Install Python 3.11 and Node 20.
2. Install backend/test dependencies with `python -m pip install -c requirements/constraints.txt -e .[test,dev]`.
3. Install local-kernel dependencies with `npm --prefix packages/parva-local-kernel ci`.
4. Run the deterministic dry run command above.
5. Inspect generated artifact `reports/external_reviewer_dry_run/review_report.json` and generated artifact `reports/external_reviewer_dry_run/review_report.md`.

The dry run does not call the live API. It verifies committed proof packs and
Timepacks, runs public claim and public-surface safety checks, and records the
optional JPL lane as skipped when no real kernel is configured.

## Troubleshooting

- Missing proof pack: run `python scripts/release/reviewer_dry_run.py --quick --civil-proofpack <path>` to isolate the failing artifact.
- JPL skipped: configure `PARVA_JPL_KERNEL_PATH` and optional `PARVA_JPL_KERNEL_SHA256`, then run `pytest tests/integration/test_jpl_provider_optional.py -q`.
- Local-kernel failure: run `npm --prefix packages/parva-local-kernel test`.
- Public claim failure: run `python scripts/release/check_public_claims.py` and remove unsupported authority or external-validation language.
