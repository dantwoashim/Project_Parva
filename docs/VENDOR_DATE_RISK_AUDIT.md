---
status: public-beta
audience: enterprise
---

# Vendor Date Risk Audit

The first commercial wedge is a BS Date Risk Audit and Conformance Suite for
Nepali software vendors, ERP, accounting, cooperative, microfinance, HR, payroll
software, and fintech platforms. Banks can be served later, but vendor and
software-platform proof is the lower-friction first step.

## Input CSV

```csv
bs_date,workflow_type,expected_behavior,actual_ad_date,holiday_assumption,fiscal_assumption
2082-01-01,invoice_due_date,next_working_day,2025-04-14,known_public_holidays,nepal_fiscal_year
```

Required columns:

- `bs_date`
- `workflow_type`
- `expected_behavior`

Optional columns:

- `actual_ad_date`
- `holiday_assumption`
- `fiscal_assumption`

## Output Report

The audit report should identify invalid dates, unsupported ranges, source
conflicts, holiday mismatches, fiscal cutoff mismatches, working-day mismatches,
review-required cases, and an overall conformance score.

For BS month-length checks, the enterprise API default is canonical
trust-arrest mode. Static lookup output is accepted only as explicit
compatibility/reference evidence and must remain review-required in vendor
reports.

Sample input and output live under `samples/vendor-date-risk-audit`.
The sample package includes exact findings, business consequences, required fixes,
acceptance criteria, and runnable regression checks.

Run the local sample:

```bash
python scripts/vendor_audit/run_vendor_date_risk_audit.py --input samples/vendor-date-risk-audit/input_sample.csv --json-out samples/vendor-date-risk-audit/output_report_sample.json --md-out samples/vendor-date-risk-audit/output_report_sample.md
python -m pytest samples/vendor-date-risk-audit/regression_test_sample.py -q
```

The command generates machine-readable JSON and a Markdown report with invalid
dates, holiday mismatches, working-day mismatches, fiscal cutoff errors,
unsupported future assumptions, source conflicts, review-required cases,
recommendations, and a conformance score.

Suggested commercial packaging:

| Offer | Scope | Price guidance |
| --- | --- | --- |
| Free mini-audit | 50 rows | Free |
| Paid audit | vendor CSV and report | NPR 50,000-150,000 |
| Vendor monthly | continuous conformance suite | NPR 25,000/month or USD 200/month |
| Enterprise | private deployment and support | NPR 1.2M+/year |

The audit is source-aware technical review, not legal, tax, banking, payroll,
or government approval.

The initial prospect set and its extraction limits are documented in
`docs/outreach/IRD_VENDOR_PROSPECTS_2026.md`, with the 50-row working data in
`docs/outreach/ird_vendor_prospects_2026.csv`.

Status: audit checklist for external products that handle Nepali dates.

This checklist helps compare vendor behavior against Parva Protocol draft
expectations. It is not a certification program.

## Audit Areas

- Date conversion range and failure behavior
- Source citations and source-tier labels
- Future-date uncertainty labels
- Fiscal-year and compliance decision handling
- Holiday and observance source boundaries
- Evidence packet or trace availability
- Release manifest and artifact hash availability
- Offline verification support
- Human-review gates for payroll, banking, legal, and official-source claims
- Public claims and marketing language

## Required Evidence

Vendors should provide runnable examples, source citations, release version
metadata, documented error behavior, and a current compatibility report if they
claim compatibility with a Parva draft level.

## Red Flags

- Claims of official approval without an official source.
- Future calendar dates presented as final when the data is computed prediction.
- Silent fallback to low-confidence data.
- Private source use without a public/private data boundary.
- No reproducible release artifact or checksum trail.
