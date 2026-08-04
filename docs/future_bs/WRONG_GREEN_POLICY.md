---
status: research
tier: 3
lane: research
last_verified: 2026-05-14
owner: research-team
---

# Future BS Wrong-GREEN Policy

Status: governance policy.

GREEN is the strongest public risk posture. It must be used conservatively.

Every future-BS result remains:

```text
computed_prediction_not_official
```

## Principle

A wrong GREEN is more serious than an ordinary error because it tells a user that a case is low risk when it should have been reviewed.

The safety target is:

```text
wrong_green_count = 0
```

## Operating Policy

- Do not expand GREEN coverage at the cost of safety.
- Prefer YELLOW when evidence, source policy, or boundary behavior is uncertain.
- Use RED when a case is invalid, source-conflicted, non-claimable, or operationally unsafe.
- Treat official publication and reviewed authoritative evidence as stronger than computed output.
- Do not allow third-party shadow data to support official-grade claims.
- Do not use broad all-reference or weak-source stress tests to tune official GREEN thresholds.
- A public GREEN label indicates lower model risk only. Every public forecast
  still carries `review_required=true` and the computed-research publication status.

## What GREEN Means

GREEN means low risk under current checks and source policy. It does not mean official publication. It does not guarantee future behavior. It does not override a later official release.

## Required Metrics

Every GREEN-related report must include:

- `wrong_green_count`
- `wrong_high_confidence_count`
- `false_confidence_rate`
- high-confidence coverage
- source policy
- official or reviewed evidence window
- excluded source tiers
- residual summary

## What Happens After a Wrong GREEN

If a wrong GREEN is discovered, the affected case should be moved out of GREEN, the reason code memory should be updated, and comparable boundary cases should be reviewed before any broader claim is made.

The next public release must document the correction and re-run:

```bash
python scripts/check_future_bs_public_leakage.py
pytest -q -m "not private_source and not wide_corpus and not research_artifact" tests/future_bs tests/accuracy tests/artifacts tests/performance --maxfail=20
```
