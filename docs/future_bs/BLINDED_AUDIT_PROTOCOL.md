# Blinded Audit Protocol

Project Parva can review an external BS month-length assumption sheet without returning corrected future values by default.

The protocol is designed for risk screening, not for publishing a future calendar.

Every output is labeled:

```text
computed_prediction_not_official
```

## Purpose

The blinded audit answers aggregate questions:

- how many submitted month assumptions look low risk under the public alpha
- how many require review
- which years contain more disagreements
- whether any complete submitted year has a suspicious total
- how many rows are boundary-sensitive

It does not reveal Parva corrected month values in the default mode.

## Input Shape

The CSV input must include:

```text
bs_year,bs_month,month_length
```

Real external sheets may be used locally when authorized. Real client data, corrected future values, and private audit outputs must not be committed to the public repository.

## Default Output Shape

The default report contains aggregate fields only:

- total_months_checked
- agreement_count
- disagreement_count
- disagreement_distribution_by_year
- boundary_sensitive_count
- year_total_anomaly_count
- high_risk_month_count
- corrected_values_included: false

Agreement means compatibility with the public risk alpha. It is not a corrected-value match.

## Safety Boundary

The public alpha is a review layer. It does not replace official publication, institutional approval, or legal, tax, regulatory, or banking-contract review.
