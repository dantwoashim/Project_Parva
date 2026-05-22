# Public Nepali Date Library Regression Cases

## Purpose

Project Parva keeps a small public regression corpus for recurring Nepali date
failure classes seen in open-source libraries. These fixtures are conformance
examples, not authority claims.

The goal is to make month-day, BS/AD conversion, invalid-date, and off-by-one
issues easier to reproduce and prevent.

## Why Public Regression Cases Matter

Public issues are useful because they show where ordinary library users notice
date behavior changing in real workflows. A fixture derived from a public issue
can preserve the failure class even if the original repository is inactive or
does not merge a fix.

Each case keeps the source issue report separate from Parva's own expected
behavior. Public issue text is evidence of a reported regression, not a source
of official calendar authority.

## Leapfrog `nepali-date-picker` Issue Summary

Repository: <https://github.com/leapfrogtechnology/nepali-date-picker>

Inspected commit: `bce7cdaa155a6ec389a7a227eb4295fb392135a6`

Package version: `2.0.2`

Calendar data source inspected: `src/nepaliDatePicker.js`

Supported BS range in the current source: `1970-2100`

Issues reviewed:

| Issue | Status | Extracted result |
| --- | --- | --- |
| [#66](https://github.com/leapfrogtechnology/nepali-date-picker/issues/66) | Open | Broad BS 2082 month-day report; not enough detail for a deterministic case. |
| [#68](https://github.com/leapfrogtechnology/nepali-date-picker/issues/68) | Open | Broad BS 2082 month-day report; not enough detail for a deterministic case. |
| [#69](https://github.com/leapfrogtechnology/nepali-date-picker/issues/69) | Open | Off-by-one candidate for AD `2025-05-19`, using the issue creation date because the body says "today". |
| [#70](https://github.com/leapfrogtechnology/nepali-date-picker/issues/70) | Open | Concrete BS 2082 and 2083 month-day reports. |

## Cases Extracted

The committed fixture is:

`conformance/public-nepali-date-libraries/leapfrog_nepali_date_picker_2082_2083_cases.json`

It includes:

- BS 2082 month-day reports for Baisakh, Jestha, Asar, Shrawan, Asoj, Mangsir,
  Poush, and Magh.
- BS 2083 month-day reports for Asoj, Mangsir, Poush, and Magh.
- One AD-to-BS off-by-one candidate for issue #69.

The fixture records:

- issue-reported expected values,
- current Leapfrog source behavior reproduced locally,
- Parva's current expected behavior,
- whether the issue-reported value matches Parva's current table,
- a public-issue authority boundary.

Two issue #70 rows, BS 2082 Asar and BS 2082 Shrawan, are intentionally marked
as issue evidence requiring review because the issue-reported month days do not
match Parva's current table.

## Cases Reproduced

Using the current Leapfrog source, the following examples still reproduce as
reported in issue #70:

- BS 2082 Baisakh: issue reports 31 days; current source returns 30.
- BS 2082 Jestha: issue reports 31 days; current source returns 32.
- BS 2082 Mangsir: issue reports 29 days; current source returns 30.
- BS 2082 Poush: issue reports 30 days; current source returns 29.
- BS 2082 Magh: issue reports 29 days; current source returns 30.
- BS 2083 Asoj: issue reports 31 days; current source returns 30.
- BS 2083 Mangsir: issue reports 29 days; current source returns 30.
- BS 2083 Poush: issue reports 30 days; current source returns 29.
- BS 2083 Magh: issue reports 29 days; current source returns 30.

Issue #69 is represented as a bounded candidate: the issue says "today" was
Jestha 5 Monday and was opened on AD `2025-05-19`; the current source returns
BS `2082-02-06` for that AD date while Parva returns BS `2082-02-05`.

## Cases That Need More Detail

Issues #66 and #68 report incorrect BS 2082 month days but do not list exact
month-day values. They are useful as public evidence of the failure class, but
not enough by themselves for deterministic conformance cases.

Issue #70 includes day-name ranges for Kartik 2082 and Kartik 2083. Those are
kept in the issue summary for now; they should become fixture cases only after
the exact date/day mapping is represented in a deterministic input/output form.

## What Parva Checks

The Parva conformance runner now loads the Leapfrog public regression fixture
and checks:

- fixture shape,
- public-issue authority boundary,
- no production-impact claim,
- Parva's month-day values for represented month cases,
- Parva's AD-to-BS result for the issue #69 candidate.

The tests also ensure public issue cases remain labeled as `needs_review`.

## What Parva Does Not Claim

These fixtures do not claim:

- official calendar authority,
- production impact in Leapfrog or downstream projects,
- that every issue-reported expected value is correct,
- that Leapfrog should replace its implementation,
- that Parva is a dependency for Leapfrog.

They are public regression examples for conformance and review.

## How To Add New Public Regression Cases

1. Link the public issue or discussion.
2. Extract only concrete inputs and outputs.
3. Reproduce current library behavior locally when practical.
4. Keep issue-reported values separate from Parva expected behavior.
5. Mark vague reports as insufficient detail.
6. Preserve `public_issue_regression_case_not_official_authority`.
7. Add a focused test that proves the fixture is loaded and bounded.
