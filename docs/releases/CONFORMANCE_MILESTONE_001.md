# Project Parva Conformance Milestone 001

## Summary

Project Parva now has a public Nepali date issue conformance foundation:
schema-backed public issue fixtures, a runner for executable and documented-only
cases, benchmark docs, a Yarsa source-drift case study, an upstream action plan,
and a Nepal compliance profile.

## Why It Matters

Nepali date correctness is not only a conversion problem. Public issue evidence
shows recurring risks around duplicated source tables, month-length drift,
conversion boundaries, invalid dates, unsupported ranges, future BS uncertainty,
and payroll or fiscal workflow assumptions.

This milestone turns those public cases into a restrained conformance program:
exact cases can run, partial cases stay marked for review, and business cases
do not become authority claims.

## What Is Included

- Public issue conformance index.
- Fixture schema and category fixture packs.
- Conformance runner support for `public-nepali-date-issues`.
- Profile runner support for `nepal-compliance`.
- Yarsa source-drift case study.
- Nepal compliance conformance profile.
- Upstream public issue action plan.
- Benchmark documentation for public failure classes.
- Public-safe outreach drafts.

## Evidence Categories

- Frontend/backend source drift.
- Month-length mismatch and correction rows.
- Conversion boundary mismatch.
- Invalid BS dates.
- Unsupported lower and upper ranges.
- Future BS uncertainty.
- Fiscal, payroll, and business workflow evidence.

## Validation

Expected final validation commands:

```powershell
py -3.11 -m pytest tests/conformance -q
py -3.11 tools\conformance_runner\run.py --suite public-nepali-date-issues
py -3.11 tools\conformance_runner\run.py --profile nepal-compliance
py -3.11 tools\conformance_runner\run.py
py -3.11 scripts\check_docs_links.py
py -3.11 scripts\release\check_public_claims.py
py -3.11 scripts\release\verify_public.py
py -3.11 -m ruff check .
```

These commands should pass before this milestone is treated as published.

## Safe Claims

- Project Parva tracks public Nepali date regression cases as conformance
  fixtures.
- Project Parva's benchmark work contributed a standalone calendar source
  consistency guard to `yarsa/nepal-compliance`.
- Project Parva distinguishes verified, reported, partial, narrative,
  business-workflow, and review-needed evidence.
- Project Parva can run a public issue conformance suite and a Nepal compliance
  profile locally.

## Forbidden Claims

Do not claim:

- An upstream project depends on Project Parva unless that is explicitly true.
- Project Parva has recognized public calendar authority for Nepal.
- Listed projects are globally broken.
- A public issue proves production payroll, invoices, or compliance outputs are
  wrong.
- Future BS dates are guaranteed.
- The Nepal compliance profile is legal, tax, payroll, or banking authority.

## Next Targets

- `opensource-nepal/node-nepali-datetime` #82 and #121.
- `opensource-nepal/go-nepali` #15 historical regression coverage.
- `medic/bikram-sambat` #26 correction-row comparisons.
- `leapfrogtechnology/nepali-date-picker` #70 fixture tightening.
- Yarsa #252 only after a concrete payroll reproduction exists.
