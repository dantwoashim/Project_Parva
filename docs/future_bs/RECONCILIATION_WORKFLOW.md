---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Calendar Reconciliation Workflow

Parva can support a controlled workflow for reconciling official calendar updates, reviewed source changes, and internal temporal assumptions against downstream systems.

This is a review workflow. It is not a public future-calendar publication service.

## Workflow

1. An official, reviewed, or approved source is published.
2. Parva verifies and digitizes the source under the configured source policy.
3. A signed and versioned calendar release is generated.
4. A diff report compares the new release against the previous approved calendar state.
5. Affected BS years, months, date ranges, schedules, and records are flagged for review.
6. A webhook or notification can be sent to downstream systems.
7. The operator approves, rejects, or manually reviews the update under its own policy.
8. Downstream systems apply the approved version after their approval path completes.

Parva should not silently update production databases without operator approval.

## Event Types

- `calendar.official_release.verified`
- `calendar.release.diff_available`
- `calendar.risk_label.changed`
- `calendar.schedule.review_required`
- `calendar.future_assumption.resolved`

## Synthetic Event Example

```json
{
  "event": "calendar.schedule.review_required",
  "release_version": "public-example-001",
  "affected_years": [9000],
  "affected_months": ["9000-01"],
  "requires_review": true,
  "diff_available": true,
  "publication_status": "computed_prediction_not_official",
  "signature": "example-signature-placeholder"
}
```

The example is synthetic and does not contain real future month values.

## Claim Boundary

Official publication overrides computed output. Future-BS research outputs remain:

```text
computed_prediction_not_official
```
