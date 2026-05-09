# Calendar Reconciliation Workflow

Parva can support a controlled workflow for reconciling official calendar updates against internal systems. This is a private deployment workflow, not a public future-calendar publication service.

## Workflow

1. An official or approved source is published.
2. Parva verifies and digitizes the source under the configured source policy.
3. A signed and versioned calendar release is generated.
4. A diff report compares the new release against the previous approved calendar state.
5. Affected BS years, months, date ranges, schedules, and records are flagged for review.
6. A webhook or notification can be sent to downstream systems.
7. The client or institution approves, rejects, or manually reviews the update under its own policy.
8. Downstream systems apply the approved version.

Parva should not silently update production databases without the operator's approval path.

## Example Event Types

- `calendar.official_release.verified`
- `calendar.risk_label.changed`
- `calendar.client_sheet.disagreement_detected`
- `calendar.month_boundary.review_required`

## Synthetic Webhook Example

```json
{
  "event_type": "calendar.month_boundary.review_required",
  "release_version": "public-example-001",
  "source_tier": "printed_verified",
  "affected_bs_year": 2090,
  "affected_months": ["synthetic_month_a"],
  "requires_review": true,
  "publication_status": "computed_prediction_not_official",
  "signature": "example-signature-placeholder"
}
```

The example is synthetic and does not contain real future month values.
