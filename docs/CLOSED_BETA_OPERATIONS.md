# Closed Beta Operations

Use this guide when running Parva with real beta users before a wider public
announcement.

## Intake Channels

- Route all user-visible issues through one shared triage queue.
- Attach request IDs, screenshots, place/date inputs, and the route where the
  issue occurred.
- Treat provenance or trust-language mismatches as product incidents, not only
  UI bugs.

## Support Taxonomy

- `calendar-trust`: wrong date, missing observance, incorrect sacred-time claim.
- `personal-context`: wrong place/timezone behavior, personal sunrise drift,
  degraded-state confusion.
- `frontend-regression`: broken navigation, rendering, dialog, accessibility,
  mobile shell, or save-state behavior.
- `integration`: calendar feed, embed, webhook, or export behavior.
- `operations`: release packaging, provenance, signing, deployment, or artifact
  drift.

## Severity Levels

- `sev-1`: wrong sacred-time answer on a launch-critical surface, broken public
  home route, or invalid provenance/signing evidence.
- `sev-2`: degraded or unavailable launch-critical surface with a fallback path.
- `sev-3`: support/beta route defect, content issue, or non-blocking UI
  regression.

## Triage Workflow

1. Confirm the route, date, place, and request reference.
2. Check `docs/public_beta/dashboard_metrics.md` and `/api/reliability/status`
   for correlated reliability or degraded-mode signals.
3. Reproduce with the built app and capture the affected journey in
   `output/playwright/`.
4. Classify the issue using the support taxonomy above and assign severity.
5. Escalate `sev-1` and provenance issues immediately; do not wait for the next
   beta batch.

## Escalation Triggers

- Pause rollout if signed provenance, contract freeze, golden journeys, or
  bundle budget gates fail.
- Roll back when the degraded rate rises unexpectedly on launch-critical routes
  or when a sacred-time answer is materially wrong for a confirmed user input.
- Record every accepted risk or temporary workaround in
  `docs/public_beta/release_candidate_dossier.md`.

## Required Artifacts Per Beta Cut

- `reports/release/browser_smoke.json`
- `reports/release/golden_journeys.json`
- `reports/release/frontend_bundle_budget.json`
- `reports/security_audit.json`
- `docs/public_beta/release_candidate_dossier.md`
- `docs/LAUNCH_SIGNOFF.md`
