---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# No-Break Calendar Policy

Financial systems should not hardcode unpublished future BS month lengths as final truth.

Recommended states:

- `computed_provisional`
- `internally_approved`
- `official_published`
- `reconciled`
- `superseded`

Every future schedule should store:

- `calendar_run_id`
- `calendar_version`
- `publication_status`
- `confidence_label`
- `prediction_set`
- `reconciliation_required`
- `override_policy`
- `generated_at`

Yellow and red months should use override-ready or dual-schedule workflows until official publication.
