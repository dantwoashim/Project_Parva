# Project Parva for InfoDevelopers

## What Project Parva Is

Project Parva is a developer API for Nepali calendar computation. For InfoDevelopers, the most relevant use case is validation and standardization of BS date logic across financial systems.

## Why InfoDevelopers May Care

Financial systems need consistent BS/AD conversion, month length handling, fiscal-year boundaries, and regression checks across many products. Parva can help evaluate those date rules with a repeatable API and validation report workflow.

## Relevant Product Areas

- Core banking
- Cooperative and microfinance systems
- Reconciliation systems
- HRIS and payroll
- Budget and fiscal reporting
- Financial statements and ledgers

## Current Stable Capabilities

- BS to AD conversion
- AD to BS conversion
- BS month length lookup
- fiscal-year boundary derivation
- bulk conversion
- validation suite

## Evaluation-Ready Endpoints

- `/v3/api/calendar/convert`
- `/v3/api/calendar/bs-to-gregorian`
- `/v3/api/calendar/convert/compare`
- `/v3/api/enterprise/fiscal-year/{bs_year}`
- `/v3/api/enterprise/bs-months/{bs_year}`
- `/v3/api/enterprise/bulk-convert`
- `/v3/api/enterprise/validate`

## Proposed First Step

Technical validation against InfoDevelopers internal known test cases.

## Correct Positioning

Project Parva should be considered as:

- validation reference
- regression test suite
- private deployable calendar service
- integration layer after review

## What Parva Is Not

- not an immediate replacement for existing internal systems
- not a legal/tax final authority
- not production financial infrastructure without validation

## Suggested Next Step

InfoDevelopers can provide 20 to 50 known edge cases for comparison. The cases can be run through the validation suite to generate a mismatch report and a shared technical baseline.
