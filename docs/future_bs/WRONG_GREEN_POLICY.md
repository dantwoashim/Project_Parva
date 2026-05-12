# Wrong-GREEN Policy

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

## What GREEN Means

GREEN means low risk under current checks and source policy. It does not mean official publication. It does not guarantee future behavior. It does not override a later official release.

## What Happens After a Wrong GREEN

If a wrong GREEN is discovered, the affected case should be moved out of GREEN, the reason code memory should be updated, and comparable boundary cases should be reviewed before any broader claim is made.
