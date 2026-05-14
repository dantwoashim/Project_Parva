---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Confidence Model

Future-BS confidence is not a single magic score. It is assembled from model agreement, future horizon, source quality, civil-boundary risk, and known residual behavior.

## Labels

- `official_verified`: structured corpus year with official verification.
- `computed_very_high`: strong model agreement and high confidence.
- `computed_high`: good model agreement with manageable uncertainty.
- `computed_medium`: useful but reviewable.
- `computed_low`: weak enough to require review before serious use.
- `needs_review`: insufficient confidence for unsupervised use.

## Inputs

The current confidence model considers:

- agreement between computational and legacy fallback models
- probability distribution across 29/30/31/32 day outcomes
- distance from civil assignment boundary
- future horizon beyond the static corpus
- source quality for known rows
- backtest and residual behavior

## Risk Flags

Common flags:

- `outside_static_lookup`
- `long_horizon`
- `model_disagreement`
- `manual_review_recommended`
- `historically_sensitive_month`
- `sankranti_near_civil_assignment_boundary`

When `manual_review_recommended` is present, do not use the month directly in long-term financial contracts without review.
