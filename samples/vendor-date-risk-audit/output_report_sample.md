# Vendor Date Risk Audit Sample

Status: sample output, not a certification.

## Invalid Dates

- `2082-13-01` should be rejected. Month 13 is invalid for public BS date
  handling.

## Holiday Mismatches

- `2082-01-01` requires source-aware holiday policy review before a vendor
  treats it as a non-working day.

## Working-Day Mismatches

- `2082-04-02` should be evaluated against the selected institution profile.

## Fiscal Cutoff Errors

- No fiscal cutoff error is proven in this sample. Final accounting behavior
  requires organization policy.

## Unsupported Future Assumptions

- `2090-01-01` must remain review-required. The sample must not infer an
  official future holiday or civil rule.

## Source Conflicts

- No conflicting source packet is attached in the sample input.

## Review-Required Cases

- Payroll, loan repayment, banking, tax, legal, and official-source decisions
  remain review-required unless the institution attaches its own source policy.

## Conformance Score

Sample score: 72/100.

This score is a technical sample only. It is not external certification,
government approval, customer proof, or legal approval.
