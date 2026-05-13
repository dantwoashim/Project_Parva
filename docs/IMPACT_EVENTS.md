# Impact Events

Layer 8 defines event payload shapes but does not deliver production webhooks.

Preview event types include:

- `temporal.release.diff.created`
- `temporal.impact.detected`
- `temporal.evidence.stale`
- `temporal.rule.review_required`
- `temporal.feed.regeneration_required`
- `temporal.conflict.discovered`
- `temporal.conflict.resolved`

Preview events use `unsigned_preview` unless a private deployment adds signing.
