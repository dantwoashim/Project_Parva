# Year 1 Retrospective

## What Worked

- Unified V2 calculation path removed major date drift between endpoints.
- Contract-first API iteration (`/v2/api/*`) improved frontend-backend stability.
- Evaluation automation + discrepancy triage made quality measurable and repeatable.
- Explainability endpoint improved evaluator and user trust.

## What Was Hard

- Keeping legacy compatibility while evolving response schemas.
- Managing multiple source formats (PDF OCR, normalized tables, rules JSON).
- Ensuring every UX path handled empty/loading/error states cleanly.

## Key Improvements Delivered

- v2 deprecation headers on legacy routes.
- Frontend schema audit and fixes.
- Provenance snapshot hashing + Merkle proof endpoints.
- Benchmark package with one-command rerun.

## Risks Remaining

- Out-of-range calendar conversion still depends on estimated mode confidence.
- Regional variation logic needs richer rule modeling.
- Free-tier deployment limits can affect tail latency during peak periods.

## Year 2 Adjustments

1. Expand rule coverage and regional observance variants.
2. Add stronger differential testing against multiple public references.
3. Improve provenance UX (human-readable verify UI, not just API).
4. Build partner-ready SDK examples for adoption.

## Final Note

Year 1 successfully established a reproducible, verifiable technical baseline. Year 2 should focus on breadth (coverage) without sacrificing the correctness guarantees achieved here.
