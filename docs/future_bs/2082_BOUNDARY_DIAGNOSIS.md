---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-05
owner: research-team
---

# BS 2082 Boundary Diagnosis

## Observed Failure

The former broad-reference model predicted these adjacent month lengths for BS 2082:

```text
Ashadh 31 days
Shrawan 32 days
```

The verified BS 2082 calendar has:

```text
Ashadh 32 days
Shrawan 31 days
```

These were two visible conversion failures caused by one wrong month-start boundary. The incorrect boundary placed Shrawan 1 on 2025-07-16. The verified boundary is 2025-07-17.

## Missing Model Distinction

The ingress solver places the Karka solar ingress on 2025-07-16 at about 17:48 Nepal time. The former model treated modern physical ingress evidence as a direct proxy for the published civil calendar decision. That assumption was too strong.

The [official BS 2082 Panchanga](https://npns.gov.np/pages/the-year-of-2082-bs-3/) places Shrawan 1 on 2025-07-17. An [NPNS method notice](https://npns.gov.np/content/13/press-release-20251216/) also describes the current traditional Saurukta Panchanga practice and its relationship to alternative calculation methods. This establishes a method boundary: physical ingress and the official civil assignment are related inputs, yet they serve different roles.

## General Correction

Model `parva_authority_aware_solar_civil_v7` separates the evidence into two reusable towers:

1. The reference tower learns long-range solar-civil behavior from the broad historical corpus.
2. The authority tower learns civil decisions only from earlier verified official years.
3. Each tower receives equal total weight regardless of its number of internal rules.
4. A boundary vote combines both towers, with official support resolving an exact numerical tie.
5. Complete-year constraints require twelve months, month lengths from 29 through 32 days, and a 365- or 366-day year.

For the BS 2082 replay, training ends at BS 2081. Four earlier official years activate the authority tower. The trace for the Shrawan boundary is:

| Candidate start | Total support | Official-tower support | Reference-tower support |
| --- | ---: | ---: | ---: |
| 2025-07-16 | 0.957428 | 0.276193 | 0.681235 |
| 2025-07-17 | 1.042571 | 0.723806 | 0.318765 |

The selected boundary is 2025-07-17. The resulting year row is:

```text
[31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
```

The implementation contains one source-stratified rule for every target year. It contains no BS 2082 condition and no replacement lookup row.

## Validation Boundary

Chronological rolling validation over BS 2078-2083 produces 72 exact month matches from 72 official month cases. Every target year uses training data ending at the previous year. This six-year window also informed model development, so the result remains development-window evidence. Public forecasts remain `computed_prediction_not_official`, review-required, and subordinate to later official publication.
