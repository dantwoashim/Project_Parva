# Reviewer Dry Run

This dry run checks local/offline Project Parva proof artifacts from a clone. It
does not claim external validation, customer adoption, registry acceptance,
package publication, government authority, legal authority, tax authority,
payroll authority, banking authority, or official Panchanga authority.

## Run

```bash
py -3.11 scripts/release/reviewer_dry_run.py --quick
```

For the full local-kernel package check:

```bash
py -3.11 scripts/release/reviewer_dry_run.py
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
