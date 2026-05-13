# Enterprise Compliance Preview

Project Parva includes a minimal enterprise temporal compliance layer for source-aware decision support.

It helps organizations ask operational calendar questions without treating computed output as legal authority.

## What It Answers

- Is this date a working day for a profile?
- What is the next or previous working day?
- What date results after adding working days?
- What is the last working day of a BS month?
- What fiscal period does this date belong to?
- Does this decision require human review?
- What source, confidence, data version, warning, and claim boundary support the answer?

## Claim Boundary

Compliance responses are decision support only.

They are not:

- official government calendar publication
- legal authority
- tax authority
- banking-contract authority
- payroll final authority
- institution-specific closure policy

Official publications, institution-approved policy, and human review override Parva compliance-preview output.

The compliance claim boundary is:

```text
enterprise_decision_support_not_legal_authority
```

## Built-In Profiles

| Profile | Status | Scope |
|---|---|---|
| `nepal_public_general` | preview public corpus | Saturday weekend logic, fixed-date public corpus observances, Nepali fiscal periods |
| `nepal_government_general` | limited, official review required | Saturday weekend logic, official holiday source required |
| `nepal_banking_general` | limited, official review required | Saturday weekend logic, banking holiday source required |
| `nepal_private_company_default` | preview public corpus | Saturday weekend logic, fixed-date public corpus observances, Nepali fiscal periods |
| `nepal_school_general` | limited, institution review required | Saturday weekend logic, academic closure policy not bundled |
| `custom_demo_company` | synthetic demo | Saturday and Sunday weekends for integration testing only |

The public demo does not bundle a complete authoritative government, banking, school, province, municipality, or organization-specific holiday calendar.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v3/api/compliance/profiles` | List built-in compliance profiles and reason codes |
| `GET /v3/api/compliance/profiles/{profile_id}` | Return one profile definition |
| `POST /v3/api/compliance/evaluate-date` | Evaluate one BS or AD date |
| `POST /v3/api/compliance/next-working-day` | Find the next working day with a bounded search |
| `POST /v3/api/compliance/previous-working-day` | Find the previous working day with a bounded search |
| `POST /v3/api/compliance/add-working-days` | Add or subtract working days with bounded iteration |
| `POST /v3/api/compliance/month-closing-day` | Return the last calendar day and last working day of a BS month |
| `POST /v3/api/compliance/fiscal-period` | Return Nepali fiscal year, fiscal month, and quarter |

The lightweight public demo route profile may exclude these endpoints. They are available in the full public or private deployment profile.

## Request Shape

Most date-evaluation endpoints accept exactly one of `bs_date` or `ad_date`.

```json
{
  "profile_id": "nepal_private_company_default",
  "bs_date": "2082-04-02"
}
```

## Response Shape

```json
{
  "profile_id": "nepal_private_company_default",
  "date": {
    "bs": "2082-04-02",
    "ad": "2025-07-17"
  },
  "decision": {
    "is_working_day": true,
    "is_business_day": true,
    "is_payroll_safe": true,
    "requires_human_review": false,
    "reason_codes": ["WEEKDAY", "NO_MATCHING_PUBLIC_HOLIDAY"],
    "holiday": null
  },
  "fiscal_period": {
    "fiscal_year_label": "2082/83",
    "fiscal_month": 1,
    "fiscal_quarter": 1
  },
  "meta": {
    "confidence": "official_verified",
    "claim_boundary": "enterprise_decision_support_not_legal_authority",
    "warnings": ["not_legal_tax_or_banking_contract_authority"],
    "trace_id": "request-trace-id"
  }
}
```

## Reason Codes

| Code | Meaning |
|---|---|
| `WEEKDAY` | The date is not configured as a non-working weekday for the profile |
| `WEEKEND` | The date is configured as non-working for the profile |
| `SATURDAY_NON_WORKING` | Saturday is non-working for the profile |
| `PUBLIC_HOLIDAY_MATCH` | A public-corpus fixed-date observance matched the BS date |
| `BANKING_HOLIDAY_SOURCE_NOT_AVAILABLE` | Banking holiday source data is not bundled |
| `PROFILE_REQUIRES_OFFICIAL_SOURCE` | The profile requires official source review before operational use |
| `SOURCE_CONFIDENCE_TOO_LOW` | The source confidence is below profile policy |
| `OUTSIDE_SUPPORTED_RANGE` | The date is outside supported calendar range |
| `RESEARCH_PREVIEW_BLOCKED` | Research-preview data is blocked by profile policy |
| `FUTURE_DATE_REVIEW_REQUIRED` | The profile requires review for future-dated decisions |
| `NO_MATCHING_PUBLIC_HOLIDAY` | No fixed-date public-corpus holiday matched |
| `FISCAL_YEAR_BOUNDARY` | The date is BS Shrawan 1, the start of a Nepali fiscal year |
| `PAYROLL_REVIEW_REQUIRED` | Payroll-style use requires stronger source and policy review |

## Working-Day Search Bounds

Working-day search is bounded to prevent accidental unbounded loops.

- Next and previous working-day search: 370 days maximum.
- Add or subtract working days: 366 working days maximum.

Unsupported inputs return structured 4xx errors.

## Source Confidence

Compliance responses propagate Layer 3 metadata:

- source
- confidence
- data version
- claim boundary
- warnings
- trace id

If profile policy requires stronger evidence than the public corpus provides, the response sets `requires_human_review` to `true` and includes reason codes such as `PROFILE_REQUIRES_OFFICIAL_SOURCE` or `SOURCE_CONFIDENCE_TOO_LOW`.

## SDKs

The alpha JavaScript and Python SDKs expose helpers for:

- list profiles
- get profile
- evaluate date
- next working day
- previous working day
- add working days
- month closing day
- fiscal period

SDKs return the raw response object so callers can inspect `decision`, `reason_codes`, and `meta`.
