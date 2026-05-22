# Upstream Comment Drafts

These drafts are intentionally short. They should be posted only when the
linked Parva docs are public and the target issue is a good fit for a small
conformance note.

## opensource-nepal/go-nepali #15

Target: https://github.com/opensource-nepal/go-nepali/issues/15

Post now: not automatically. The issue is closed and current upstream behavior
appears fixed, so this is optional.

Reason: historical executable regression fixture.

Risk level: low.

Draft:

> Hi, I was collecting public Nepali date regression cases for Project Parva's conformance suite.
>
> I added this issue as a historical AD-to-BS boundary regression case because it captures the `2024-06-14` / `2081-02-32` boundary clearly.
>
> Current upstream behavior appears fixed in my local checkout, so no action is needed here. Sharing only in case the fixture is useful for future tests:
> https://github.com/dantwoashim/Project_Parva/blob/main/conformance/public-nepali-date-issues/conversion_cases.json
>
> The fixture is marked as a public regression case with an explicit authority boundary; it does not claim official date authority.

## opensource-nepal/node-nepali-datetime #82

Target: https://github.com/opensource-nepal/node-nepali-datetime/issues/82

Post now: later, if useful.

Reason: source-provenance conformance class with exact issue rows.

Risk level: medium, because the issue compares multiple sources and should not
be framed as choosing a winner.

Draft:

> Hi, I was collecting public Nepali date regression and source-provenance cases for Project Parva's conformance suite.
>
> I added this issue as a source-comparison case because it captures month table disagreement across sources for BS 2082-2088.
>
> No dependency or integration is required. Sharing in case it is useful for future tests or docs:
> https://github.com/dantwoashim/Project_Parva/blob/main/conformance/public-nepali-date-issues/source_drift_cases.json
>
> I kept it marked as reported source-provenance evidence, not as a final authority decision.

## opensource-nepal/node-nepali-datetime #121

Target: https://github.com/opensource-nepal/node-nepali-datetime/issues/121

Post now: later, if useful.

Reason: future BS review-needed evidence.

Risk level: low.

Draft:

> Hi, I was collecting public Nepali date regression and source-boundary cases for Project Parva's conformance suite.
>
> I added this issue as future-BS review-needed evidence because it clearly documents that future dates may change when source data is corrected.
>
> No dependency or integration is required. Sharing in case it is useful as a reference for future-date caveats:
> https://github.com/dantwoashim/Project_Parva/blob/main/conformance/public-nepali-date-issues/future_uncertainty_cases.json
>
> The fixture is deliberately non-executable and does not claim settled future-date authority.

## medic/bikram-sambat #26

Target: https://github.com/medic/bikram-sambat/issues/26

Post now: no.

Reason: issue is closed and exact correction rows are now preserved locally as a
historical benchmark.

Risk level: low.

Draft:

> Hi, I was collecting public Nepali date regression cases for Project Parva's conformance suite.
>
> I represented the correction rows from this issue as a historical month-length benchmark:
> https://github.com/dantwoashim/Project_Parva/blob/main/conformance/public-nepali-date-issues/month_length_cases.json
>
> No action needed here; sharing only if it is useful for future regression checks.

## leapfrogtechnology/nepali-date-picker #70

Target: https://github.com/leapfrogtechnology/nepali-date-picker/issues/70

Post now: no.

Reason: repo appears low-activity; Parva should use this as fixture evidence
without pushing for a PR.

Risk level: medium.

Draft:

> Hi, I was collecting public Nepali date regression cases for Project Parva's conformance suite.
>
> I represented the exact rows from this issue as public regression fixtures, with notes where issue-reported values and Parva's current table differ:
> https://github.com/dantwoashim/Project_Parva/blob/main/conformance/public-nepali-date-libraries/leapfrog_nepali_date_picker_2082_2083_cases.json
>
> No dependency or integration is required. Sharing only in case it is useful for future maintenance.

## yarsa/nepal-compliance #252

Target: https://github.com/yarsa/nepal-compliance/issues/252

Post now: no.

Reason: reproduction is not strong enough yet.

Risk level: high.

Draft:

> Hi, I was reviewing this as a payroll date-risk case.
>
> I am not posting a conclusion yet because I have not reproduced it in a full Frappe/bench environment. The public report is useful as an investigation target, but I would want a smaller reproduction before suggesting any change.
