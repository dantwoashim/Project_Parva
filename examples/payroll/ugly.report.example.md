# Parva payroll date-risk audit

This report is decision support only. It is not legal, tax, payroll, banking, government, or official calendar authority.

- Rows: 7
- Review required: 6
- Pass: 1
- Conformance score: 14.29

## Findings

### 2082-01-02
- Status: pass
- AD date: 2025-04-15
- Issues: none
- Risk score: 0

### row 2
- Status: review_required
- AD date: unresolved
- Issues: missing_bs_date
- Risk score: 25

### 2082/01/99
- Status: review_required
- AD date: unresolved
- Issues: invalid_ad_date, invalid_bs_date
- Risk score: 50

### 2082-01-01
- Status: review_required
- AD date: 2025-04-14
- Issues: authority_overclaim, holiday_conflict, non_working_day_conflict, static_reference_overclaim
- Risk score: 100

### 2082-04-01
- Status: review_required
- AD date: 2025-07-17
- Issues: fiscal_boundary_ambiguity
- Risk score: 25

### 2082-12-01
- Status: review_required
- AD date: 2026-03-15
- Issues: holiday_assumption_requires_review, review_required_future_sensitive
- Risk score: 50

### 2082-12-01
- Status: review_required
- AD date: 2026-03-15
- Issues: duplicate_row, holiday_assumption_requires_review, review_required_future_sensitive
- Risk score: 75

## Forbidden claims

- No government authority.
- No legal, tax, payroll, or banking authority.
- No official future-date authority.
- No official Panchanga or ritual authority.
