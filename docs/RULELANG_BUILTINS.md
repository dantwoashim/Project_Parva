---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# RuleLang Built-ins

RuleLang can call only allowlisted temporal functions backed by existing Project Parva services.

Current public built-ins:

| Function | Purpose |
|---|---|
| `convert_bs_to_ad` | Convert a BS date to an AD date |
| `convert_ad_to_bs` | Convert an AD date to a BS date |
| `validate_date` | Validate and normalize a date |
| `normalize_date` | Alias for date validation and normalization |
| `get_weekday` | Return AD weekday for a normalized date |
| `is_weekend` | Check profile-specific non-working day behavior |
| `is_working_day` | Check working-day status for a profile |
| `is_business_day` | Alias for working-day support |
| `is_holiday` | Check public-corpus fixed-date holiday behavior |
| `is_known_public_holiday` | Alias for public holiday check |
| `next_working_day` | Move to a later working day |
| `previous_working_day` | Move to an earlier working day |
| `add_days` | Add calendar days |
| `subtract_days` | Subtract calendar days |
| `add_working_days` | Add bounded working days |
| `last_day_of_nepali_month` | Return the last calendar day of a BS month |
| `first_day_of_nepali_month` | Return the first calendar day of a BS month |
| `last_working_day_of_nepali_month` | Return the last working day of a BS month |
| `get_month_length` | Return a BS month length |
| `get_fiscal_period` | Return Nepali fiscal period metadata |
| `get_fiscal_year` | Fiscal helper backed by fiscal-period logic |
| `confidence_at_least` | Compare confidence labels |
| `requires_human_review` | Return review status for a date or current context |
| `fact_is_disputed` | Check whether a TimeGraph fact participates in a conflict |

Unsupported functions are rejected during validation.

Forbidden function names such as `eval`, `exec`, `shell`, `open`, `import`, and `os.environ` are rejected.

## Confidence Labels

RuleLang uses Project Parva confidence labels:

- `official_verified`
- `source_backed`
- `calculated`
- `research_preview`
- `fixture`
- `unsupported`
- `unknown`

Weak confidence can force review or blocking depending on the rule risk policy.
