# Public Nepali Date Issue Conformance Summary

## Summary

| Metric | Count |
|---|---:|
| Total cases | 22 |
| Executed | 12 |
| Passed | 12 |
| Failed | 0 |
| Skipped/documented | 10 |
| Review-needed | 5 |

- Suite: `public-nepali-date-issues`
- Generated at: `2026-05-23T11:39:56Z`
- Repository commit: `5d326c35c99195da78cc7a1abe51c6ca1e2056ad`

## Executed Cases

- `cht-core-7925-invalid-kartik-2079-accepted`
- `go-nepali-15-2024-06-14-ad-to-bs-boundary`
- `leapfrog-13-2018-03-12-range-error`
- `medic-26-2081-11-month-length-correction`
- `medic-26-2081-12-month-length-correction`
- `medic-26-2082-01-month-length-correction`
- `medic-26-2082-02-month-length-correction`
- `medic-26-2082-06-month-length-correction`
- `medic-26-2082-08-month-length-correction`
- `medic-26-2082-09-month-length-correction`
- `medic-26-2082-10-month-length-correction`
- `yarsa-257-258-2087-mangsir-source-drift`

## Skipped/documented Cases

- `node-nepali-datetime-82-source-provenance`: documented-only public issue
- `leapfrog-70-2082-2083-month-length-cluster`: documented-only public issue
- `medic-bikram-sambat-26-2081-2082-month-corrections`: documented-only public issue
- `leapfrog-33-35-april-2021-boundary`: documented-only public issue
- `odk-pre-1951-lower-bound-range`: documented-only public issue
- `subeshb1-71-upper-range-above-2090-12-30`: documented-only public issue
- `node-nepali-datetime-121-future-date-accuracy`: documented-only public issue
- `yarsa-252-payroll-asoj-month-duration`: documented-only public issue
- `erpnext-31245-bs-support-request`: documented-only public issue
- `frappe-books-787-bs-support-request`: documented-only public issue

## Review-needed Cases

- `leapfrog-33-35-april-2021-boundary`
- `node-nepali-datetime-121-future-date-accuracy`
- `odk-pre-1951-lower-bound-range`
- `subeshb1-71-upper-range-above-2090-12-30`
- `yarsa-252-payroll-asoj-month-duration`

## Failure-class Breakdown

- `ad_to_bs_conversion_mismatch`: 2
- `bs_to_ad_conversion_mismatch`: 1
- `business_workflow_gap`: 2
- `frontend_backend_source_drift`: 1
- `future_bs_uncertainty`: 1
- `invalid_bs_date_accepted`: 1
- `month_length_mismatch`: 10
- `payroll_date_risk`: 1
- `source_provenance`: 1
- `unsupported_lower_range`: 1
- `unsupported_upper_range`: 1

## Evidence-level Breakdown

- `business_wedge`: 3
- `narrative_evidence`: 1
- `reported_public_issue`: 4
- `reported_public_issue_partial`: 3
- `verified_public_issue`: 11

## Authority Boundary

Public issue fixtures are regression and conformance evidence, not official calendar source material or upstream approval.

Project Parva runs a public Nepali date issue conformance suite with explicit evidence levels and review-needed boundaries.

This report is not a legal, payroll, banking, ritual, or calendar-publication authority.
