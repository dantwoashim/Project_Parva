# Yarsa #252 Payroll Date-Risk Investigation

## Issue Summary

Yarsa issue #252 reports that when creating monthly payroll for Asoj, the
system automatically pulls 30 days even though the reporter expects 31 days.

Issue: https://github.com/yarsa/nepal-compliance/issues/252

## Public Evidence Available

- Issue title: `wrong nepali date pulled in payroll`
- Public symptom: monthly payroll for Asoj pulls 30 days.
- Public expected value: Asoj has 31 days in the reported case.
- Public reproduction steps: create payroll entry for Asoj.
- Missing detail: exact BS year, company setup, payroll period configuration,
  salary slip dates, Frappe/HRMS version details in text form, and expected
  final AD date.

## Code Paths Inspected

Clean upstream research checkout:

- Repository: `https://github.com/yarsa/nepal-compliance`
- Branch inspected: `develop`
- Commit inspected: `ce78338`

Relevant paths:

- `nepal_compliance/public/js/salary_slip.js`
- `nepal_compliance/overrides/salary_slip.py`
- `nepal_compliance/nepali_date_utils/nepali_date.py`
- `nepal_compliance/nepali_date_utils/data/nepali_calendar.csv`
- `nepal_compliance/public/js/nepali_date_lib.js`
- `nepal_compliance/public/js/nepali_date_override.js`
- `nepal_compliance/public/js/report_filter.js`
- `nepal_compliance/custom_code/payroll/`

Observed code signals:

- `salary_slip.js` wraps calls to
  `hrms.payroll.doctype.payroll_entry.payroll_entry.get_end_date` and restores
  selected salary components after end-date changes.
- Salary Slip UI fields convert `start_date` and `end_date` through
  `NepaliFunctions.AD2BS` and `NepaliFunctions.BS2AD`.
- Backend conversion uses `nepali_date_utils/nepali_date.py` and the backend CSV
  calendar data.
- Frontend conversion uses the bundled JS Nepali date library.

## Reproduction Attempt

A full runtime reproduction was not completed because this environment does not
have a configured Frappe/bench site with HRMS payroll data.

Static inspection confirmed plausible payroll/date-conversion paths, but static
inspection alone is not enough to classify this as a confirmed runtime bug.

## Result

Status: insufficient public detail for executable reproduction.

The issue is represented in Project Parva as:

- Failure class: `payroll_date_risk`
- Evidence level: `business_wedge`
- Executable: `false`
- Recommended action: manual verification required

## Failure Class

Payroll date-risk / month-duration mismatch.

This class covers cases where business workflows depend on BS month duration,
BS/AD conversion, payroll period end dates, or source-backed month-length
tables.

## Parva Fixture Recommendation

Keep `yarsa-252-payroll-asoj-month-duration` as a non-executable public issue
case until a minimal reproduction exists.

Before making it executable, collect:

- BS year and month.
- Payroll start and end dates.
- Expected AD start and end dates.
- Actual AD start and end dates.
- Whether the value came from frontend, backend, or HRMS payroll logic.
- Frappe/ERPNext/HRMS and nepal-compliance versions.

## Upstream Action Recommendation

Do not comment or open a PR yet.

A useful next step would be a tiny standalone reproduction or consistency check
that demonstrates the date source used by the payroll end-date path. Without
that, a comment would be premature.

## Safe Claim

Yarsa issue #252 is a reported payroll date-risk case that Project Parva tracks
as an investigation target.

## Forbidden Claim

Do not claim the issue is confirmed, do not claim payroll authority, and do not
claim production impact beyond the public issue text.

## Next Step

Set up a Frappe/bench reproduction environment or ask for the exact BS year,
payroll period dates, and generated start/end dates before proposing upstream
action.
