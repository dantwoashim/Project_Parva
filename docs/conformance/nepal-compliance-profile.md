# Nepal Compliance Conformance Profile

## Purpose

This profile is for Nepal-facing ERP, accounting, payroll, and compliance
systems that handle Bikram Sambat and Gregorian dates in user-visible workflows.

It gives Project Parva a focused way to group public regression cases around
source drift, payroll date risk, fiscal boundaries, invalid dates, and
review-needed future BS data.

## What It Checks

- Frontend/backend calendar source consistency.
- BS month-length validation.
- BS/AD conversion and roundtrip-sensitive boundaries.
- Invalid BS date rejection.
- Fiscal year boundary classification.
- Payroll month duration review.
- Future BS review-needed classification.
- Holiday and working-day data hooks for future source-backed fixtures.

## Evidence Basis

- Yarsa issue #257 and PR #258: a merged standalone calendar source consistency
  benchmark for duplicated frontend/backend BS month tables.
- Yarsa issue #252: a reported payroll date-risk case around Asoj month duration;
  this remains an investigation target until a Frappe reproduction is available.
- ERPNext #31245 and Frappe Books #787: business workflow evidence that BS support
  matters for Nepal-facing accounting systems.
- Public issue fixtures under `conformance/public-nepali-date-issues/`.

## How To Run

Run the full public issue suite:

```powershell
py -3.11 tools\conformance_runner\run.py --suite public-nepali-date-issues
```

Run this profile:

```powershell
py -3.11 tools\conformance_runner\run.py --profile nepal-compliance
```

## What This Profile Does Not Claim

- It is not legal, tax, payroll, or banking authority.
- It is not recognized public calendar authority for Nepal.
- It is not proof of production impact unless an upstream issue documents that
  impact directly.
- It is not a replacement for official review, source publication, or maintainer
  judgment.
