# Project Parva Reviewer Dry Run

This is a local/offline review dry run. It does not prove external validation, adoption, registry acceptance, package publication, or official authority.

- Status: pass
- Commands: 8

| Check | Status | Exit |
| --- | --- | ---: |
| environment | pass | 0 |
| local-kernel tests | pass | 0 |
| civil proofpack | pass | 0 |
| panchanga proofpack | pass | 0 |
| payroll timepack | pass | 0 |
| public claims | pass | 0 |
| public surface security | pass | 0 |
| optional JPL kernel lane | skip | 0 |

## Safe Claims

- Local/offline proof packs can be verified from committed artifacts.
- The reviewer dry run exercises civil, Panchanga, and payroll/date-risk examples without live API access.
- Panchanga results are computed/method-backed decision support with explicit non-authority boundaries.

## Forbidden Claims

- No government authority.
- No legal, tax, payroll, or banking authority.
- No official future-date authority.
- No official Panchanga or ritual authority.
- No external certification, registry acceptance, package publication, adoption, or customer proof unless real evidence exists.
- No real JPL-kernel execution is claimed unless PARVA_JPL_KERNEL_PATH is configured and verified.

## Expected Outputs

- json_report: `reports/external_reviewer_dry_run/review_report.json`
- markdown_report: `reports/external_reviewer_dry_run/review_report.md`
- civil_proofpack: `examples/external/proofpacks/civil-conversion.proofpack.json`
- panchanga_proofpack: `examples/external/proofpacks/panchanga-summary.proofpack.json`
- payroll_timepack: `examples/external/timepacks/payroll-date-risk.timepack.json`
