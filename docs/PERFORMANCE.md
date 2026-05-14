---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Performance Notes

Project Parva keeps public route checks fast enough for release verification, but some calendar surfaces still have different cold and warm behavior.

## Festival Upcoming Route

`/v3/api/festivals/upcoming?days=30` resolves a festival window from rule metadata, calendar conversions, and source notes. The first in-process call currently warms the festival occurrence cache. On the Windows verification machine used for this hardening pass, the observed timing was:

| Case | Local in-process timing |
|---|---:|
| Cold first call | about 1.33 seconds |
| Warm cached call | about 3 milliseconds |

The current regression test enforces warm-cache latency under 300 ms:

```bash
python -m pytest tests/performance/test_festival_upcoming_cache.py -q
```

The public Render blueprint enables `PARVA_PREWARM_HOTSET=true`, and startup prewarming now warms the same upcoming-festival cache path used by the public route. The remaining optimization target is moving that warmup into a release-artifact job or startup task with observable timing by environment, while keeping the public API response source-aware and non-authoritative.
