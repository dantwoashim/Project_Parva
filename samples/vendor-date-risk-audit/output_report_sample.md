# Parva Vendor Date Risk Audit - Demonstration Report

This sanitized demonstration shows the audit deliverable for a software vendor. It is a technical conformance report, not certification or official authority.

## Executive Summary

- Rows: 6
- Rows with failures: 4
- Conformance score: 58.33
- Technical failures: 5
- Review controls: 1
- Critical findings: 1
- High findings: 3

The screening score subtracts one half-row penalty for each technical failure and floors at zero. Review controls are reported separately and do not reduce the score.

The sample contains an impossible BS month, a one-day dual-date mismatch, an unsupported future-date assumption, a source gap, and a fiscal-policy mismatch. Correct boundary rows are included to show that the audit distinguishes passing cases from failures.

## Finding Index

| ID | Severity | Category | BS date | Workflow |
| --- | --- | --- | --- | --- |
| PARVA-AUD-001 | CRITICAL | invalid dates | `2082-13-01` | payroll_cutoff |
| PARVA-AUD-002 | HIGH | working day mismatches | `2082-04-02` | attendance |
| PARVA-AUD-003 | HIGH | fiscal cutoff errors | `2082-04-01` | fiscal_period_start |
| PARVA-AUD-004 | HIGH | unsupported future assumptions | `2090-01-01` | loan_repayment |
| PARVA-AUD-005 | MEDIUM | source conflicts | `2090-01-01` | loan_repayment |
| PARVA-AUD-006 | ADVISORY | review required cases | `2090-01-01` | loan_repayment |

## Detailed Findings

Runnable equivalents are provided in `regression_test_sample.py`.

### PARVA-AUD-001: Invalid BS date reaches a business workflow

- Severity: CRITICAL
- Input: row 4, `2082-13-01`, `payroll_cutoff`
- Observed: Invalid BS date: 2082-13-01. Year must be 2000-2099, month 1-12, and day must be valid for that month.
- Expected: Reject the value before persistence, conversion, or workflow execution.
- Consequence: The affected payroll or invoice workflow can fail or store an impossible civil date.
- Required fix: Validate BS year, month, and day against the canonical month-length row at the input boundary.
- Regression check:

```python
with pytest.raises(ValueError):
    bs_to_gregorian(2082, 13, 1)
```

### PARVA-AUD-002: Stored AD and BS dates identify different civil days

- Severity: HIGH
- Input: row 6, `2082-04-02`, `attendance`
- Observed: Vendor AD value is 2025-07-19.
- Expected: 2082-04-02 converts to 2025-07-18.
- Consequence: Invoices, attendance, due dates, and sorted reports can move by one day.
- Required fix: Correct the stored AD value and enforce conversion plus round-trip checks before persistence.
- Regression check:

```python
assert bs_to_gregorian(2082, 4, 2).isoformat() == "2025-07-18"
```

### PARVA-AUD-003: Workflow uses the wrong fiscal-year convention

- Severity: HIGH
- Input: row 7, `2082-04-01`, `fiscal_period_start`
- Observed: Fiscal assumption is gregorian_calendar_year.
- Expected: Use the configured Nepal fiscal-year convention for the audited workflow.
- Consequence: Transactions can be assigned to the wrong reporting year at the Shrawan boundary.
- Required fix: Resolve fiscal periods through the shared fiscal engine instead of calendar-year logic.
- Regression check:

```python
assert fiscal_period_for_bs_date(2082, 4, 1).fiscal_year_label == "2082/83"
```

### PARVA-AUD-004: Future date is treated beyond the official source range

- Severity: HIGH
- Input: row 5, `2090-01-01`, `loan_repayment`
- Observed: Source status is static_table_unverified for 2090-01-01.
- Expected: Require an authoritative source or keep the result explicitly review-required.
- Consequence: A repayment or contractual date can appear final before an authoritative calendar is published.
- Required fix: Persist source status and block operational finalization until the authoritative release is available.
- Regression check:

```python
assert get_bs_year_provenance(2090).confidence != "official"
```

### PARVA-AUD-005: Holiday policy lacks a supported source

- Severity: MEDIUM
- Input: row 5, `2090-01-01`, `loan_repayment`
- Observed: Holiday assumption is unknown_future_holiday_policy.
- Expected: Attach a named source release and institution policy to the decision.
- Consequence: The workflow can skip or include the wrong working day without an auditable reason.
- Required fix: Require source ID, release ID, and institution profile before holiday adjustment.
- Regression check:

```python
assert audit_report["source_conflicts"]
```

### PARVA-AUD-006: Sensitive workflow requires human approval

- Severity: ADVISORY
- Input: row 5, `2090-01-01`, `loan_repayment`
- Observed: loan_repayment uses source status static_table_unverified.
- Expected: Hold final execution until a reviewer accepts the source and policy context.
- Consequence: Automatic execution would bypass the stated control for a sensitive workflow.
- Required fix: Enforce a review-required state and record reviewer identity, decision, and timestamp.
- Regression check:

```python
assert audit_report["review_required_cases"]
```

## Remediation Order

- Reject invalid BS dates before persistence or conversion.
- Reconcile stored AD dates against deterministic BS/AD conversion.
- Treat unsupported future or unverified source ranges as review_required.
- Attach source evidence for holiday and institution-specific assumptions.
- Require human review for sensitive payroll, repayment, banking, legal, or tax workflows.

## Acceptance Criteria

- Every critical and high regression check passes in CI.
- Stored AD and BS values round-trip to the same civil day.
- Invalid dates are rejected before persistence.
- Future and source-limited decisions remain review-required.
- Fiscal periods resolve through the configured Nepal fiscal policy.
