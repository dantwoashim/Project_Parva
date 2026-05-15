# Heavy Compute Audit

Generated artifact from the focused execution sprint.

Refresh commands:

```bash
rg "async def" backend/app/api backend/app/routes
rg "swisseph|kundali|muhurta|panchanga|ephemeris|future_bs|impact|timegraph" backend/app
```

Acceptance posture:

- public routes should use precomputed artifacts, bounded inputs, offload,
  cache, queues, or explicit timeouts for heavy computation,
- missing generated artifacts should return clear errors naming the generation
  command,
- exact Future-BS research compute stays behind private gates,
- no route should perform unbounded public compute by default.
