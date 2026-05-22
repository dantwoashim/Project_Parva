# Public Nepali Date Failure Classes

## Purpose

Project Parva uses public issue reports to design conformance checks. The point
is not to rank projects. The point is to preserve concrete failure classes that
Nepali date software should be able to detect, explain, or safely mark for
review.

## Failure Class 1: Frontend/Backend Source Drift

Primary example: `yarsa/nepal-compliance`
[Issue #257](https://github.com/yarsa/nepal-compliance/issues/257) and
[PR #258](https://github.com/yarsa/nepal-compliance/pull/258).

Project Parva's benchmark work contributed a merged standalone consistency
guard to `yarsa/nepal-compliance`.

The source-drift fixture records:

- BS 2087 Mangsir.
- Backend CSV: `29` days.
- Frontend JS table: `30` days.
- Shift examples produced by the upstream benchmark script:
  - BS `2088-01-01`: backend AD `2031-04-15`, frontend AD `2031-04-16`.
  - BS `2089-12-30`: backend AD `2033-04-13`, frontend AD `2033-04-14`.

This demonstrates why duplicated calendar tables need consistency checks.

## Failure Class 2: Month-Length Matrix Drift

Examples:

- `leapfrogtechnology/nepali-date-picker`
  [Issue #70](https://github.com/leapfrogtechnology/nepali-date-picker/issues/70)
- `medic/bikram-sambat`
  [Issue #26](https://github.com/medic/bikram-sambat/issues/26)
- `opensource-nepal/node-nepali-datetime`
  [Issue #82](https://github.com/opensource-nepal/node-nepali-datetime/issues/82)

These cases are useful because BS month lengths are compact data, but small
table differences can shift later conversions. Public issue text is not
automatically authority. Exact rows should be represented separately from
Parva's current expected behavior.

## Failure Class 3: BS/AD Boundary Conversion Mismatch

Examples:

- `opensource-nepal/go-nepali`
  [Issue #15](https://github.com/opensource-nepal/go-nepali/issues/15):
  AD `2024-06-14`, expected BS `2081-02-32`, actual BS `2081-03-01`.
  Current upstream checkout `e85acd1` returns BS `2081-02-32`, so Parva keeps
  this as a fixed historical regression fixture.
- Leapfrog issue references #33/#35 around April 2021 boundary behavior, kept
  as partial until exact rows are verified.

Boundary cases matter because a one-day or one-month rollover error can look
valid while still changing the user's intended date.

## Failure Class 4: Invalid BS Date Acceptance

Example:

- `medic/cht-core`
  [Issue #7925](https://github.com/medic/cht-core/issues/7925)

The represented fixture checks a bounded invalid date shape such as
`99 Kartik 2079`. Parva treats this as an invalid-date validation case, not as a
claim about every upstream date flow.

## Failure Class 5: Unsupported Range Boundaries

Examples:

- ODK / `medic/bikram-sambat` lower-bound discussion around DOB values before
  1951.
- `subeshb1/Nepali-Date` upper-range issue above BS `2090-12-30`.

These are currently documented-only until exact public inputs and expected
outcomes are represented.

## Failure Class 6: Future BS Uncertainty

Example:

- `opensource-nepal/node-nepali-datetime`
  [Issue #121](https://github.com/opensource-nepal/node-nepali-datetime/issues/121)

Future-facing Nepali date data can depend on publication status and source
availability. Parva uses these cases to test review-needed behavior and to avoid
treating unsupported future dates as settled output.

## Failure Class 7: Fiscal, Payroll, and Business Workflow Risk

Examples:

- `yarsa/nepal-compliance`
  [Issue #252](https://github.com/yarsa/nepal-compliance/issues/252), tracked
  as reported payroll date-risk evidence around Asoj month duration. This is not
  executable until reproduced in a Frappe/bench environment.
- `frappe/erpnext`
  [Issue #31245](https://github.com/frappe/erpnext/issues/31245)
- `frappe/books`
  [Issue #787](https://github.com/frappe/books/issues/787)

These are business workflow signals, not executable bug fixtures. They show
that Nepali date support appears in accounting, fiscal-year, invoice, and
workflow contexts. They do not establish production impact by themselves.

These cases should be used as workflow evidence and conformance design input,
not as legal, tax, payroll, or production-impact conclusions.

## What Parva Does Not Claim

Parva does not claim:

- recognized public calendar authority for Nepal,
- government, legal, tax, payroll, banking, or ritual authority,
- that listed projects are globally broken,
- production impact unless a public source explicitly documents it,
- that public issue reports are official source material,
- that future BS dates are guaranteed.

## How To Contribute New Public Cases

Add a new case only when the following are clear:

- issue or discussion URL,
- input,
- expected behavior if available,
- actual behavior if available,
- source status,
- evidence level,
- authority boundary,
- whether the case is executable or documented-only.

When exact values are missing, mark the case as `reported_public_issue_partial`
or `review_needed` and keep it out of executable checks.
