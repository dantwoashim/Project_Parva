# Nepali Date Conformance Index

## Purpose

This index tracks public Nepali date and time failure classes that Project Parva
uses for conformance testing, benchmark design, and review planning.

The goal is practical: preserve small, reproducible public cases around BS/AD
conversion, month lengths, invalid dates, unsupported ranges, source drift,
future-date uncertainty, and workflow risk.

## What This Index Is

- A public evidence map for Nepali date/time regression classes.
- A source for reproducible conformance fixtures.
- A way to track failure classes across Nepali date libraries and Nepal-facing
  software.
- A way to distinguish verified cases, reported cases, partial reports, and
  narrative workflow evidence.

## What This Index Is Not

- Not a recognized public calendar authority for Nepal.
- Not a claim that listed projects are globally broken.
- Not proof of production impact unless the linked public source explicitly
  documents that impact.
- Not a replacement for official Panchanga, government publication, or
  institution-specific authority.
- Not a shame list.

## Evidence Levels

| Level | Meaning |
| --- | --- |
| `verified_public_issue` | Exact public input plus expected and/or actual behavior is available and represented as an executable or directly checkable fixture. |
| `reported_public_issue` | A public issue exists, but the expected or actual behavior may be partial or bounded. |
| `reported_public_issue_partial` | A public issue exists, but it lacks enough deterministic detail for executable use. |
| `narrative_evidence` | Public discussion or workflow pain, not an executable bug fixture. |
| `business_wedge` | Relevant business workflow evidence, not necessarily a bug. |
| `review_needed` | Requires manual validation before executable use. |

## Master Table

| ID | Source / repo | Issue / PR | Failure class | Evidence level | Exact input available? | Executable fixture? | Upstream status | Parva use | Safe claim |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `YARSA-257-258` | `yarsa/nepal-compliance` | [Issue #257](https://github.com/yarsa/nepal-compliance/issues/257), [PR #258](https://github.com/yarsa/nepal-compliance/pull/258) | Frontend/backend source drift | `verified_public_issue` | Yes | Yes | PR merged, merge commit `c220a9e` | Source-drift conformance fixture | Parva benchmark work contributed a merged standalone calendar consistency guard. |
| `LEAPFROG-70` | `leapfrogtechnology/nepali-date-picker` | [Issue #70](https://github.com/leapfrogtechnology/nepali-date-picker/issues/70) | Month-length mismatch | `reported_public_issue` | Partly, via existing local fixture | Documented in this suite; executable rows live in the older Leapfrog fixture | Open at time of local review | Month-length regression cluster | Parva tracks the issue as a public regression cluster. |
| `LEAPFROG-13` | `leapfrogtechnology/nepali-date-picker` | [Issue #13](https://github.com/leapfrogtechnology/nepali-date-picker/issues/13) | Conversion/range error | `verified_public_issue` | Yes | Yes | Public issue | AD-to-BS range-error fixture | Parva tracks the reported input and verifies its own bounded conversion behavior. |
| `LEAPFROG-33-35` | `leapfrogtechnology/nepali-date-picker` | Public issue references #33/#35 | April 2021 boundary conversion | `reported_public_issue_partial` | No | No | Public issue reports | Manual review target | These reports are tracked as boundary-conversion candidates. |
| `GO-NEPALI-15` | `opensource-nepal/go-nepali` | [Issue #15](https://github.com/opensource-nepal/go-nepali/issues/15) | AD-to-BS month-boundary mismatch | `verified_public_issue` | Yes | Yes | Public issue | Executable conversion fixture | Parva includes AD `2024-06-14` as a month-boundary regression case. |
| `MEDIC-BIKRAM-SAMBAT-26` | `medic/bikram-sambat` | [Issue #26](https://github.com/medic/bikram-sambat/issues/26) | 2081/2082 month-length correction | `reported_public_issue_partial` | Not in this repo yet | No | Public issue | Manual review target | Parva tracks it as month-length correction evidence. |
| `NODE-NEPALI-DATETIME-82` | `opensource-nepal/node-nepali-datetime` | [Issue #82](https://github.com/opensource-nepal/node-nepali-datetime/issues/82) | Source provenance / source disagreement | `reported_public_issue` | No | No | Public issue | Source-comparison benchmark | Parva tracks it as evidence that source provenance matters. |
| `NODE-NEPALI-DATETIME-121` | `opensource-nepal/node-nepali-datetime` | [Issue #121](https://github.com/opensource-nepal/node-nepali-datetime/issues/121) | Future BS uncertainty | `narrative_evidence` | No | No | Public issue | Future review-boundary evidence | Parva uses it to support review-needed future-date handling. |
| `CHT-CORE-7925` | `medic/cht-core` | [Issue #7925](https://github.com/medic/cht-core/issues/7925) | Invalid BS date accepted | `reported_public_issue` | Yes, bounded form | Yes | Public issue | Invalid date fixture | Parva checks that an invalid Kartik 2079 date shape is rejected. |
| `ODK-PRE-1951` | ODK forum / `medic/bikram-sambat` | Public discussion | Unsupported lower range | `reported_public_issue_partial` | No | No | Public discussion | Range-boundary evidence | Parva tracks it as lower-bound range evidence. |
| `SUBESHB1-71` | `subeshb1/Nepali-Date` | Public issue reference | Unsupported upper range | `reported_public_issue_partial` | No | No | Public issue reference | Range-boundary evidence | Parva tracks it as upper-range review evidence. |
| `ERPNEXT-31245` | `frappe/erpnext` | [Issue #31245](https://github.com/frappe/erpnext/issues/31245) | Business workflow gap | `business_wedge` | No | No | Public request | Workflow evidence | Parva tracks it as evidence that BS support matters in business software. |
| `FRAPPE-BOOKS-787` | `frappe/books` | [Issue #787](https://github.com/frappe/books/issues/787) | Business workflow gap | `business_wedge` | No | No | Public request | Workflow evidence | Parva tracks it as accounting workflow context. |

## Upstream Contribution Status

Yarsa `nepal-compliance` PR
[#258](https://github.com/yarsa/nepal-compliance/pull/258) was merged with
merge commit `c220a9e`.

Contribution type: standalone benchmark script.

What it checked:

- Backend CSV Nepali calendar table.
- Frontend JS Nepali calendar table.
- Supported range differences as informational.
- Overlapping month-length differences as failures.
- BS 2087 Mangsir source drift: backend CSV `29` days, frontend JS `30` days.

This is an upstream benchmark contribution inspired by Parva's conformance work.
It is not a dependency relationship, adoption claim, or production-impact claim.

## Safe Claims

- Project Parva's benchmark work contributed a standalone Nepali calendar source
  consistency guard to `yarsa/nepal-compliance`.
- Project Parva tracks public Nepali date regression cases as conformance
  fixtures.
- Some public issues show recurring failure classes around month lengths,
  conversion boundaries, invalid dates, unsupported ranges, and future-date
  uncertainty.

## Forbidden Claims

Do not claim:

- Yarsa changed its product to depend on Project Parva.
- Parva has recognized public calendar authority for Nepal.
- Listed projects are globally broken.
- Parva proves production payroll or invoices are wrong.
- Future BS dates are guaranteed.
