---
status: research
audience: astronomical-computation
---

# JPL DE440 Integration

JPL DE440 is a deterministic astronomical truth tower for research and
cross-checking. It is not a public official BS prediction engine.

## Role

JPL can improve:

- apparent solar longitude,
- lunar longitude,
- tithi boundary sensitivity,
- nakshatra, yoga, and karana sensitivity,
- panchanga-at-sunrise comparisons,
- solar ingress root solving,
- festival boundary sensitivity,
- Future-BS astronomy candidate generation.

JPL cannot replace:

- official Panchanga authority,
- civil calendar committee decisions,
- MoHA holiday decisions,
- fiscal, working-day, payroll, tax, or banking rules,
- published source authority.

## Pipeline

```text
DE440 or DE441 SPK kernel
-> apparent solar and lunar longitude
-> sidereal longitude with ayanamsha
-> solar ingress root solving
-> Nepal civil date conversion
-> ayanamsha sensitivity
-> sunrise, refraction, and location sensitivity
-> JPL vs Swiss vs Horizons differential report
-> boundary-risk label
```

## Runtime Boundary

Public verification does not require JPL kernels. If no kernel is configured,
the JPL adapter reports unavailable and public routes continue to use the safe
public fallback.

If a kernel is configured, operators must run:

```bash
python scripts/ephemeris/verify_kernel_hashes.py
```

Only relative policy ids and hash status should appear in public reports. Local
operator paths remain private.
