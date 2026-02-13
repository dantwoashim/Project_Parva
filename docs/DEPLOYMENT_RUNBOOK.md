# Deployment Runbook (Year 1)

## Goal
Ship v2.1 consistently and verify live behavior matches local benchmarked behavior.

## Pre-deploy gate

Run from repo root:

```bash
./scripts/year1_closure.sh
```

Required outcomes:
- Test suite passes
- v2 smoke passes
- Benchmark pass rate meets gate
- Frontend build succeeds

## Deploy targets (0-budget)

- Backend: Render/Railway/Fly free-tier
- Frontend: Vercel/Netlify free-tier

## Post-deploy verification

```bash
python3 scripts/live_smoke.py --base https://<your-backend-domain>
```

Checks include:
- `/v2/api/calendar/today`
- `/v2/api/calendar/convert`
- `/v2/api/festivals/dashain`
- `/v2/api/festivals/dashain/explain`
- `/v2/api/provenance/root`

## Rollback trigger

Rollback if any of these fail:
- non-200 on smoke endpoints
- benchmark gate regression
- broken provenance metadata in date responses

## Artifacts to publish with release

- `docs/NEPAL_GOLD_TECHNICAL_REPORT.md`
- `docs/VERIFICATION_DOSSIER_2027.md`
- `docs/RELEASE_NOTES_V2_1_GOLD.md`
- `reports/year1_closure/summary.md`
