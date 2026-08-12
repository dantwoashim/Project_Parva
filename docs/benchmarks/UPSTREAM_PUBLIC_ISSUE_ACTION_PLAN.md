# Upstream Public Issue Action Plan

## Purpose

This plan records which public Nepali date issues Project Parva has reviewed,
which ones are represented as fixtures, and which upstream actions are safe.

The goal is to keep outreach small and useful: verified cases become fixtures,
partial cases stay marked for review, and comments or PRs happen only when they
help maintainers without adding pressure or dependency.

## Target Summary

| Target | Status | Evidence level | Parva action | Upstream action |
|---|---|---:|---|---|
| opensource-nepal/go-nepali #15 | Closed; current checkout fixed | Verified exact issue | Historical executable regression fixture | Comment posted; tiny regression-test PR opened |
| opensource-nepal/node-nepali-datetime #82 | Public source rows available | Reported public issue | Source-provenance fixture with exact issue rows | Draft comment only |
| opensource-nepal/node-nepali-datetime #121 | Open known issue | Narrative evidence | Future BS review-needed fixture | Comment posted; no PR opened |
| medic/bikram-sambat #26 | Closed with PR #27 | Reported public issue | Exact correction rows preserved | No comment unless useful later |
| leapfrogtechnology/nepali-date-picker #70 | Open; repo appears low-activity | Reported public issue | Fixture-only benchmark evidence | Draft comment only |
| yarsa/nepal-compliance #252 | Open; reproduction incomplete | Business wedge | Payroll date-risk investigation target | No comment yet |

## Verified Exact Cases

- `go-nepali-15-2024-06-14-ad-to-bs-boundary`
  - Public issue reports AD `2024-06-14` was returned as BS `2081-03-01`
    while the reporter expected BS `2081-02-32`.
  - Current upstream checkout `e85acd1` returns BS `2081-02-32`, so this is
    treated as a fixed historical regression fixture.
- `medic-bikram-sambat-26-2081-2082-month-corrections`
  - Public issue lists exact incorrect and correct month-day rows for BS 2081
    and 2082.
  - Upstream issue is closed with PR #27, so Parva stores the rows as a
    historical month-length correction benchmark.
- `leapfrog-70-2082-2083-month-length-cluster`
  - Public issue lists exact rows for BS 2082 and 2083 month-length and
    weekday drift reports.
  - Existing Parva fixtures preserve issue-reported rows and distinguish rows
    that do not match Parva's current table.

## Partial Or Review-Needed Cases

- `node-nepali-datetime-82-source-provenance`
  - Public issue lists source rows for current data, Hamro Patro, and Nepali
    Patro across BS 2082-2088.
  - Parva stores these as source-comparison evidence, not as a final authority
    decision.
- `node-nepali-datetime-121-future-date-accuracy`
  - Public issue explicitly states that future BS dates may change when source
    data changes.
  - Parva uses this as evidence for review-needed future-date boundaries.
- `yarsa-252-payroll-asoj-month-duration`
  - Public issue reports monthly payroll for Asoj pulling 30 days where the
    reporter expected 31.
  - Local inspection found payroll/date conversion code paths, but a full
    Frappe reproduction was not run.

## Recommended Upstream Action

| Target | Recommendation | Reason |
|---|---|---|
| go-nepali #15 | Comment posted; regression-test PR opened | Already fixed upstream; current tests did not include the exact AD `2024-06-14` to BS `2081-02-32` boundary from issue #15. The PR is test-only and does not request a dependency or integration. |
| node-nepali-datetime #82 | Comment draft only | Useful source-provenance evidence; no need to choose a canonical source upstream. |
| node-nepali-datetime #121 | Comment posted | Aligns with review-needed future date language. No PR, dependency, or integration was requested. |
| medic/bikram-sambat #26 | No action now | Closed and represented as historical evidence. |
| Leapfrog #70 | Fixture only | Repo appears low-activity; avoid low-value PR churn. |
| Yarsa #252 | Manual verification required | Do not comment until a concrete reproduction exists. |

## Risks And Boundaries

- Public issues are evidence, not official calendar source material by
  themselves.
- A fixture does not prove production impact.
- A merged standalone benchmark contribution does not mean an upstream project
  depends on Project Parva.
- Future BS cases must stay review-needed unless source coverage supports a
  stronger claim.
- Payroll and compliance cases are decision-support evidence, not legal, tax,
  payroll, or banking determinations.

## Day 3 Posted Comments Status

- `opensource-nepal/go-nepali #15`
  - Upstream comment: posted
  - Comment URL: <https://github.com/opensource-nepal/go-nepali/issues/15#issuecomment-4522000828>
  - Status: historical regression fixture; current upstream behavior appears fixed.
  - Upstream PR: opened
  - PR URL: <https://github.com/opensource-nepal/go-nepali/pull/34>
  - Assessment: [go-nepali issue #15 regression PR assessment](../research/go-nepali-15-regression-pr-assessment.md)
  - Notes: the comment records the issue as public AD to BS conversion boundary
    regression evidence for Parva's conformance suite. The PR adds only a
    regression test for the already-fixed boundary case. No dependency,
    integration, maintainer approval, or authority claim was made.
- `opensource-nepal/node-nepali-datetime #121`
  - Upstream comment: posted
  - Comment URL: <https://github.com/opensource-nepal/node-nepali-datetime/issues/121#issuecomment-4524796914>
  - Status: public future-BS uncertainty and review-needed conformance evidence.
  - Upstream PR: not opened
  - Notes: the comment records the issue as public conformance evidence for
    review-needed future-date boundaries. No dependency, integration,
    maintainer approval, or authority claim was made.

## Day 4 Follow-Up Targets

- Keep Yarsa #252 as the next careful reproduction target.
- If a Frappe/bench environment is available, reproduce the Asoj payroll period
  issue before any upstream comment or PR.
- Convert any verified Yarsa #252 reproduction into a small payroll date-risk
  fixture before proposing upstream action.
